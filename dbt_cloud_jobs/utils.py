import os
from functools import lru_cache
from typing import Literal, Mapping, Optional, Union

import requests
from requests.auth import AuthBase

from dbt_cloud_jobs.logger import logger


class DbtCloudAuth(AuthBase):
    """
    Create a base object that can be used to authenticate to the dbt Cloud API.
    """

    def __call__(self, r):
        r.headers = {
            "Content-Type": "application/json",
            "Authorization": f'Token {os.getenv("DBT_API_TOKEN")}',
        }
        return r


def call_dbt_cloud_api(
    method: Literal["get"],
    endpoint: str,
    params: Optional[Mapping[str, Union[int, str]]] = None,
) -> Mapping[str, Union[int, str]]:
    """
    A helper function for calling the dbt Cloud API.

    Args:
        method (str): _description_
        endpoint (str): _description_
        params (Optional[Mapping[str, Union[int, str]]], optional): _description_. Defaults to None.

    Raises:
        RuntimeError: _description_

    Returns:
        Mapping[str, Union[int, str]]: _description_
    """

    base_url = "https://cloud.getdbt.com/api/v3/"
    if method == "get":
        r = create_requests_session().get(
            f"{base_url}{endpoint}",
            auth=DbtCloudAuth(),
            params=params,
        )

    try:
        assert r.status_code == 200
    except AssertionError as e:
        logger.error(f"{r.status_code=}")
        raise RuntimeError(e)

    return r.json()


@lru_cache
def create_requests_session() -> requests.Session:
    """
    Create a requests session and cache it to avoid recreating the session.

    Returns:
        requests.Session
    """

    logger.info("Creating re-usable requests session...")
    return requests.Session()
