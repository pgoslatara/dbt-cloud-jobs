import os
from pathlib import Path

import pytest
import yaml
from pytest_helpers import job_prefix

from dbt_cloud_jobs.dbt_api_helpers import delete_dbt_cloud_job, list_dbt_cloud_jobs
from dbt_cloud_jobs.logger import logger


@pytest.fixture(scope="function")
def file_definition_valid(tmp_path: Path) -> Path:
    file = tmp_path / "test_duplicate_job_names.yml"
    with Path.open(Path(file), "w") as f1:
        yaml.safe_dump(
            {"jobs": [{"name": "job1", "account_id": 123}, {"name": "job2", "account_id": 123}]},
            f1,
        )

    return file


@pytest.fixture(scope="session")
def file_job_minimal_definition() -> dict:
    with Path.open(Path("./tests/fixtures/valid/job_with_minimal_definition.yml"), "r") as file:
        definitions = yaml.safe_load(file)

    return definitions


def pytest_sessionfinish(session, exitstatus):
    logger.info("Running cleanup after pytest...")
    for job in list_dbt_cloud_jobs(account_id=os.getenv("DBT_ACCOUNT_ID")):
        if job["name"].startswith(job_prefix()):
            delete_dbt_cloud_job(job)
