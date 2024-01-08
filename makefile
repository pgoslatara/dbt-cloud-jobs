test:
	poetry run pytest --junitxml=coverage.xml --cov-report=term-missing:skip-covered --cov=dbt_cloud_jobs/ ./tests/unit --numprocesses 5 | tee pytest-coverage.txt && exit ${PIPESTATUS[0]}
	poetry run pytest --junitxml=coverage.xml --cov-report=term-missing:skip-covered --cov=dbt_cloud_jobs/ ./tests/integration --numprocesses 1 --cov-append | tee pytest-coverage.txt && exit ${PIPESTATUS[0]}
