import os

import pytest

from dbt_cloud_jobs.dbt_api_helpers import call_dbt_cloud_api


def test_dbt_cloud_api_connection() -> None:
    """
    Test that the dbt Cloud API can be reached
    """

    response = call_dbt_cloud_api(
        method="get", endpoint=f'accounts/{os.getenv("DBT_ACCOUNT_ID")}/projects/'
    )
    assert response["status"]["is_success"]


def test_dbt_cloud_api_connection_errors() -> None:
    """
    Test that a RuntimeError is raised for invalid endpoint.
    """

    with pytest.raises(RuntimeError):
        call_dbt_cloud_api(
            method="get", endpoint=f'accounts/{os.getenv("DBT_ACCOUNT_ID")}/non_existent_endpoint/'
        )


@pytest.mark.parametrize(
    "env_var_name", ("DBT_ACCOUNT_ID", "DBT_ENVIRONMENT_ID", "DBT_PROJECT_ID")
)
def test_required_env_vars_are_set(env_var_name) -> None:
    try:
        int(os.getenv(env_var_name))
    except:
        raise RuntimeError(f"{env_var_name} must be set as a integer.")
