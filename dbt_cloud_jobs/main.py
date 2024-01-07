import argparse
import inspect
from pathlib import Path

import yaml

from dbt_cloud_jobs.dbt_cloud_helpers import delete_dbt_cloud_job, list_dbt_cloud_jobs
from dbt_cloud_jobs.exceptions import DuplicateJobNameError
from dbt_cloud_jobs.logger import logger
from dbt_cloud_jobs.sync_job import sync_dbt_cloud_job
from tests.pytest_helpers import job_prefix


def main(args=None) -> None:
    logger.info("Running dbt_cloud_jobs...")

    parser = argparse.ArgumentParser(description="Create dbt Cloud jobs from a YML file.")
    parser.add_argument(
        "--allow-deletes",
        action="store_true",
        default=False,
        help="When passed as a flag, any dbt Cloud job that does not exist in the specified YML file will be deleted.",
    )
    parser.add_argument(
        "--file",
        "-f",
        default="dbt_cloud_jobs.yml",
        help="The name of the YML file containing the dbt Cloud job definitions. Defaults to `dbt_cloud_jobs.yml`.",
        type=str,
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        default=False,
        help="When passed as a flag, any dbt Cloud jobs defined in the file passed to `--file` will be synced to dbt Cloud.",
    )

    # Determining how function is called
    if (
        inspect.stack()[1].code_context[0].strip() == "sys.exit(main())"
    ):  # Not true when pytest calls main()
        args = parser.parse_args()
        caller = "cli"
    else:
        caller = "pytest"
        # Set default values if necessary
        passed_args = [x[0] for x in args._get_kwargs()]
        if "allow_deletes" not in passed_args:
            args.allow_deletes = False
        if "sync" not in passed_args:
            args.sync = False

    # Ensure yml file exists
    if not Path(args.file).exists():
        raise FileNotFoundError(f"{args.file} does not exists.")

    logger.info(f"Using definitions files: {args.file}")
    with Path.open(Path(args.file)) as f:
        job_definitions = yaml.safe_load(f)

    logger.debug(f"{job_definitions=}")
    logger.info(f"Found definitions for {len(job_definitions['jobs'])} job(s).")

    if len([x["name"] for x in job_definitions["jobs"]]) != len(
        {x["name"] for x in job_definitions["jobs"]}
    ):
        raise DuplicateJobNameError(f"Job names must be unique in `{args.file}`.")

    if args.sync:
        for definition in job_definitions["jobs"]:
            # New jobs and jobs that need updating
            sync_dbt_cloud_job(definition=definition)

        # Remove jobs no longer present in the YML file
        for account_id in {x["account_id"] for x in job_definitions["jobs"]}:
            existing_jobs = list_dbt_cloud_jobs(account_id=account_id)
            for job in existing_jobs:
                if job["name"] not in [
                    job["name"]
                    for job in job_definitions["jobs"]
                    if job["account_id"] == account_id
                ]:
                    if args.allow_deletes and (
                        caller == "cli"
                        or (caller == "pytest" and job["name"].startswith(job_prefix()))
                    ):
                        delete_dbt_cloud_job(definition=job)
                    else:
                        logger.warning(
                            f"Job `{job['name']}` (id: {job['id']}) exists in dbt Cloud but not in `{args.file}`. Pass `--allow-deletes` to delete this job from dbt Cloud."
                        )
    else:
        logger.warning(f"Pass `--sync` to sync the jobs defined in `{args.file}` to dbt Cloud.")


if __name__ == "__main__":
    main()
