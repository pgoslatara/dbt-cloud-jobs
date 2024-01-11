test:
	$(MAKE) test_unit
	$(MAKE) test_integration

test_integration:
	poetry run pytest --junitxml=coverage.xml --cov-report=term-missing:skip-covered --cov=dbt_cloud_jobs/ ./tests/integration --numprocesses 1 --cov-append

test_unit:
	poetry run pytest --junitxml=coverage.xml --cov-report=term-missing:skip-covered --cov=dbt_cloud_jobs/ ./tests/unit --numprocesses 5
