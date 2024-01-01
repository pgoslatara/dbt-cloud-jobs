from typing import Mapping, Union

from dbt_cloud_jobs.dbt_cloud_helpers import create_dbt_cloud_job, list_dbt_cloud_jobs
from dbt_cloud_jobs.logger import logger


def sync_dbt_cloud_job(account_id: int, definition: Mapping[str, Union[int, str]]) -> None:
    existing_jobs = list_dbt_cloud_jobs(account_id=account_id)

    # Jobs that are new or need updating
    if definition["name"] in [job["name"] for job in existing_jobs]:
        logger.info(f"Job `{definition['name']}` already exists, updating...")
    else:
        logger.info(f"Job `{definition['name']}` does not exist, creating...")
        create_dbt_cloud_job(account_id=account_id, definition=definition)
