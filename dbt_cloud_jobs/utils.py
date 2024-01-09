import sys
from collections.abc import MutableMapping
from functools import lru_cache


@lru_cache
def job_prefix() -> str:
    """Generates a string that is used during testing to create (and delete) jobs dedicated to testing (and not impact other jobs).

    Returns:
        str: Always starts with "dbt_cloud_jobs_ci_" followed by the version of python being used.
    """
    return f"dbt_cloud_jobs_ci_{sys.version_info[0]}_{sys.version_info[1]}_{sys.version_info[2]}"


def merge_dicts(dict_1: dict, dict_2: dict) -> dict:
    """
    Takes 2 dicts as inputs, the values in the second dict are merged into the first,
    i.e. second dict overwrites equivalent keys in the first dict.

    Returns:
        dict: A single dict.
    """
    for k, v in dict_1.items():
        if k in dict_2:
            if all(isinstance(e, MutableMapping) for e in (v, dict_2[k])):
                dict_2[k] = merge_dicts(v, dict_2[k])

    merged_dict = dict_1.copy()
    merged_dict.update(dict_2)
    return merged_dict
