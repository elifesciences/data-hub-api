FROM python:3.8-alpine3.17 AS base

USER root

WORKDIR /app/api

COPY requirements.build.txt ./
RUN pip install --disable-pip-version-check -r requirements.build.txt


COPY requirements.dev.txt ./
RUN pip install --disable-pip-version-check -r requirements.dev.txt

COPY .pylintrc .flake8 mypy.ini ./
COPY data_hub_api ./data_hub_api