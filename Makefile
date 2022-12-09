DOCKER_COMPOSE_DEV = docker-compose
DOCKER_COMPOSE_CI = docker-compose -f docker-compose.yml
DOCKER_COMPOSE = $(DOCKER_COMPOSE_DEV)

VENV = venv
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python


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
	$(PYTHON) -m flake8 dummy_api

dev-pylint:
	$(PYTHON) -m pylint dummy_api

dev-mypy:
	$(PYTHON) -m mypy dummy_api


dev-lint: dev-flake8 dev-pylint dev-mypy


ci-build-and-test:
	$(DOCKER_COMPOSE_CI) build

ci-clean:
	$(DOCKER_COMPOSE_CI) down -v