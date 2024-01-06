import os

import yaml
from pytest_helpers import hydrate_job_definition

from dbt_cloud_jobs.dbt_cloud_helpers import (
    create_dbt_cloud_job,
    delete_dbt_cloud_job,
    list_dbt_cloud_jobs,
)


def test_create_dbt_cloud_job() -> None:
    with open("./tests/fixtures/valid/simple_job.yml") as f:
        definitions = yaml.safe_load(f)

    create_dbt_cloud_job(definition=hydrate_job_definition(definition=definitions["jobs"][0]))
    assert definitions["jobs"][0]["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(os.getenv("DBT_ACCOUNT_ID"))
    ]


def test_delete_dbt_cloud_job() -> None:
    with open("./tests/fixtures/valid/job_with_multiple_steps.yml") as f:
        definitions = yaml.safe_load(f)

    job_name = definitions["jobs"][0]["name"]

    job_id = create_dbt_cloud_job(
        definition=hydrate_job_definition(definition=definitions["jobs"][0])
    )
    assert job_name in [x["name"] for x in list_dbt_cloud_jobs(os.getenv("DBT_ACCOUNT_ID"))]

    list_dbt_cloud_jobs.cache_clear()
    existing_jobs = list_dbt_cloud_jobs(os.getenv("DBT_ACCOUNT_ID"))
    delete_dbt_cloud_job(
        definition=hydrate_job_definition(
            definition=[x for x in existing_jobs if x["id"] == job_id][0]
        )
    )

    list_dbt_cloud_jobs.cache_clear()
    assert job_id not in [x["id"] for x in list_dbt_cloud_jobs(os.getenv("DBT_ACCOUNT_ID"))]


def test_list_dbt_cloud_jobs() -> None:
    existing_jobs = list_dbt_cloud_jobs(os.getenv("DBT_ACCOUNT_ID"))
    assert isinstance(existing_jobs, list)