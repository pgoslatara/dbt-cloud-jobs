from dbt_cloud_jobs.main import main


def test_basic():
    assert main() == "Hello World!"
