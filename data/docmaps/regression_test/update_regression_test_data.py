import json
import logging
import os
from pathlib import Path

import requests

LOGGER = logging.getLogger(__name__)


DEFAULT_DATA_HUB_API_REGRESSION_TEST_URL_PREFIX = 'http://localhost:8000'
DATA_HUB_API_REGRESSION_TEST_URL_PREFIX_ENV = 'DATA_HUB_API_REGRESSION_TEST_URL_PREFIX'

DOCMAP_BY_MANUSCRIPT_PATH = (
    '/enhanced-preprints/docmaps/v2/by-publisher/elife/get-by-manuscript-id'
)

def get_regression_test_url_prefix() -> str:
    return os.getenv(
        DATA_HUB_API_REGRESSION_TEST_URL_PREFIX_ENV,
        DEFAULT_DATA_HUB_API_REGRESSION_TEST_URL_PREFIX
    )


def get_regression_test_docmap_by_manuscript_url(
    regression_test_url_prefix: str
) -> str:
    return regression_test_url_prefix + DOCMAP_BY_MANUSCRIPT_PATH


def main():
    LOGGER.info('Updating regression test data...')
    docmap_by_manuscript_id_data_path = (
        Path('./data/docmaps/regression_test/docmap_by_manuscript_id')
    )
    json_files = list(docmap_by_manuscript_id_data_path.glob('*.json'))
    LOGGER.info('Found %d JSON files:', len(json_files))
    regression_test_docmap_by_manuscript_url = (
        get_regression_test_docmap_by_manuscript_url(
            get_regression_test_url_prefix()
        )
    )
    for json_file in json_files:
        LOGGER.info('JSON file: %s', json_file)
        manuscript_id = Path(json_file).name.split('.')[0]
        LOGGER.info('manuscript_id: %s', manuscript_id)
        base_url = f'{regression_test_docmap_by_manuscript_url}'
        LOGGER.debug('base url: %s', base_url)
        response = requests.get(base_url, params={'manuscript_id': manuscript_id})
        LOGGER.info('url: %s', response.url)
        response.raise_for_status()
        docmap_json = response.json()
        Path(json_file).write_text(
            json.dumps(docmap_json, indent=4, ensure_ascii=False),
            encoding='utf-8'
        )
    LOGGER.info('Regression test data updated.')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
