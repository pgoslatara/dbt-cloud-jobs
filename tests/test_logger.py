import logging
import sys
from contextlib import contextmanager
from typing import List, Tuple

import pytest
from _pytest.logging import LogCaptureHandler

from dbt_cloud_jobs.logger import logger
from dbt_cloud_jobs.main import main


# Source: https://github.com/pytest-dev/pytest/issues/3697#issuecomment-792129636
@contextmanager
def catch_logs(level: int, logger: logging.Logger) -> LogCaptureHandler:
    """Context manager that sets the level for capturing of logs.

    After the end of the 'with' statement the level is restored to its original value.

    :param level: The level.
    :param logger: The logger to update.
    """
    handler = LogCaptureHandler()
    orig_level = logger.level
    logger.setLevel(level)
    logger.addHandler(handler)
    try:
        yield handler
    finally:
        logger.setLevel(orig_level)
        logger.removeHandler(handler)


def records_to_tuples(records: List[logging.LogRecord]) -> List[Tuple[str, int, str]]:
    """A list of a stripped down log records intended for use in assertion comparison.

    :param records: A list of LogRecord objects.
    :returns: A list of tuples, where each tuple has the format (logger_name, log_level, message)
    """
    return [(r.name, r.levelno, r.getMessage()) for r in records]


def test_logger_debug() -> None:
    with catch_logs(level=logging.DEBUG, logger=logger) as handler:
        with pytest.raises(RuntimeError) as e:
            sys.argv[1:] = ["--dbt-account-id", "123"]
            main()

        assert (
            len(
                [
                    record
                    for record in records_to_tuples(handler.records)
                    if record[2].startswith("job_definitions=")
                ]
            )
            == 1
        )


def test_logger_info(caplog) -> None:
    caplog.set_level(logging.INFO)
    with pytest.raises(RuntimeError) as e:
        sys.argv[1:] = ["--dbt-account-id", "123"]
        main()
    assert "Running dbt_cloud_jobs..." in caplog.text
