from dbt_cloud_jobs.logger import logger


def main() -> None:
    logger.info("Hello!")
    return "Hello World!"


if __name__ == "__main__":
    main()
