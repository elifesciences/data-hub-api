import json
from datetime import datetime
from unittest.mock import patch, MagicMock
from typing import Iterable

import pytest

from data_hub_api.enhanced_preprints.docmaps import provider as provider_module
from data_hub_api.enhanced_preprints.docmaps.provider import (
    get_docmap_item_for_query_result_item,
    EnhancedPreprintsDocmapsProvider,
    DOCMAPS_JSONLD_SCHEMA_URL,
    DOCMAP_ID_PREFIX,
    DOCMAP_ID_SUFFIX
)


DOI_1 = '10.1101.test/doi1'
DOI_2 = '10.1101.test/doi2'


DOCMAPS_QUERY_RESULT_ITEM_1 = {
    'manuscript_id': 'manuscript_id_1',
    'qc_complete_timestamp': datetime.fromisoformat('2022-01-01T01:02:03+00:00'),
    'preprint_doi': DOI_1,
    'preprint_version': None,
    'preprint_url': f'https://doi.org/{DOI_1}',
    'docmap_id': 'docmap_id_1',
    'provider_json': '{"id": "provider_1"}'
}


@pytest.fixture(name='iter_dict_from_bq_query_mock', autouse=True)
def _iter_dict_from_bq_query_mock() -> Iterable[MagicMock]:
    with patch.object(provider_module, 'iter_dict_from_bq_query') as mock:
        yield mock


class TestGetDocmapsItemForQueryResultItem:
    def test_should_populate_context(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        assert docmaps_item['@context'] == DOCMAPS_JSONLD_SCHEMA_URL

    def test_should_populate_type(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        assert docmaps_item['type'] == 'docmap'

    def test_should_add_prefix_and_suffix_to_id(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        assert docmaps_item['id'] == (
            DOCMAP_ID_PREFIX + DOCMAPS_QUERY_RESULT_ITEM_1['docmap_id'] + DOCMAP_ID_SUFFIX
        )

    def test_should_populate_create_and_updated_timestamp_with_qc_complete_timestamp(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        assert docmaps_item['created'] == (
            DOCMAPS_QUERY_RESULT_ITEM_1['qc_complete_timestamp'].isoformat()
        )
        assert docmaps_item['updated'] == docmaps_item['created']

    def test_should_parse_and_include_provider_json(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        assert docmaps_item['provider'] == json.loads(
            DOCMAPS_QUERY_RESULT_ITEM_1['provider_json']
        )

    def test_should_populate_first_step_input_doi_and_url(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        first_step_key = docmaps_item['first-step']
        first_step = docmaps_item['steps'][first_step_key]
        first_step_input = first_step['inputs']
        assert len(first_step_input) == 1
        assert first_step_input[0]['doi'] == DOCMAPS_QUERY_RESULT_ITEM_1['preprint_doi']
        assert first_step_input[0]['url'] == DOCMAPS_QUERY_RESULT_ITEM_1['preprint_url']

    def test_should_populate_empty_first_step_assertions_and_actions(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        first_step_key = docmaps_item['first-step']
        first_step = docmaps_item['steps'][first_step_key]
        assert not first_step['assertions']
        assert not first_step['actions']


class TestEnhancedPreprintsDocmapsProvider:
    def test_should_create_index_with_non_empty_docmaps(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = iter([
            DOCMAPS_QUERY_RESULT_ITEM_1
        ])
        docmaps_index = EnhancedPreprintsDocmapsProvider().get_docmaps_index()
        assert docmaps_index['docmaps'] == [
            get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        ]
