ifneq (,$(wildcard ./.env))
    include .env
    export
endif

requirements:
	pip3 install -r requirements.txt 
	pip3 install -r requirements-test.txt 
	pip3 install -r requirements-postgres.txt
.PHONY: requirements

fix-fmt:
	black .
.PHONY: fix-fmt

fix-imports:
	isort .
.PHONY: fix-imports

fix: fix-imports fix-fmt
.PHONY: fix

check-fmt:
	black --check .
.PHONY: check-fmt

check-imports:
	isort --check .
.PHONY: check-imports

check-lint:
	pylint action
.PHONY: check-lint

check-type:
	mypy action
.PHONY: check-type

check: check-fmt check-imports check-lint check-type
.PHONY: check

run:
	./action.sh
.PHONY: run
