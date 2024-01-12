from pathlib import Path

import pytest
import yaml

from dbt_cloud_jobs.logger import logger
from dbt_cloud_jobs.validator import validate_job_definition


@pytest.mark.parametrize("file_name", Path("./tests/fixtures/invalid/").glob(pattern="*"), ids=str)
def test_validator_invalid_ymls(file_name) -> None:
    logger.info(f"{file_name=}")
    if file_name.name not in ["duplicate_job_names.yml"]:
        with pytest.raises(Exception) as e:
            with Path.open(Path(file_name), "r") as f:
                definitions = yaml.safe_load(f)

            for definition in definitions["jobs"]:
                validate_job_definition(definition=definition)


@pytest.mark.parametrize("file_name", Path("./tests/fixtures/valid/").glob(pattern="*"), ids=str)
def test_validator_valid_ymls(file_name) -> None:
    try:
        with Path.open(Path(file_name), "r") as f:
            definitions = yaml.safe_load(f)

        for definition in definitions["jobs"]:
            validate_job_definition(definition=definition)
    except:
        logger.warning(f"{file_name=}")
        pytest.fail()
