import os

from dbt_cloud_jobs.dbt_cloud_helpers import call_dbt_cloud_api


def test_dbt_cloud_api_connection() -> None:
    """
    Test that the dbt Cloud API can be reached
    """

    response = call_dbt_cloud_api(
        method="get", endpoint=f'accounts/{os.getenv("DBT_ACCOUNT_ID")}/projects/'
    )
    assert response["status"]["is_success"]
