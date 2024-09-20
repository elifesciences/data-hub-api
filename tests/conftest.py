import logging

import pytest


@pytest.fixture(scope='session', autouse=True)
def setup_logging():
    logging.basicConfig(level='INFO')
    for name in ['tests', 'data_hub_api']:
        logging.getLogger(name).setLevel('DEBUG')
