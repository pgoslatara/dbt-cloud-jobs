import os
from pathlib import Path

import pytest
import yaml

from dbt_cloud_jobs.dbt_api_helpers import delete_dbt_cloud_job, list_dbt_cloud_jobs
from dbt_cloud_jobs.logger import logger
from dbt_cloud_jobs.utils import job_prefix
from dbt_cloud_jobs.validator import DbtCloudJobDefinitionsFile


@pytest.fixture(scope="session")
def file_job_minimal_definition() -> DbtCloudJobDefinitionsFile:
    with Path.open(Path("./tests/fixtures/valid/job_with_minimal_definition.yml"), "r") as file:
        definitions = yaml.safe_load(file)

    return definitions


def pytest_sessionfinish(session, exitstatus):
    logger.info("Running cleanup after pytest...")
    for job in list_dbt_cloud_jobs(account_id=int(os.environ["DBT_ACCOUNT_ID"])):
        if job["name"].startswith(job_prefix()):
            delete_dbt_cloud_job(job)
