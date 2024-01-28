import sys
from collections.abc import MutableMapping
from functools import lru_cache

from dbt_cloud_jobs.validator import DbtCloudJobDefinition


@lru_cache
def job_prefix() -> str:
    """Generates a string that is used during testing to create (and delete) jobs dedicated to testing (and not impact other jobs).

    Returns:
        str: Always starts with "dbt_cloud_jobs_ci_" followed by the version of python being used.
    """
    return f"dbt_cloud_jobs_ci_{sys.version_info[0]}_{sys.version_info[1]}_{sys.version_info[2]}"


def merge_job_definitions(
    job_def_1: DbtCloudJobDefinition, job_def_2: DbtCloudJobDefinition
) -> DbtCloudJobDefinition:
    """
    Takes 2 job definitions as inputs, the values in the second job are merged into the first,
    i.e. second job overwrites equivalent keys in the first job.

    Returns:
        DbtCloudJobDefinition: A single job.
    """
    for k, v in job_def_1.items():
        if k in job_def_2:
            if all(isinstance(e, MutableMapping) for e in (v, job_def_2[k])):
                job_def_2[k] = merge_job_definitions(v, job_def_2[k])

    merged_job = job_def_1.copy()
    merged_job.update(job_def_2)
    return merged_job
