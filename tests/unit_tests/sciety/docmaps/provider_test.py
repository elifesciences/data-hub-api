from unittest.mock import patch, MagicMock
from typing import Iterable

import pytest

from data_hub_api.sciety.docmaps import provider as provider_module
from data_hub_api.sciety.docmaps.provider import (
    get_docmaps_item_for_query_result_item,
    ScietyDocmapsProvider
)


DOI_1 = '10.1101.test/doi1'
DOI_2 = '10.1101.test/doi2'


DOCMAPS_QUERY_RESULT_ITEM_1 = {
    'manuscript_id': 'manuscript_id_1',
    'qc_complete_timestamp': '2022-01-01 01:02:03Z',
    'preprint_doi': DOI_1,
    'preprint_version': None,
    'preprint_url': f'https://doi.org/{DOI_1}'
}


@pytest.fixture(name='iter_dict_from_bq_query_mock', autouse=True)
def _iter_dict_from_bq_query_mock() -> Iterable[MagicMock]:
    with patch.object(provider_module, 'iter_dict_from_bq_query') as mock:
        yield mock


class TestScietyDocmapsProvider:
    def test_should_create_index_with_non_empty_articles(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = iter([
            DOCMAPS_QUERY_RESULT_ITEM_1
        ])
        docmaps_index = ScietyDocmapsProvider().get_docmaps_index()
        assert docmaps_index['articles'] == [
            get_docmaps_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        ]
