from argparse import Namespace

import pytest

from dbt_cloud_jobs.exceptions import DuplicateJobNameError
from dbt_cloud_jobs.main import main


def test_main_duplicate_job_names():
    with pytest.raises(DuplicateJobNameError):
        main(Namespace(file="./tests/fixtures/invalid/duplicate_job_names.yml"))


def test_main_file_not_exists():
    with pytest.raises(FileNotFoundError):
        main(Namespace(file="file_that_does_not_exist.yml"))
