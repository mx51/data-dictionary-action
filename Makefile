requirements:
	pip3 install -r requirements.txt 
	pip3 install -r requirements-test.txt 
	pip3 install -r requirements-postgres.txt
.PHONY: requirements

fmt:
	black .

check-fmt:
	black --check .
.PHONY: check-fmt

check-lint:
	pylint action
.PHONY: check-lint

check-type:
	mypy action
.PHONY: check-type

check: check-fmt check-lint check-type
.PHONY: check
