from dbt_cloud_jobs.version import version


def test_version() -> None:
    assert version() == "0.0.0"
