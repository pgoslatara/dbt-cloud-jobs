from pathlib import Path

import yaml

from dbt_cloud_jobs.dbt_api_helpers import delete_dbt_cloud_job, list_dbt_cloud_jobs
from dbt_cloud_jobs.exceptions import (
    DbtCloudJobsDuplicateJobNameError,
    DbtCloudJobsInvalidArguments,
)
from dbt_cloud_jobs.logger import logger
from dbt_cloud_jobs.parser import parse_args
from dbt_cloud_jobs.sync_job import sync_dbt_cloud_job
from dbt_cloud_jobs.utils import job_prefix
from dbt_cloud_jobs.validator import validate_job_definition
from dbt_cloud_jobs.version import version


def main(args=None) -> None:
    logger.info(f"Running dbt_cloud_jobs ({version()})...")
    args, caller = parse_args(args)

    # Verify supplied arguments are valid
    if args.account_id is None and args.import_:
        raise DbtCloudJobsInvalidArguments(
            "`--account_id` must be passed when `--import` is passed."
        )
    elif sum([args.import_, args.validate, args.sync]) == 0:
        raise DbtCloudJobsInvalidArguments(
            "One of `--import`, `--validate` and `--sync` must be specified."
        )
    elif sum([args.import_, args.validate, args.sync]) > 1:
        raise DbtCloudJobsInvalidArguments(
            "Only one of `--import`, `--validate` and `--sync` can be specified."
        )

    if args.import_:
        logger.info("Operation: import")

        # Ensure yml file doesn't already exists
        if Path(args.file).exists():
            raise FileExistsError(
                f"{args.file} already exists, please choose a different file name."
            )

        job_definitions = list_dbt_cloud_jobs(args.account_id)

        # Remove `id` key as `name` is used to identify jobs
        for definition in job_definitions:
            definition.pop("id")

        logger.info(f"Saving job definitions to `{args.file}...")
        with Path.open(Path(args.file), "w") as f:
            yaml.safe_dump({"jobs": job_definitions}, stream=f, encoding="utf-8", sort_keys=True)

    elif args.validate or args.sync:
        logger.info("Operation: validate")

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
            raise DbtCloudJobsDuplicateJobNameError(f"Job names must be unique in `{args.file}`.")

        for definition in job_definitions["jobs"]:
            validate_job_definition(definition=definition)

        logger.info(f"All jobs defined in {args.file} are valid.")

    if args.sync:
        logger.info("Operation: sync")

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
    elif not args.import_ and args.validate and not args.sync:
        logger.warning(f"Pass `--sync` to sync the jobs defined in `{args.file}` to dbt Cloud.")


if __name__ == "__main__":
    main()
