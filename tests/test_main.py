from argparse import Namespace
from pathlib import Path

import pytest
import yaml

from dbt_cloud_jobs.exceptions import DuplicateJobNameError
from dbt_cloud_jobs.main import main


def test_duplicate_job_names(tmp_path: Path):
    file = tmp_path / "test_duplicate_job_names.yml"
    with open(file, "w") as f1:
        yaml.dump({"jobs": [{"name": "job1"}, {"name": "job1"}]}, f1)

    with pytest.raises(DuplicateJobNameError):
        main(Namespace(file=file))


def test_file_not_exists():
    with pytest.raises(FileNotFoundError):
        main(Namespace(file="file_that_does_not_exist.yml"))
