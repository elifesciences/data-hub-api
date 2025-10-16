# Data Hup API

This repo includes eLife Data Hub APIs. Currently all API endpoints are DocMap related.

## Development Using Virtual Environment

### Pre-requisites (Virtual Environment)

* Python, ideally using `pyenv` (see `.python-version`)
* GCP credentials in `~/.config/gcloud` (e.g. via `gcloud auth application-default login`)

### First Setup (Virtual Environment)

```bash
make dev-venv
```

### Update Dependencies (Virtual Environment)

```bash
make dev-install
```

### Run Tests (Virtual Environment)

```bash
make dev-test
```

### Start Server (Virtual Environment)

```bash
make dev-start
```

The server will be available on port 8000.

You can access the API Docs via [/docs](http://localhost:8000/docs)

### Run Regression Test (Virtual Environment)

By default, this will require the server to be running locally.
You can also use `DATA_HUB_API_REGRESSION_TEST_URL_PREFIX` to point to staging or prod.

```bash
make dev-regression-test
```

### Update Regression Test Data (Virtual Environment)

You can update the regression test data using the following command:

```bash
make dev-update-regression-test-data
```

This will currently only include the enhanced-preprint data (not Kotahi).

It will update the files in [data/docmaps/regression_test/docmap_by_manuscript_id](data/docmaps/regression_test/docmap_by_manuscript_id).

Please review the changes carefully.

## Development Using Docker

### Pre-requisites (Docker)

* Docker

### Run Tests (Docker)

```bash
make build test
```

### Start Server (Docker)

```bash
make build start logs
```

The server will be available on port 8000.

You can access the API Docs via [/docs](http://localhost:8000/docs)

### Stop Server (Docker)

```bash
make stop
```
