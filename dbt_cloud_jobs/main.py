import argparse
import inspect
import os
from pathlib import Path

import yaml

from dbt_cloud_jobs.dbt_cloud_helpers import delete_dbt_cloud_job, list_dbt_cloud_jobs
from dbt_cloud_jobs.logger import logger
from dbt_cloud_jobs.sync_job import sync_dbt_cloud_job


def main(args=None) -> None:
    logger.info("Running dbt_cloud_jobs...")

    logger.error(f"{args}")
    parser = argparse.ArgumentParser(description="Create dbt Cloud jobs from a YML file.")
    parser.add_argument(
        "--allow-deletes",
        action="store_true",
        default=False,
        help="When passed as a flag, any dbt Cloud job that does not exist in the specified YML file will be deleted.",
    )
    parser.add_argument(
        "--dbt-account-id",
        default=os.getenv("DBT_ACCOUNT_ID"),
        help="The account ID of your dbt Cloud account, can be found in the URL: https://cloud.getdbt.com/develop/<ACCOUNT_ID>/projects/<PROJECT_ID>. Defaults to the value of an environment variable called DBT_ACCOUNT_ID.",
        type=str,
    )
    parser.add_argument(
        "--file",
        "-f",
        default="dbt_cloud_jobs.yml",
        help="The name of the YML file containing the dbt Cloud job definitions. Defaults to `dbt_cloud_jobs.yml`.",
        type=str,
    )

    # Determining how function is called
    if inspect.stack()[1].code_context[0].strip() == "sys.exit(main())":
        args = parser.parse_args()
        caller = "cli"
    else:
        caller = "direct"  # i.e. pytest

    # Ensure the dbt account id is set and is valid
    if not args.dbt_account_id:
        raise RuntimeError(
            "You must pass a value to --dbt_account_id or via the DBT_ACCOUNT_ID env var."
        )

    try:
        dbt_account_id = int(args.dbt_account_id)
    except:
        raise RuntimeError(
            f"The value passed to --dbt-account-id or via the DBT_ACCOUNT_ID env var is not an integer: {args.dbt_account_id}."
        )
    logger.info(f"Using dbt account id: {args.dbt_account_id}")

    # Ensure yml file exists
    if not Path(args.file).exists():
        raise FileNotFoundError(f"{args.file} does not exists.")

    logger.info(f"Using definitions files: {args.file}")
    with Path.open(args.file) as f:
        job_definitions = yaml.safe_load(f)

    logger.debug(f"{job_definitions=}")
    logger.info(f"Found definitions for {len(job_definitions['jobs'])} job(s).")

    if len([x["name"] for x in job_definitions["jobs"]]) != len(
        {x["name"] for x in job_definitions["jobs"]}
    ):
        raise RuntimeError(f"Job names must be unique in `{args.file}`.")

    # New jobs and jobs that need updating
    for definition in job_definitions["jobs"]:
        sync_dbt_cloud_job(account_id=dbt_account_id, definition=definition)

    # Remove jobs no longer present in the YML file
    existing_jobs = list_dbt_cloud_jobs(account_id=dbt_account_id)
    for definition in existing_jobs:
        if definition["name"] not in [job["name"] for job in job_definitions["jobs"]]:
            if args.allow_deletes:
                delete_dbt_cloud_job(account_id=dbt_account_id, definition=definition)
            else:
                logger.warning(
                    f"Job `{definition['name']}` (id: {definition['id']}) exists in dbt Cloud but not in `{args.file}`. Pass `--allow-deletes` to delete this job from dbt Cloud."
                )


if __name__ == "__main__":
    main()
