FROM python:3.9-slim AS base

USER root
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app/api

COPY requirements.build.txt ./
RUN pip install --disable-pip-version-check -r requirements.build.txt

COPY requirements.txt ./
RUN pip install --disable-pip-version-check -r requirements.txt

COPY requirements.dev.txt ./
RUN pip install --disable-pip-version-check -r requirements.dev.txt

COPY .pylintrc .flake8 mypy.ini ./
COPY data_hub_api ./data_hub_api
COPY config ./config
COPY tests ./tests
COPY data ./data

CMD [ "python3", "-m", "uvicorn", "data_hub_api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--log-config=config/logging.yaml"]
