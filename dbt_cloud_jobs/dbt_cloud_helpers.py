import os
from functools import lru_cache
from typing import List, Literal, Mapping, Optional, Union

import requests
from requests import HTTPError
from requests.auth import AuthBase

from dbt_cloud_jobs.logger import logger


class DbtCloudAuth(AuthBase):
    """
    Create a base object that can be used to authenticate to the dbt Cloud API.
    """

    def __call__(self, r):
        r.headers = {
            "Accept": "application/json",
            "Authorization": f'Token {os.getenv("DBT_API_TOKEN")}',
            "Content-Type": "application/json",
        }
        return r


def call_dbt_cloud_api(
    method: Literal["get", "post"],
    endpoint: str,
    params: Optional[Mapping[str, Union[int, str]]] = None,
    payload: Optional[Mapping[str, Union[int, str]]] = None,
) -> Mapping[str, Union[int, str]]:
    """
    A helper function for calling the dbt Cloud API.

    Args:
        method (str): _description_
        endpoint (str): _description_
        params (Optional[Mapping[str, Union[int, str]]], optional): _description_. Defaults to None.
        payload (Optional[Mapping[str, Union[int, str]]], optional): _description_. Defaults to None.

    Raises:
        RuntimeError: _description_

    Returns:
        Mapping[str, Union[int, str]]: _description_
    """

    # TODO: allow setting of URL to account for AU/EU/US
    base_url = "https://cloud.getdbt.com/api/v2/"
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

    try:
        r.raise_for_status()
    except HTTPError as e:
        logger.error(f"{r.status_code=}")
        logger.error(f"{r.content=}")
        raise RuntimeError(e)

    return r.json()


def create_dbt_cloud_job(account_id: int, definition) -> int:  # TODO pydantic class for definition
    logger.debug(f"{definition=}")
    r = call_dbt_cloud_api(
        method="post",
        endpoint=f"accounts/{account_id}/jobs/",
        payload=definition,
    )
    logger.info(
        f"Created new dbt Cloud job, URL: https://cloud.getdbt.com/deploy/{account_id}/projects/{definition['environment_id']}/jobs/{r['data']['id']}"
    )
    return r["data"]["id"]


@lru_cache
def create_requests_session() -> requests.Session:
    """
    Create a requests session and cache it to avoid recreating the session.

    Returns:
        requests.Session
    """

    logger.info("Creating re-usable requests session...")
    return requests.Session()


def list_dbt_cloud_jobs(account_id: int) -> List[Mapping[str, Union[int, str]]]:
    """
    Get a list of all existing dbt Cloud jobs

    Args:
        account_id (int): _description_

    Returns:
        List[Mapping[str, Union[int, str]]]: _description_
    """

    # TODO: pagination
    return call_dbt_cloud_api(
        method="get",
        endpoint=f"accounts/{account_id}/jobs/",
    )["data"]
