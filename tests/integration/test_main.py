import os
from argparse import Namespace
from pathlib import Path
from tempfile import NamedTemporaryFile

import yaml
from pytest_helpers import hydrate_job_definition

from dbt_cloud_jobs.dbt_api_helpers import list_dbt_cloud_jobs
from dbt_cloud_jobs.logger import logger
from dbt_cloud_jobs.main import main


def test_main_import_true(request, tmp_path):
    file = Path(tmp_path / f"{request.node.name}.yml")
    assert file.exists() is False

    logger.info("Calling main() with import=True...")
    main(Namespace(account_id=os.getenv("DBT_ACCOUNT_ID"), file=file, import_=True))

    assert file.exists()

    with Path.open(file, "r") as f:
        definitions = yaml.safe_load(f)

    assert isinstance(definitions["jobs"], list)


def test_main_sync_false(caplog, file_simple_job_yml):
    definitions = file_simple_job_yml

    definition = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.safe_dump({"jobs": [definition]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    logger.info("Calling main() with sync=False...")
    main(Namespace(file=file.name, sync=False))

    assert definition["name"] not in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition["account_id"])
    ]
    assert f"Pass `--sync` to sync the jobs defined in `{file.name}` to dbt Cloud." in caplog.text


def test_main_sync_remove_job_allow_deletes_false(caplog, file_simple_job_yml):
    definitions = file_simple_job_yml

    definition_1 = hydrate_job_definition(definitions["jobs"][0])
    definition_2 = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.safe_dump({"jobs": [definition_1, definition_2]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    logger.info("Calling main() with allow_deletes=False, expecting 2 jobs to be created...")
    main(Namespace(allow_deletes=False, file=file.name, sync=True))

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
    file.write(bytes(yaml.safe_dump({"jobs": [definition_1]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    logger.info(
        "Calling main() with allow_deletes=False, expecting 1 job to be unchanged and 1 job to be listed for deletion..."
    )
    main(Namespace(allow_deletes=False, file=file.name, sync=True))

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


def test_main_sync_remove_job_allow_deletes_true(caplog, file_simple_job_yml):
    definitions = file_simple_job_yml

    definition_1 = hydrate_job_definition(definitions["jobs"][0])
    definition_2 = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.safe_dump({"jobs": [definition_1, definition_2]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    logger.info("Calling main() with allow_deletes=False, expecting 2 jobs to be created...")
    main(Namespace(allow_deletes=False, file=file.name, sync=True))

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
    file.write(bytes(yaml.safe_dump({"jobs": [definition_1]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    logger.info(
        "Calling main() with allow_deletes=True, expecting 1 job to be unchanged and 1 job to be listed for deletion..."
    )
    main(Namespace(allow_deletes=True, file=file.name, sync=True))

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


def test_main_sync_simple_job(caplog, file_simple_job_yml):
    definitions = file_simple_job_yml

    definition = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.safe_dump({"jobs": [definition]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    logger.info("Calling main() with allow_deletes=False, expecting 1 job to be created...")
    main(Namespace(allow_deletes=False, file=file.name, sync=True))

    assert definition["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition["account_id"])
    ]
    assert f"Using definitions files: {file.name}" in caplog.text
    assert f"Found definitions for 1 job(s)." in caplog.text


def test_main_sync_true(file_simple_job_yml):
    definitions = file_simple_job_yml

    definition = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.safe_dump({"jobs": [definition]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    logger.info("Calling main() with sync=True...")
    main(Namespace(file=file.name, sync=True))

    assert definition["name"] in [
        x["name"] for x in list_dbt_cloud_jobs(account_id=definition["account_id"])
    ]
