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

1. Set an environment variable with the value of the token:

    ```bash
    export DBT_API_TOKEN="<VALUE_FROM_PREVIOUS_STEP>"
    ```

1. Set an environment variable for the region where your dbt Cloud account is hosted. The value must be one of "AU", "Europe" or "US" (see docs [here](https://docs.getdbt.com/dbt-cloud/api-v2#/)):

    ```bash
    export DBT_CLOUD_REGION="<REGION>"
    ```

1. Import your existing dbt Cloud jobs:

    ```bash
    dbt_cloud_jobs --import --account-id 123456 --file dbt_cloud_jobs.yml
    ```

1. Edit the definition of your jobs in `dbt_cloud_jobs.yml`.

1. Sync the updated definitions to dbt Cloud:

    ```bash
    dbt_cloud_jobs --sync --file dbt_cloud_jobs.yml
    ```

# Recommended usage in CI/CD

## CI

In CI `dbt-cloud-jobs` should be used to verify that the provided YML file is valid. For example:

```yaml
    - name: Install dbt_cloud_jobs
      run: pip install dbt-cloud-jobs

    - name: Validate `dbt_cloud_jobs.yml`
      run: dbt_cloud_jobs --validate --file dbt_cloud_jobs.yml
```

## CD

In CD `dbt-cloud-jobs` should be used to sync the provided YML file to dbt Cloud. For example:

```yaml
    - name: Install dbt_cloud_jobs
      run: pip install dbt-cloud-jobs

    - name: Sync `dbt_cloud_jobs.yml`
      run: dbt_cloud_jobs --sync --file dbt_cloud_jobs.yml
```

## Example

For an example of how this package can be used, take a look at [`dbt-cloud-jobs-example-repo`](https://github.com/pgoslatara/dbt-cloud-jobs-example-repo), specifically:

* The [`dbt_cloud_jobs.yml`](https://github.com/pgoslatara/dbt-cloud-jobs-example-repo/blob/main/dbt_cloud_jobs.yml) file.
* The [CI pipeline](https://github.com/pgoslatara/dbt-cloud-jobs-example-repo/blob/main/.github/workflows/ci_pipeline.yml).
* The [CD pipeline](https://github.com/pgoslatara/dbt-cloud-jobs-example-repo/blob/main/.github/workflows/cd_pipeline.yml).
* This [CI pipeline](https://github.com/pgoslatara/dbt-cloud-jobs-example-repo/actions/runs/8238754815/job/22530416583) run that validated the jobs definitions added in [PR1](https://github.com/pgoslatara/dbt-cloud-jobs-example-repo/pull/1).
* This [CD pipeline](https://github.com/pgoslatara/dbt-cloud-jobs-example-repo/actions/runs/8238763252/job/22530445750) run that updated the `Daily job` dbt Cloud job.

# Limitations/Warnings

* Service account tokens are created at the account level. This means that if you have multiple dbt Cloud accounts you will need to create different `dbt_cloud_jobs.yml` files for each account. If you try to use `dbt-cloud-jobs` with a file that contains multiple `account_id` values, an error will be raised.

* ⚠️ `dbt_cloud_jobs` expects to "own" all the jobs in the projects where it is used. This means that if you are running `dbt_cloud_jobs --sync --file dbt_cloud_jobs.yml` for the first time in a project, any pre-existing jobs not present in your `dbt_cloud_jobs.yml` file will be deleted.

# Development

To setup your development environment, fork this repository and run:

```bash
poetry shell
poetry install
```

Set the following environment variables:
```bash
export DBT_ACCOUNT_ID=<DBT_ACCOUNT_ID>
export DBT_CLOUD_REGION="<DBT_CLOUD_REGION>"
export DBT_ENVIRONMENT_ID=<DBT_ENVIRONMENT_ID>
export DBT_PROJECT_ID=<DBT_PROJECT_ID>
export DBT_API_TOKEN="<DBT_API_TOKEN>"
```
It is highly recommended that a dedicated dbt Cloud environment be used for development.

All tests can be run via:
```bash
make test
```

# Release

Trigger the `Publish to PyPi` workflow, inputting the version to publish to PyPi. This workflow will:

- Publish the version to [PyPi](https://pypi.org/project/dbt-cloud-jobs/).
- Tag the HEAD commit of the `main` branches (tags visible [here](https://github.com/pgoslatara/dbt-cloud-jobs/tags)).
- Create a release (releases visible [here](https://github.com/pgoslatara/dbt-cloud-jobs/releases)).
