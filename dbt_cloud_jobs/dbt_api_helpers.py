import os
from functools import lru_cache
from typing import Any, Dict, Literal, Mapping, Optional, Union

import requests
from requests import HTTPError
from requests.auth import AuthBase
from requests.structures import CaseInsensitiveDict

from dbt_cloud_jobs.logger import logger
from dbt_cloud_jobs.validator import DbtCloudJobDefinition, DbtCloudJobDefinitionsFile


class DbtCloudAuth(AuthBase):
    """
    Create a base object that can be used to authenticate to the dbt Cloud API.
    """

    def __call__(self, r: requests.models.PreparedRequest):
        r.headers = CaseInsensitiveDict(
            {
                "Accept": "application/json",
                "Authorization": f'Token {os.getenv("DBT_API_TOKEN")}',
                "Content-Type": "application/json",
            }
        )
        return r


def call_dbt_cloud_api(
    method: Literal["delete", "get", "post"],
    endpoint: str,
    params: Optional[Mapping[str, Union[float, int, str]]] = None,
    payload: Optional[Mapping[str, Union[float, int, str]]] = None,
) -> Union[DbtCloudJobDefinition, Dict[Any, object]]:
    """
    A helper function for calling the dbt Cloud API.

    Args:
        method (str): _description_
        endpoint (str): _description_
        params (Optional[Mapping[str, Union[int, str]]], optional): _description_. Defaults to None.
        payload (Optional[Mapping[str, Union[int, str]]], optional): _description_. Defaults to None.

    Raises:
        RuntimeError

    Returns:
        Union[DbtCloudJobDefinition, Dict[Any, object]]
    """

    base_url = f"{get_dbt_cloud_api_base_url()}/api/v2/"
    if method == "get":
        r = create_requests_session().get(
            auth=DbtCloudAuth(),
            params=params,
            url=f"{base_url}{endpoint}",
        )
    elif method == "post":
        r = create_requests_session().post(
            auth=DbtCloudAuth(),
            json=payload,
            url=f"{base_url}{endpoint}",
        )
    elif method == "delete":
        r = create_requests_session().delete(
            auth=DbtCloudAuth(),
            url=f"{base_url}{endpoint}",
        )

    try:
        r.raise_for_status()
    except HTTPError as e:
        logger.error(f"{r.status_code=}")
        logger.error(f"{r.content=}")
        raise RuntimeError(e)

    return r.json()


def create_dbt_cloud_job(
    definition: DbtCloudJobDefinition,
) -> int:
    # New jobs require an "id" key in the payload, even though the value of this key does not yet exist
    definition["id"] = None

    logger.debug(f"{definition=}")
    r: DbtCloudJobDefinition = call_dbt_cloud_api(
        method="post",
        endpoint=f"accounts/{definition['account_id']}/jobs/",
        payload=definition,
    )[
        "data"
    ]  # type: ignore[assignment]
    logger.info(
        f"Created new dbt Cloud job, URL: https://cloud.getdbt.com/deploy/{definition['account_id']}/projects/{definition['project_id']}/jobs/{r['id']}"
    )
    return r["id"]


@lru_cache
def create_requests_session() -> requests.Session:
    """
    Create a requests session and cache it to avoid recreating the session.

    Returns:
        requests.Session
    """

    logger.info("Creating re-usable requests session...")
    return requests.Session()


def delete_dbt_cloud_job(
    definition: DbtCloudJobDefinition,
) -> None:
    logger.debug(f"{definition=}")
    call_dbt_cloud_api(
        method="delete",
        endpoint=f"accounts/{definition['account_id']}/jobs/{definition['id']}",
    )
    logger.warning(
        f"Deleted dbt Cloud job `{definition['name']}` (id: {definition['id']}), URL: https://cloud.getdbt.com/deploy/{definition['account_id']}/projects/{definition['project_id']}/jobs/{definition['id']}"
    )


@lru_cache
def get_dbt_cloud_api_base_url() -> str:
    """Returns the base URL to use for all dbt Cloud API calls.

    Raises:
        RuntimeError:

    Returns:
        str: Base url to use for all dbt Cloud API calls.
    """

    if os.getenv("DBT_CLOUD_REGION") == "US":
        return "https://cloud.getdbt.com"
    elif os.getenv("DBT_CLOUD_REGION") == "Europe":
        return "https://emea.dbt.com"
    elif os.getenv("DBT_CLOUD_REGION") == "AU":
        return "https://au.dbt.com"
    else:
        raise RuntimeError("The env var `DBT_CLOUD_REGION` must be one of: US, Europe, AU")


def list_dbt_cloud_jobs(account_id: int, project_id: int) -> DbtCloudJobDefinitionsFile:
    """
    Get a list of all existing dbt Cloud jobs

    Args:
        account_id (int)
        project_id (int)

    Returns:
        DbtCloudJobDefinitionsFile
    """

    logger.info(f"Listing dbt Cloud jobs for account id {account_id}...")

    jobs: DbtCloudJobDefinitionsFile = []  # type: ignore[assignment]
    while True:
        jobs_data = call_dbt_cloud_api(
            method="get",
            endpoint=f"accounts/{account_id}/jobs/",
            params={"offset": len(jobs), "project_id": project_id},
        )
        if jobs_data["data"] == []:
            break
        jobs += jobs_data["data"]

    logger.info(f"Found {len(jobs)} jobs...")

    return jobs
