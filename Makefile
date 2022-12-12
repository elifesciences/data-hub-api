DOCKER_COMPOSE_DEV = docker-compose
DOCKER_COMPOSE_CI = docker-compose -f docker-compose.yml
DOCKER_COMPOSE = $(DOCKER_COMPOSE_DEV)

VENV = venv
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python

ARGS =
PYTEST_WATCH_MODULES = tests/unit_tests

venv-clean:
	@if [ -d "$(VENV)" ]; then \
		rm -rf "$(VENV)"; \
	fi


venv-create:
	python3 -m venv $(VENV)


venv-activate:
	chmod +x venv/bin/activate
	bash -c "venv/bin/activate"


dev-install:
	$(PIP) install --disable-pip-version-check \
		-r requirements.build.txt \
		-r requirements.dev.txt


dev-venv: venv-create dev-install


dev-flake8:
	$(PYTHON) -m flake8 data_hub_api tests

dev-pylint:
	$(PYTHON) -m pylint data_hub_api tests

dev-mypy:
	$(PYTHON) -m mypy data_hub_api tests


dev-lint: dev-flake8 dev-pylint dev-mypy


dev-unittest:
	$(PYTHON) -m pytest -p no:cacheprovider $(ARGS) tests/unit_tests

dev-watch:
	$(PYTHON) -m pytest_watch -- -p no:cacheprovider $(ARGS) $(PYTEST_WATCH_MODULES)

dev-test: dev-lint dev-unittest


build:
	$(DOCKER_COMPOSE) build data-hub-api

ci-build-and-test:
	$(DOCKER_COMPOSE_CI) build

ci-clean:
	$(DOCKER_COMPOSE_CI) down -v