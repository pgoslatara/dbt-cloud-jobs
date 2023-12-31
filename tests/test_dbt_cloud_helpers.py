import os

from dbt_cloud_jobs.dbt_cloud_helpers import call_dbt_cloud_api, list_dbt_cloud_jobs


def test_dbt_cloud_api_connection() -> None:
    """
    Test that the dbt Cloud API can be reached
    """

    response = call_dbt_cloud_api(
        method="get", endpoint=f'accounts/{os.getenv("DBT_ACCOUNT_ID")}/projects/'
    )
    assert response["status"]["is_success"]


def test_list_dbt_cloud_jobs() -> None:
    existing_jobs = list_dbt_cloud_jobs(os.getenv("DBT_ACCOUNT_ID"))
    assert isinstance(existing_jobs, list)
