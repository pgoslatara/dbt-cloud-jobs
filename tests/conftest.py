import logging
from contextlib import contextmanager
from pathlib import Path
from typing import List, Tuple

import pytest
import yaml
from _pytest.logging import LogCaptureHandler


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


@pytest.fixture(scope="function")
def file_definition_valid(tmp_path: Path) -> Path:
    file = tmp_path / "test_duplicate_job_names.yml"
    with open(file, "w") as f1:
        yaml.dump({"jobs": [{"name": "job1"}, {"name": "job2"}]}, f1)

    return file
