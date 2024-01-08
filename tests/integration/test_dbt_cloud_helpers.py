import os

from pytest_helpers import hydrate_job_definition

from dbt_cloud_jobs.dbt_api_helpers import (
    create_dbt_cloud_job,
    delete_dbt_cloud_job,
    list_dbt_cloud_jobs,
)


def test_create_dbt_cloud_job(file_simple_job_yml) -> None:
    definitions = file_simple_job_yml

    definition = hydrate_job_definition(definition=definitions["jobs"][0])
    create_dbt_cloud_job(definition=definition)
    assert definition["name"] in [x["name"] for x in list_dbt_cloud_jobs(definition["account_id"])]


def test_delete_dbt_cloud_job(file_simple_job_yml) -> None:
    definitions = file_simple_job_yml

    definition = hydrate_job_definition(definition=definitions["jobs"][0])
    job_id = create_dbt_cloud_job(definition=definition)
    assert definition["name"] in [x["name"] for x in list_dbt_cloud_jobs(definition["account_id"])]

    existing_jobs = list_dbt_cloud_jobs(definition["account_id"])
    delete_dbt_cloud_job(
        definition=hydrate_job_definition(
            definition=[x for x in existing_jobs if x["id"] == job_id][0]
        )
    )

    assert job_id not in [x["id"] for x in list_dbt_cloud_jobs(definition["account_id"])]


def test_list_dbt_cloud_jobs() -> None:
    existing_jobs = list_dbt_cloud_jobs(os.getenv("DBT_ACCOUNT_ID"))
    assert isinstance(existing_jobs, list)
