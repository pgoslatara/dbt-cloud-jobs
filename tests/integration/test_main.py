from argparse import Namespace
from pathlib import Path
from tempfile import NamedTemporaryFile

import yaml
from pytest_helpers import hydrate_job_definition

from dbt_cloud_jobs.dbt_cloud_helpers import list_dbt_cloud_jobs
from dbt_cloud_jobs.main import main


def test_main_remove_job_allow_deletes_false(caplog):
    with Path.open(Path("./tests/fixtures/valid/simple_job.yml"), "r") as file:
        definitions = yaml.safe_load(file)

    definition_1 = hydrate_job_definition(definitions["jobs"][0])
    definition_2 = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.dump({"jobs": [definition_1, definition_2]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    main(Namespace(allow_deletes=False, file=file.name))

    assert definition_1["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition_1["account_id"])
    ]
    assert definition_2["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition_2["account_id"])
    ]
    assert f"Using definitions files: {file.name}" in caplog.text
    assert f"Found definitions for 2 job(s)." in caplog.text

    # Remove job from YML and call main() again
    definition_2_job_id = [
        x["id"]
        for x in list_dbt_cloud_jobs(account_id=definition_2["account_id"])
        if x["name"] == definition_2["name"]
    ][0]
    file = NamedTemporaryFile()
    file.write(bytes(yaml.dump({"jobs": [definition_1]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    main(Namespace(allow_deletes=False, file=file.name))

    assert definition_1["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition_1["account_id"])
    ]
    assert definition_2["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition_2["account_id"])
    ]
    assert f"Using definitions files: {file.name}" in caplog.text
    assert f"Found definitions for 1 job(s)." in caplog.text
    assert definition_1["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition_1["account_id"])
    ]
    assert definition_2["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition_2["account_id"])
    ]
    assert (
        f"Job `{definition_2['name']}` (id: {definition_2_job_id}) exists in dbt Cloud but not in `{file.name}`. Pass `--allow-deletes` to delete this job from dbt Cloud."
        in caplog.text
    )


def test_main_remove_job_allow_deletes_false(caplog):
    with Path.open(Path("./tests/fixtures/valid/simple_job.yml"), "r") as file:
        definitions = yaml.safe_load(file)

    definition_1 = hydrate_job_definition(definitions["jobs"][0])
    definition_2 = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.dump({"jobs": [definition_1, definition_2]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    main(Namespace(allow_deletes=False, file=file.name))

    assert definition_1["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition_1["account_id"])
    ]
    assert definition_2["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition_2["account_id"])
    ]
    assert f"Using definitions files: {file.name}" in caplog.text
    assert f"Found definitions for 2 job(s)." in caplog.text

    # Remove job from YML and call main() again
    definition_2_job_id = [
        x["id"]
        for x in list_dbt_cloud_jobs(account_id=definition_2["account_id"])
        if x["name"] == definition_2["name"]
    ][0]
    file = NamedTemporaryFile()
    file.write(bytes(yaml.dump({"jobs": [definition_1]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    main(Namespace(allow_deletes=True, file=file.name))

    assert definition_1["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition_1["account_id"])
    ]
    assert definition_2["name"] not in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition_2["account_id"])
    ]
    assert f"Using definitions files: {file.name}" in caplog.text
    assert f"Found definitions for 1 job(s)." in caplog.text
    assert (
        f"Deleted dbt Cloud job `{definition_2['name']}` (id: {definition_2_job_id}), URL: https://cloud.getdbt.com/deploy/{definition_2['account_id']}/projects/{definition_2['project_id']}/jobs/{definition_2_job_id}"
        in caplog.text
    )


def test_main_simple_job(caplog):
    with Path.open(Path("./tests/fixtures/valid/simple_job.yml"), "r") as file:
        definitions = yaml.safe_load(file)

    definition = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.dump({"jobs": [definition]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    main(Namespace(allow_deletes=False, file=file.name))

    assert definition["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition["account_id"])
    ]
    assert f"Using definitions files: {file.name}" in caplog.text
    assert f"Found definitions for 1 job(s)." in caplog.text
