test:
	pytest ./tests/unit --numprocesses 5
	pytest ./tests/integration --numprocesses 1
