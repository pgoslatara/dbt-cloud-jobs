import datetime
from typing import List, Literal, Optional, Set, Union

from pydantic import BaseModel, Extra, Field, StrictBool, root_validator, validator

from dbt_cloud_jobs.logger import logger


class DbtCloudJobExecution(BaseModel):
    timeout_seconds: int = Field(
        default=0,
        description="Maximum number of seconds a run will execute before it is canceled by dbt Cloud.",
        ge=0,
    )


class DbtCloudJobScheduleDateCron(BaseModel):
    cron: str = Field(
        default="0 * * * *",
        description="Using cron syntax, you can specify the minute, hour, day of the month, month, and day of the week, allowing you to set up complex schedules like running a job on the first Monday of each month.",
    )
    type: Literal["custom_cron"]

    # TODO: validate that cron matches cron in DbtCloudJobSchedule


class DbtCloudJobScheduleDate(BaseModel):
    days: Set[int] = Field(description="Days of the week, 0=Sunday.", ge=0, le=6)
    type: Literal["days_of_week"]


class DbtCloudJobScheduleDateHoursOfTheDay(BaseModel):
    days: Set[int] = Field(description="Days of the week, 0=Sunday.", ge=0, le=6)
    type: Literal["days_of_week"]


class DbtCloudJobScheduleTime(BaseModel):
    interval: Literal[1, 2, 3, 4, 6, 8, 12] = Field(
        description="Interval in hours between job executions."
    )
    type: Literal["every_hour"]


class DbtCloudJobScheduleTimeHoursOfTheDay(BaseModel):
    hours: Set[int] = Field(
        description="Hours of the day when the job will be executed, 0-indexed.", ge=0, le=23
    )
    type: Literal["at_exact_hours"]


class DbtCloudJobSchedule(BaseModel):
    cron: str = Field(
        default="0 * * * *",
        description="Using cron syntax, you can specify the minute, hour, day of the month, month, and day of the week, allowing you to set up complex schedules like running a job on the first Monday of each month.",
    )
    date: Union[
        DbtCloudJobScheduleDate,
        DbtCloudJobScheduleDateCron,
    ]  # Discriminate based on different field?
    time: Union[
        DbtCloudJobScheduleTimeHoursOfTheDay,
        DbtCloudJobScheduleTime,
    ]


class DbtCloudJobSettings(BaseModel):
    threads: int = Field(
        default=1,
        description="The maximum number of paths through the graph dbt may work on at once. Increasing the number of threads can minimize the run time of your project; however this may increase load on your warehouse.",
        gt=0,
    )
    target_name: str = Field(
        default="default",
        description="If you have logic that behaves differently depending on the specified target, set a value other than default.",
    )


class DbtCloudJobTriggers(BaseModel):
    github_webhook: StrictBool = False
    schedule: StrictBool = Field(
        default=False, description="Triggers a run when the schedule is active."
    )
    custom_branch_only: StrictBool = False


class DbtCloudJobConfig(BaseModel):
    account_id: int = Field(gt=0)
    created_at: Optional[datetime.datetime]
    cron_humanized: Optional[str]
    dbt_version: Optional[str] = Field(
        default=None,
        description="Override the dbt version this job runs on. This will cause your job to be out of sync with the environment.",
    )
    deactivated: StrictBool = False
    deferring_environment_id: Optional[int] = Field(
        description="Select an environment to compare code changes against. Only modified models will build and these modified models will reference upstream, unchanged models from the comparison environment.",
        gt=0,
    )
    deferring_job_definition_id: Optional[int] = Field(gt=0)
    description: Optional[str] = Field(
        description="Add additional context about this job to help your teammates understand its purpose."
    )
    environment_id: int
    execute_steps: List[str]
    execution: Optional[DbtCloudJobExecution]
    generate_docs: StrictBool = Field(
        default=False,
        description="Automatically generate updated project docs each time this job runs.",
    )
    generate_sources: StrictBool = Field(
        default=False,
        description="Enables dbt source freshness as the first step of this job, without breaking subsequent steps. Same as `run_generate_sources`.",
    )
    is_deferrable: StrictBool = False
    job_completion_trigger_condition: Optional[StrictBool]
    job_type: Optional[Literal["ci", "other", "scheduled"]]
    lifecycle_webhooks: StrictBool = False
    lifecycle_webhooks_url: Optional[str]
    name: str = Field(
        description="Consider choosing a name that's easily understood by your teammates."
    )
    next_run: Optional[datetime.datetime]
    next_run_humanized: Optional[str]
    project_id: int = Field(gt=0)
    raw_dbt_version: Optional[str]
    run_failure_count: Optional[int] = Field(ge=0)
    run_generate_sources: StrictBool = Field(
        default=False,
        description="Enables dbt source freshness as the first step of this job, without breaking subsequent steps. Same as `generate_sources`.",
    )
    schedule: DbtCloudJobSchedule
    settings: DbtCloudJobSettings
    state: Literal[1, 2] = Field(default=1, description="1 = Active, 2 = Deleted.")
    triggers: DbtCloudJobTriggers
    triggers_on_draft_pr: StrictBool = Field(
        default=False,
        description="Will run when a pull request is opened in draft mode, and subsequent commits.",
    )
    updated_at: Optional[datetime.datetime]

    class Config:
        extra = Extra.allow

    @root_validator()
    def check_id_is_not_passed(cls, values):
        if "id" in values.keys():
            raise ValueError("`id` should be be passed in the job definition.")
        else:
            return values

    @root_validator()
    def check_source_values_are_consistent(cls, values):
        if (values["generate_sources"] is True and values["run_generate_sources"] is False) or (
            values["generate_sources"] is False and values["run_generate_sources"] is True
        ):
            raise ValueError(
                "`generate_sources` and `run_generate_sources` must both contain the same value: False or True."
            )
        else:
            return values

    @validator("execute_steps")
    def dbt_command_validation(cls, cmd: List[str]) -> List[str]:
        for step in cmd:
            assert step.startswith("dbt ")

        return cmd


def validate_job_definition(definition: dict) -> None:
    logger.info("Validating job definition...")
    DbtCloudJobConfig(**definition)
