import os
from typing import Dict

import pytest
from pytest import MonkeyPatch

from dbt_cloud_jobs.dbt_api_helpers import (
    call_dbt_cloud_api,
    get_dbt_cloud_api_base_url,
)


def test_dbt_cloud_api_connection() -> None:
    """
    Test that the dbt Cloud API can be reached
    """

    response: Dict[str, Dict[str, str]] = call_dbt_cloud_api(
        method="get", endpoint=f'accounts/{os.getenv("DBT_ACCOUNT_ID")}/projects/'
    )  # type: ignore[assignment]
    assert response["status"]["is_success"]


def test_dbt_cloud_api_connection_errors() -> None:
    """
    Test that a RuntimeError is raised for invalid endpoint.
    """

    with pytest.raises(RuntimeError):
        call_dbt_cloud_api(
            method="get", endpoint=f'accounts/{os.getenv("DBT_ACCOUNT_ID")}/non_existent_endpoint/'
        )


def test_dbt_cloud_region_is_set() -> None:
    if os.getenv("DBT_CLOUD_REGION") not in ["AU", "Europe", "US"]:
        raise RuntimeError("The env var `DBT_CLOUD_REGION` must be one of: US, Europe, AU")


def test_get_dbt_cloud_api_base_url_invalid():
    with MonkeyPatch.context() as mp:
        mp.setenv("DBT_CLOUD_REGION", "")
        with pytest.raises(RuntimeError) as e:
            get_dbt_cloud_api_base_url.cache_clear()
            get_dbt_cloud_api_base_url()

        assert str(e.value) == "The env var `DBT_CLOUD_REGION` must be one of: US, Europe, AU"


@pytest.mark.parametrize(
    "dbt_cloud_region, base_url",
    (
        ["AU", "https://au.dbt.com"],
        ["Europe", "https://emea.dbt.com"],
        ["US", "https://cloud.getdbt.com"],
    ),
)
def test_get_dbt_cloud_api_base_url_valid(dbt_cloud_region, base_url):
    with MonkeyPatch.context() as mp:
        mp.setenv("DBT_CLOUD_REGION", dbt_cloud_region)
        get_dbt_cloud_api_base_url.cache_clear()
        assert get_dbt_cloud_api_base_url() == base_url


@pytest.mark.parametrize(
    "env_var_name", ("DBT_ACCOUNT_ID", "DBT_ENVIRONMENT_ID", "DBT_PROJECT_ID")
)
def test_required_env_vars_are_set(env_var_name) -> None:
    try:
        int(os.environ[env_var_name])
    except:
        raise RuntimeError(f"{env_var_name} must be set as a integer.")
