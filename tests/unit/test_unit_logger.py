import logging
from argparse import Namespace
from pathlib import Path
from tempfile import NamedTemporaryFile

import yaml

from dbt_cloud_jobs.logger import logger
from dbt_cloud_jobs.main import main
from dbt_cloud_jobs.validator import DbtCloudJobDefinitionsFile
from tests.pytest_helpers import catch_logs, hydrate_job_definition, records_to_tuples


def test_logger_debug(file_job_minimal_definition: DbtCloudJobDefinitionsFile) -> None:
    definitions = file_job_minimal_definition

    definition = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.safe_dump({"jobs": [definition]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    with catch_logs(level=logging.DEBUG, logger=logger) as handler:
        main(Namespace(file=file.name, validate=True))

        assert (
            len(
                [
                    record
                    for record in records_to_tuples(handler.records)
                    if record[2].startswith("caller='pytest'")
                ]
            )
            == 1
        )


def test_logger_info(caplog, file_job_minimal_definition: DbtCloudJobDefinitionsFile) -> None:
    caplog.set_level(logging.INFO)
    definitions = file_job_minimal_definition

    definition = hydrate_job_definition(definitions["jobs"][0])
    file = NamedTemporaryFile()
    file.write(bytes(yaml.safe_dump({"jobs": [definition]}), encoding="utf-8"))
    file.seek(0)
    with Path.open(Path(file.name), "r") as f:
        definitions = yaml.safe_load(f)

    main(Namespace(file=file.name, validate=True))

    assert "Running dbt_cloud_jobs (0.0.0)..." in caplog.text
