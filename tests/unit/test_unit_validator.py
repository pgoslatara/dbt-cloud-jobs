from pathlib import Path

import pytest

from dbt_cloud_jobs.logger import logger
from dbt_cloud_jobs.validator import validate_job_definition_file


@pytest.mark.parametrize("file_name", Path("./tests/fixtures/invalid/").glob(pattern="*"), ids=str)
def test_validator_invalid_ymls(file_name) -> None:
    logger.info(f"{file_name=}")
    with pytest.raises(Exception) as e:
        validate_job_definition_file(file=file_name)


@pytest.mark.parametrize("file_name", Path("./tests/fixtures/valid/").glob(pattern="*"), ids=str)
def test_validator_valid_ymls(file_name) -> None:
    try:
        validate_job_definition_file(file=file_name)
    except:
        logger.warning(f"{file_name=}")
        pytest.fail()
