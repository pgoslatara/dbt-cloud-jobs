from pathlib import Path

import pytest
import yaml


@pytest.fixture(scope="function")
def file_definition_valid(tmp_path: Path) -> Path:
    file = tmp_path / "test_duplicate_job_names.yml"
    with open(file, "w") as f1:
        yaml.dump(
            {"jobs": [{"name": "job1", "account_id": 123}, {"name": "job2", "account_id": 123}]},
            f1,
        )

    return file
