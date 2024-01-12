class DbtCloudJobsDuplicateJobNameError(Exception):
    """Exception raised when more than one job defined in a YML file contains the same name.

    Args:
        message (str): Explainer of the error.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class DbtCloudJobsInvalidArguments(Exception):
    """Exception raised when the arguments supplied to `dbt_cloud_jobs` are invalid.

    Args:
        message (str): Explainer of the error.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
