# dbt-cloud-jobs

[![pypi version shield](https://img.shields.io/pypi/v/dbt-cloud-jobs)](https://img.shields.io/pypi/v/dbt-cloud-jobs)
![CI](https://github.com/pgoslatara/dbt-cloud-jobs/actions/workflows/ci_pipeline.yml/badge.svg)
![Publish](https://github.com/pgoslatara/dbt-cloud-jobs/actions/workflows/publish.yml/badge.svg)
![Python versions](https://img.shields.io/pypi/pyversions/dbt-cloud-jobs.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Version control your dbt Cloud jobs with YML.

# Installation

```bash
pip install dbt-cloud-jobs
```

# Quickstart

1. Create an API token in dbt Cloud:

    - [Generate a service account token](https://docs.getdbt.com/docs/dbt-cloud-apis/service-tokens#generate-service-account-tokens), make sure to grant the `Jobs Admin` permission set.
    - If you do not have access to create a service account token you can create a [User API token](https://docs.getdbt.com/docs/dbt-cloud-apis/user-tokens). Note that the service account method is preferred.

1. Set an environment variables with the value of the token:

    ```bash
    export DBT_API_TOKEN="<VALUE_FROM_PREVIOUS_STEP>"
    ```

1. Import your existing dbt Cloud jobs:

    ```bash
    dbt_cloud_jobs --import --account_id 123456 --file dbt_cloud_jobs.yml
    ```

1. Edit the definition of your jobs in `dbt_cloud_jobs.yml`.

1. Sync the updated definitions to dbt Cloud:

    ```bash
    dbt_cloud_jobs --sync --file dbt_cloud_jobs.yml
    ```

# Recommended usage in CI/CD

## CI

In CI `dbt_cloud_jobs` should be used to verify that the provided YML file is valid. For example:

```bash
    - name: Install dbt_cloud_jobs
      run: pip install dbt_cloud_jobs

    - name: Validate `dbt_cloud_jobs.yml`
      run: dbt_cloud_jobs --validate --file dbt_cloud_jobs.yml
```

## CD

In CD `dbt_cloud_jobs` should be used to sync the provided YML file to dbt Cloud. For example:

```bash
    - name: Install dbt_cloud_jobs
      run: pip install dbt_cloud_jobs

    - name: Sync `dbt_cloud_jobs.yml`
      run: dbt_cloud_jobs --sync --file dbt_cloud_jobs.yml
```

# Development

# Release

Trigger the `Publish` workflow, inputting the version to publish to PyPi. This workflow will:

- Publish the version to [PyPi](https://pypi.org/project/dbt-cloud-jobs/).
- Tag the HEAD commit of the `main` branches (tags visible [here](https://github.com/pgoslatara/dbt-cloud-jobs/tags)).
- Create a release (releases visible [here](https://github.com/pgoslatara/dbt-cloud-jobs/releases)).
