from dbt_cloud_jobs.dbt_api_helpers import (
    call_dbt_cloud_api,
    create_dbt_cloud_job,
    list_dbt_cloud_jobs,
)
from dbt_cloud_jobs.logger import logger
from dbt_cloud_jobs.utils import merge_job_definitions
from dbt_cloud_jobs.validator import DbtCloudJobDefinition


def sync_dbt_cloud_job(definition: DbtCloudJobDefinition) -> None:
    existing_jobs = list_dbt_cloud_jobs(
        account_id=definition["account_id"], project_id=definition["project_id"]
    )

    # Jobs that are new or need updating
    if definition["name"] in [job["name"] for job in existing_jobs]:
        logger.info(f"Job `{definition['name']}` already exists, updating...")

        existing_definition = [x for x in existing_jobs if x["name"] == definition["name"]][0]
        logger.debug(f"{existing_definition=}")

        # definitions in YML may not contain id values, need to set manually to avoid comparison never returning True
        if not definition.get("id"):
            definition["id"] = existing_definition["id"]

        updated_definition = merge_job_definitions(existing_definition, definition)
        logger.debug(f"{updated_definition=}")
        if updated_definition == existing_definition:
            logger.info(
                f"Definition of job `{existing_definition['name']}` (id: {existing_definition['id']}) has not changed, will not be updated."
            )
        else:
            call_dbt_cloud_api(
                method="post",
                endpoint=f"accounts/{updated_definition['account_id']}/jobs/{updated_definition['id']}",
                payload=updated_definition,
            )
            logger.info(
                f"Updated dbt Cloud job, URL: https://cloud.getdbt.com/deploy/{definition['account_id']}/projects/{updated_definition['project_id']}/jobs/{updated_definition['id']}"
            )
    else:
        logger.info(f"Job `{definition['name']}` does not exist, creating...")
        create_dbt_cloud_job(definition=definition)
