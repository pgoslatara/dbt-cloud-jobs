import logging
from argparse import Namespace
from pathlib import Path

import pytest
from conftest import catch_logs, records_to_tuples

from dbt_cloud_jobs.logger import logger
from dbt_cloud_jobs.main import main


def test_logger_debug(file_definition_valid: Path) -> None:
    with catch_logs(level=logging.DEBUG, logger=logger) as handler:
        with pytest.raises(RuntimeError) as e:
            main(Namespace(file=file_definition_valid))

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


def test_logger_info(caplog, file_definition_valid: Path) -> None:
    caplog.set_level(logging.INFO)
    with pytest.raises(RuntimeError) as e:
        main(Namespace(file=file_definition_valid))

    assert "Running dbt_cloud_jobs..." in caplog.text
