from argparse import Namespace
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
import yaml

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
        main(Namespace(account_id=123, file=file.name, import_=True, sync=True))

    assert str(e.value) == "Only one of `--import` and `--sync` can be specified."


def test_main_args_import_to_existing_file():
    file = NamedTemporaryFile()
    logger.info("Calling main() with account_id=None and import=True...")
    with pytest.raises(FileExistsError) as e:
        main(Namespace(account_id=123, file=file.name, import_=True))

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
        main(Namespace(account_id=None, file=file.name, import_=True))

    assert str(e.value) == "`--account_id` must be passed when `--import` is passed."


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

    assert str(e.value) == "Only one of `--sync` and `--validate` can be specified."


def test_main_duplicate_job_names():
    with pytest.raises(DbtCloudJobsDuplicateJobNameError):
        main(Namespace(file="./tests/fixtures/invalid/duplicate_job_names.yml", sync=True))


def test_main_file_not_exists():
    with pytest.raises(FileNotFoundError):
        main(Namespace(file="file_that_does_not_exist.yml", sync=True))
