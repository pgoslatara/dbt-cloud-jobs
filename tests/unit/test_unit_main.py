import os
from argparse import Namespace
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
import yaml
from pytest import MonkeyPatch

from dbt_cloud_jobs.dbt_api_helpers import get_dbt_cloud_api_base_url
from dbt_cloud_jobs.exceptions import (
    DbtCloudJobsDuplicateJobNameError,
    DbtCloudJobsInvalidArguments,
)
from dbt_cloud_jobs.logger import logger
from dbt_cloud_jobs.main import main
from tests.pytest_helpers import hydrate_job_definition


def test_main_args_import_and_sync_both_true(file_job_minimal_definition):
    definitions = file_job_minimal_definition

    definition = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.safe_dump({"jobs": [definition]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    logger.info("Calling main() with import=True and sync=True...")
    with pytest.raises(DbtCloudJobsInvalidArguments) as e:
        main(Namespace(account_id=123, file=file.name, import_=True, project_id=456, sync=True))

    assert str(e.value) == "Only one of `--import`, `--validate` and `--sync` can be specified."


def test_main_args_import_to_existing_file():
    file = NamedTemporaryFile()
    logger.info("Calling main() with account_id=None and import=True...")
    with pytest.raises(FileExistsError) as e:
        main(Namespace(account_id=123, file=file.name, import_=True, project_id=456))

    assert str(e.value) == f"{file.name} already exists, please choose a different file name."


def test_main_args_import_without_account_id(file_job_minimal_definition):
    definitions = file_job_minimal_definition

    definition = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.safe_dump({"jobs": [definition]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    logger.info("Calling main() with account_id=None and import=True...")
    with pytest.raises(DbtCloudJobsInvalidArguments) as e:
        main(Namespace(account_id=None, file=file.name, import_=True, project_id=456))

    assert (
        str(e.value)
        == "`--account-id` and `--project-id` must be passed when `--import` is passed."
    )


def test_main_args_import_without_project_id(file_job_minimal_definition):
    definitions = file_job_minimal_definition

    definition = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.safe_dump({"jobs": [definition]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    logger.info("Calling main() with project_id=None and import=True...")
    with pytest.raises(DbtCloudJobsInvalidArguments) as e:
        main(Namespace(account_id=123, file=file.name, import_=True, project_id=None))

    assert (
        str(e.value)
        == "`--account-id` and `--project-id` must be passed when `--import` is passed."
    )


def test_main_args_none(file_job_minimal_definition):
    definitions = file_job_minimal_definition

    definition = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.safe_dump({"jobs": [definition]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    logger.info("Calling main() with ano args...")
    with pytest.raises(DbtCloudJobsInvalidArguments) as e:
        main(Namespace())

    assert str(e.value) == "One of `--import`, `--validate` and `--sync` must be specified."


def test_main_args_sync_and_validate_both_true(file_job_minimal_definition):
    definitions = file_job_minimal_definition

    definition = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.safe_dump({"jobs": [definition]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    logger.info("Calling main() with sync=True and validate=True...")
    with pytest.raises(DbtCloudJobsInvalidArguments) as e:
        main(Namespace(file=file.name, sync=True, validate=True))

    assert str(e.value) == "Only one of `--import`, `--validate` and `--sync` can be specified."


@pytest.mark.parametrize("dbt_cloud_region", (None, "", 2, "EU", "us"))
def test_main_dbt_cloud_region_not_set_errors(
    dbt_cloud_region: str, file_job_minimal_definition
) -> None:
    if os.getenv("DBT_CLOUD_REGION") not in ["AU", "Europe", "US"]:
        raise RuntimeError("The env var `DBT_CLOUD_REGION` must be one of: US, Europe, AU")

    with MonkeyPatch.context() as mp:
        mp.setenv("DBT_CLOUD_REGION", dbt_cloud_region)
        definitions = file_job_minimal_definition

        definition = hydrate_job_definition(definitions["jobs"][0])
        file = NamedTemporaryFile()
        file.write(bytes(yaml.safe_dump({"jobs": [definition]}), encoding="utf-8"))
        file.seek(0)
        with Path.open(Path(file.name), "r") as f:
            definitions = yaml.safe_load(f)

        logger.info("Calling main() with validate=True...")
        with pytest.raises(RuntimeError) as e:
            get_dbt_cloud_api_base_url.cache_clear()
            main(Namespace(file=file.name, validate=True))

        assert str(e.value) == "The env var `DBT_CLOUD_REGION` must be one of: US, Europe, AU"


def test_main_duplicate_job_names():
    with pytest.raises(DbtCloudJobsDuplicateJobNameError):
        main(Namespace(file="./tests/fixtures/invalid/duplicate_job_names.yml", sync=True))


def test_main_file_not_exists():
    with pytest.raises(FileNotFoundError):
        main(Namespace(file="file_that_does_not_exist.yml", sync=True))
