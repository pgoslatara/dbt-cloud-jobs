import pytest

from dbt_cloud_jobs.utils import merge_job_definitions


@pytest.mark.parametrize(
    "dict_1, dict_2, merged_dict",
    [
        pytest.param(
            {"a": 1},
            {"a": 2},
            {"a": 2},
            id="Testing single top-level value change.",
        ),
        pytest.param(
            {"a": 1, "b": {"c": 3}},
            {"a": 1, "b": {"c": 3.1}},
            {"a": 1, "b": {"c": 3.1}},
            id="Testing single nested value change.",
        ),
        pytest.param(
            {"a": 1},
            {"a": 1, "b": 2},
            {"a": 1, "b": 2},
            id="Testing adding single top-level value key.",
        ),
        pytest.param(
            {"a": 1, "b": {"c": 3}},
            {"a": 1, "b": {"c": 3, "d": 4}},
            {"a": 1, "b": {"c": 3, "d": 4}},
            id="Testing adding single nested key.",
        ),
    ],
)
def test_merge_dicts(dict_1, dict_2, merged_dict) -> None:
    assert merge_job_definitions(job_def_1=dict_1, job_def_2=dict_2) == merged_dict
