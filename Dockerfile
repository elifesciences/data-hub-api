FROM python:3.13-slim AS base

USER root
WORKDIR /app/api

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV VENV=/opt/venv
ENV VIRTUAL_ENV=${VENV} PYTHONUSERBASE=${VENV} PATH=${VENV}/bin:$PATH

COPY pyproject.toml uv.lock ./
RUN uv sync --active --frozen \
  --dev

COPY .pylintrc .flake8 mypy.ini ./
COPY data_hub_api ./data_hub_api
COPY config ./config
COPY tests ./tests
COPY data ./data

CMD [ "python3", "-m", "uvicorn", "data_hub_api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--log-config=config/logging.yaml"]
