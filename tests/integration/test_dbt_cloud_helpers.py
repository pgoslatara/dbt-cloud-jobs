import os
from pathlib import Path

import yaml
from pytest_helpers import hydrate_job_definition

from dbt_cloud_jobs.dbt_cloud_helpers import (
    create_dbt_cloud_job,
    delete_dbt_cloud_job,
    list_dbt_cloud_jobs,
)


def test_create_dbt_cloud_job() -> None:
    with Path.open(Path("./tests/fixtures/valid/simple_job.yml"), "r") as f:
        definitions = yaml.safe_load(f)

    create_dbt_cloud_job(definition=hydrate_job_definition(definition=definitions["jobs"][0]))
    assert definitions["jobs"][0]["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(os.getenv("DBT_ACCOUNT_ID"))
    ]


def test_delete_dbt_cloud_job() -> None:
    with Path.open(Path("./tests/fixtures/valid/job_with_multiple_steps.yml"), "r") as f:
        definitions = yaml.safe_load(f)

    job_id = create_dbt_cloud_job(
        definition=hydrate_job_definition(definition=definitions["jobs"][0])
    )
    assert definitions["jobs"][0]["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(os.getenv("DBT_ACCOUNT_ID"))
    ]

    existing_jobs = list_dbt_cloud_jobs(os.getenv("DBT_ACCOUNT_ID"))
    delete_dbt_cloud_job(
        definition=hydrate_job_definition(
            definition=[x for x in existing_jobs if x["id"] == job_id][0]
        )
    )

    assert job_id not in [x["id"] for x in list_dbt_cloud_jobs(os.getenv("DBT_ACCOUNT_ID"))]


def test_list_dbt_cloud_jobs() -> None:
    existing_jobs = list_dbt_cloud_jobs(os.getenv("DBT_ACCOUNT_ID"))
    assert isinstance(existing_jobs, list)
