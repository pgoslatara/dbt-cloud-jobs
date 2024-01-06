import logging
import os
import sys
from contextlib import contextmanager
from functools import lru_cache
from random import random
from typing import List, Tuple

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


def hydrate_job_definition(definition: dict) -> dict:  # TODO: pydantic class
    definition["account_id"] = int(os.getenv("DBT_ACCOUNT_ID"))
    definition["environment_id"] = int(os.getenv("DBT_ENVIRONMENT_ID"))
    definition["name"] = f"{job_prefix()}_{definition['name']}_{int(random() * 1000000)}"
    definition["project_id"] = int(os.getenv("DBT_PROJECT_ID"))
    return definition


@lru_cache
def job_prefix():
    return f"dbt_cloud_jobs_ci_{sys.version_info[0]}_{sys.version_info[1]}_{sys.version_info[2]}"


def records_to_tuples(records: List[logging.LogRecord]) -> List[Tuple[str, int, str]]:
    """A list of a stripped down log records intended for use in assertion comparison.

    :param records: A list of LogRecord objects.
    :returns: A list of tuples, where each tuple has the format (logger_name, log_level, message)
    """
    return [(r.name, r.levelno, r.getMessage()) for r in records]
