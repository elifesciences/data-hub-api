FROM python:3.10-slim AS base

USER root
WORKDIR /app/api

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY requirements.txt ./
RUN uv pip install --system -r requirements.txt

COPY requirements.dev.txt ./
RUN uv pip install --system -r requirements.dev.txt

COPY .pylintrc .flake8 mypy.ini ./
COPY data_hub_api ./data_hub_api
COPY config ./config
COPY tests ./tests
COPY data ./data

CMD [ "python3", "-m", "uvicorn", "data_hub_api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--log-config=config/logging.yaml"]
