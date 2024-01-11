import argparse
import inspect

from dbt_cloud_jobs.logger import logger


def parse_args(args):
    parser = argparse.ArgumentParser(description="Create dbt Cloud jobs from a YML file.")
    parser.add_argument(
        "--account_id",
        help="The dbt Cloud account ID, only used when `--import` is passed.",
        type=int,
    )
    parser.add_argument(
        "--allow-deletes",
        action="store_true",
        default=False,
        help="When passed as a flag, any dbt Cloud job that does not exist in the specified YML file will be deleted.",
    )
    parser.add_argument(
        "--file",
        "-f",
        help="""
            When used with `--import`, the name of the YML file where dbt Cloud job definitions will be saved. This file cannot exist beforehand.
            When used with `--sync`, the name of the YML file containing the dbt Cloud job definitions.
        """,
        type=str,
    )
    parser.add_argument(
        "--import",
        action="store_true",
        default=False,
        dest="import_",
        help="When passed as a flag, any dbt Cloud job will be saved to a file specified by the `--file` parameter.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        default=False,
        help="When passed as a flag, any dbt Cloud jobs defined in the file passed to `--file` will be validated. No job on dbt Cloud will be updated; to do this, pass `--sync` instead of `--validate`.",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        default=False,
        help="When passed as a flag, any dbt Cloud jobs defined in the file passed to `--file` will be synced to dbt Cloud.",
    )

    # Determining how function is called
    if (
        inspect.stack()[2].code_context[0].strip() == "sys.exit(main())"
    ):  # Not true when pytest calls main()
        args = parser.parse_args()
        caller = "cli"
        logger.debug(f"{caller=}")
    else:
        caller = "pytest"
        logger.debug(f"{caller=}")
        # Set default values if necessary
        passed_args = [x[0] for x in args._get_kwargs()]
        for arg in parser._actions:
            if arg.dest not in passed_args:
                setattr(args, arg.dest, arg.default)

    return args, caller
