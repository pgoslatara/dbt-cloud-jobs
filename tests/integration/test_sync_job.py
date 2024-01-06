from pathlib import Path

import yaml
from pytest_helpers import hydrate_job_definition

from dbt_cloud_jobs.dbt_cloud_helpers import create_dbt_cloud_job
from dbt_cloud_jobs.sync_job import sync_dbt_cloud_job


def test_sync_dbt_cloud_job_new_job(caplog) -> None:
    with Path.open(Path("./tests/fixtures/valid/simple_job.yml"), "r") as f:
        definitions = yaml.safe_load(f)

    definition = hydrate_job_definition(definitions["jobs"][0])
    sync_dbt_cloud_job(definition=definition)

    assert f"Job `{definition['name']}` does not exist, creating..." in caplog.text


def test_sync_dbt_cloud_job_no_update(caplog) -> None:
    with Path.open(Path("./tests/fixtures/valid/simple_job.yml"), "r") as f:
        definitions = yaml.safe_load(f)

    definition = hydrate_job_definition(definitions["jobs"][0])
    create_dbt_cloud_job(definition=definition)
    sync_dbt_cloud_job(definition=definition)

    assert f"Job `{definition['name']}` already exists, updating..." in caplog.text
    assert (
        f"Definition of job `{definition['name']}` (id: {definition['id']}) has not changed, will not be updated."
        in caplog.text
    )


def test_sync_dbt_cloud_job_update(caplog) -> None:
    with Path.open(Path("./tests/fixtures/valid/simple_job.yml"), "r") as f:
        definitions = yaml.safe_load(f)

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
