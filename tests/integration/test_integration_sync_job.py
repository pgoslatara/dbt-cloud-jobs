from dbt_cloud_jobs.dbt_api_helpers import create_dbt_cloud_job
from dbt_cloud_jobs.sync_job import sync_dbt_cloud_job
from tests.pytest_helpers import hydrate_job_definition


def test_sync_dbt_cloud_job_new_job(caplog, file_job_minimal_definition) -> None:
    definitions = file_job_minimal_definition

    definition = hydrate_job_definition(definitions["jobs"][0])
    sync_dbt_cloud_job(definition=definition)

    assert f"Job `{definition['name']}` does not exist, creating..." in caplog.text


def test_sync_dbt_cloud_job_no_update(caplog, file_job_minimal_definition) -> None:
    definitions = file_job_minimal_definition

    definition = hydrate_job_definition(definitions["jobs"][0])
    create_dbt_cloud_job(definition=definition)
    sync_dbt_cloud_job(definition=definition)

    assert f"Job `{definition['name']}` already exists, updating..." in caplog.text
    assert (
        f"Definition of job `{definition['name']}` (id: {definition['id']}) has not changed, will not be updated."
        in caplog.text
    )


def test_sync_dbt_cloud_job_update(caplog, file_job_minimal_definition) -> None:
    definitions = file_job_minimal_definition

    definition = hydrate_job_definition(definitions["jobs"][0])
    create_dbt_cloud_job(definition=definition)

    # Force update
    definition["settings"]["threads"] = 4

    sync_dbt_cloud_job(definition=definition)

    assert f"Job `{definition['name']}` already exists, updating..." in caplog.text
    assert (
        f"Updated dbt Cloud job, URL: https://cloud.getdbt.com/deploy/{definition['account_id']}/projects/{definition['project_id']}/jobs/{definition['id']}"
        in caplog.text
    )
