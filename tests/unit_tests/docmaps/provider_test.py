import json
from datetime import datetime
from unittest.mock import patch, MagicMock
from typing import Iterable

import pytest

from data_hub_api.docmaps import provider as provider_module
from data_hub_api.docmaps.provider import (
    DOI_ROOT_URL,
    ELIFE_REVIEWED_PREPRINTS_URL,
    HYPOTHESIS_URL,
    SCIETY_ARTICLES_ACTIVITY_URL,
    SCIETY_ARTICLES_EVALUATIONS_URL,
    get_docmap_item_for_query_result_item,
    DocmapsProvider,
    DOCMAPS_JSONLD_SCHEMA_URL,
    DOCMAP_ID_PREFIX,
    DOCMAP_ID_SUFFIX,
    generate_docmap_steps
)


DOI_1 = '10.1101.test/doi1'
DOI_2 = '10.1101.test/doi2'


DOCMAPS_QUERY_RESULT_ITEM_1 = {
    'manuscript_id': 'manuscript_id_1',
    'qc_complete_timestamp': datetime.fromisoformat('2022-01-01T01:02:03+00:00'),
    'preprint_doi': DOI_1,
    'preprint_version': None,
    'preprint_url': f'{DOI_ROOT_URL}{DOI_1}',
    'docmap_id': 'docmap_id_1',
    'publisher_json': '{"id": "publisher_1"}',
    'evaluations': [],
    'elife_doi': 'elife_doi_1'
}

DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATIONS = {
    'manuscript_id': 'manuscript_id_1',
    'qc_complete_timestamp': datetime.fromisoformat('2022-01-01T01:02:03+00:00'),
    'preprint_doi': DOI_1,
    'preprint_version': None,
    'preprint_url': f'{DOI_ROOT_URL}{DOI_1}',
    'docmap_id': 'docmap_id_1',
    'publisher_json': '{"id": "publisher_1"}',
    'evaluations': [
        {
            'hypothesis_id': 'hypothesis_id_1',
            'annotation_created_timestamp': 'annotation_created_timestamp_1'
        },
        {
            'hypothesis_id': 'hypothesis_id_2',
            'annotation_created_timestamp': 'annotation_created_timestamp_2'
        }
    ],
    'elife_doi': 'elife_doi_1'
}


@pytest.fixture(name='iter_dict_from_bq_query_mock', autouse=True)
def _iter_dict_from_bq_query_mock() -> Iterable[MagicMock]:
    with patch.object(provider_module, 'iter_dict_from_bq_query') as mock:
        yield mock


class TestGenerateDocmapSteps:
    def test_should_return_minimum_required_fields_for_a_step(self):
        steps = generate_docmap_steps(1, DOCMAPS_QUERY_RESULT_ITEM_1)
        assert steps['_:b0']['inputs'] == []
        assert steps['_:b0']['actions']
        assert steps['_:b0']['assertions']

    def test_should_return_first_step_key_if_number_of_steps_is_one(self):
        steps = generate_docmap_steps(1, DOCMAPS_QUERY_RESULT_ITEM_1)
        assert steps['_:b0']

    def test_should_return_all_step_keys_if_number_of_steps_is_more_than_one(self):
        steps = generate_docmap_steps(3, DOCMAPS_QUERY_RESULT_ITEM_1)
        step_key_list = list(steps.keys())
        assert step_key_list == ['_:b0', '_:b1', '_:b2']

    def test_should_not_have_next_or_previous_step_keys_while_number_of_steps_is_one(self):
        steps = generate_docmap_steps(1, DOCMAPS_QUERY_RESULT_ITEM_1)
        with pytest.raises(KeyError):
            assert steps['_:b0']['previous-step']
        with pytest.raises(KeyError):
            assert steps['_:b0']['next-step']

    def test_should_only_have_next_step_for_first_step_while_number_of_steps_more_than_one(self):
        steps = generate_docmap_steps(2, DOCMAPS_QUERY_RESULT_ITEM_1)
        assert steps['_:b0']['next-step'] == '_:b1'
        with pytest.raises(KeyError):
            assert steps['_:b0']['previous-step']

    def test_should_have_both_next_and_previous_steps_keys_for_a_middle_step(self):
        steps = generate_docmap_steps(3, DOCMAPS_QUERY_RESULT_ITEM_1)
        assert steps['_:b1']['next-step'] == '_:b2'
        assert steps['_:b1']['previous-step'] == '_:b0'

    def test_should_only_have_previous_step_for_latest_step(self):
        steps = generate_docmap_steps(3, DOCMAPS_QUERY_RESULT_ITEM_1)
        assert steps['_:b2']['previous-step'] == '_:b1'
        with pytest.raises(KeyError):
            assert steps['_:b2']['next-step']


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

    def test_should_parse_and_include_publisher_json(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        assert docmaps_item['publisher'] == json.loads(
            DOCMAPS_QUERY_RESULT_ITEM_1['publisher_json']
        )

    def test_should_have_an_empty_list_for_inputs_in_first_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        second_step_input = docmaps_item['steps']['_:b0']['inputs']
        assert len(second_step_input) == 0

    def test_should_populate_other_steps_inputs_doi_and_url(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        second_step_input = docmaps_item['steps']['_:b1']['inputs']
        assert len(second_step_input) == 1
        assert second_step_input[0]['type'] == 'preprint'
        assert second_step_input[0]['doi'] == DOCMAPS_QUERY_RESULT_ITEM_1['preprint_doi']
        assert second_step_input[0]['url'] == DOCMAPS_QUERY_RESULT_ITEM_1['preprint_url']
        third_step_input = docmaps_item['steps']['_:b2']['inputs']
        assert len(third_step_input) == 1
        assert third_step_input[0]['type'] == 'preprint'
        assert third_step_input[0]['doi'] == DOCMAPS_QUERY_RESULT_ITEM_1['preprint_doi']
        assert third_step_input[0]['url'] == DOCMAPS_QUERY_RESULT_ITEM_1['preprint_url']

    def test_should_populate_first_step_assertions_with_status_manuscript_published(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        first_step_key = docmaps_item['first-step']
        first_step = docmaps_item['steps'][first_step_key]
        assert first_step['assertions'] == [{
            'item': {
                'type': 'preprint',
                'doi': DOI_1,
                'versionIdentifier': ''
            },
            'status': 'manuscript-published'
        }]

    def test_should_populate_second_step_assertions_with_status_under_review_and_draft(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        second_step_assertions = docmaps_item['steps']['_:b1']['assertions']
        assert second_step_assertions == [
            {
                'item': {
                    'type': 'preprint',
                    'doi': DOI_1,
                    'versionIdentifier': ''
                },
                'status': 'under-review',
                'happened': datetime.fromisoformat('2022-01-01T01:02:03+00:00')
            },
            {
                'item': {
                    'type': 'preprint',
                    'doi': 'elife_doi_1',
                    'versionIdentifier': ''
                },
                'status': 'draft'
            }
        ]

    def test_should_populate_third_step_assertions_with_status_peer_reviewed(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        second_step_assertions = docmaps_item['steps']['_:b2']['assertions']
        assert second_step_assertions == [{
            'item': {
                'type': 'preprint',
                'doi': DOI_1,
                'versionIdentifier': ''
            },
            'status': 'peer-reviewed'
        }]

    def test_should_populate_first_step_actions_outputs_with_doi_and_url(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        first_step = docmaps_item['steps']['_:b0']
        assert first_step['actions'] == [{
            'participants': [],
            'outputs': [{
                'type': 'preprint',
                'doi': DOI_1,
                'url': f'{DOI_ROOT_URL}{DOI_1}',
                'published': datetime.fromisoformat('2022-01-01T01:02:03+00:00'),
                'versionIdentifier': ''
            }]
        }]

    def test_should_populate_second_step_actions_outputs_with_necessary_details(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        second_step = docmaps_item['steps']['_:b1']
        assert second_step['actions'] == [{
            'participants': [],
            'outputs': [{
                'identifier': 'manuscript_id_1',
                'versionIdentifier': '',
                'type': 'preprint',
                'doi': 'elife_doi_1',
                'url': f'{DOI_ROOT_URL}elife_doi_1',
                'content': [{
                    'type': 'web-page',
                    'url': f'{ELIFE_REVIEWED_PREPRINTS_URL}manuscript_id_1'
                }]
            }]
        }]

    def test_should_populate_actions_for_articles_with_evaluations_in_first_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(
            DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATIONS
        )
        first_step_key = docmaps_item['first-step']
        first_step = docmaps_item['steps'][first_step_key]
        assert first_step['actions'] == [
            {
                'participants': [],
                'outputs': [
                    {
                        'type': '',
                        'doi': 'elife_doi_1',
                        'published': 'annotation_created_timestamp_1',
                        'url': f'{DOI_ROOT_URL}elife_doi_1',
                        'content': [
                            {
                                'type': 'web-page',
                                'url': f'{HYPOTHESIS_URL}hypothesis_id_1'
                            },
                            {
                                'type': 'web-page',
                                'url': (
                                    f'{SCIETY_ARTICLES_ACTIVITY_URL}'
                                    f'{DOI_1}#hypothesis:hypothesis_id_1'
                                )
                            },
                            {
                                'type': 'web-page',
                                'url': (
                                    f'{SCIETY_ARTICLES_EVALUATIONS_URL}'
                                    'hypothesis_id_1/content'
                                )
                            }
                        ]
                    }
                ]
            },
            {
                'participants': [],
                'outputs': [
                    {
                        'type': '',
                        'doi': 'elife_doi_1',
                        'published': 'annotation_created_timestamp_2',
                        'url': f'{DOI_ROOT_URL}elife_doi_1',
                        'content': [
                            {
                                'type': 'web-page',
                                'url': f'{HYPOTHESIS_URL}hypothesis_id_2'
                            },
                            {
                                'type': 'web-page',
                                'url': (
                                    f'{SCIETY_ARTICLES_ACTIVITY_URL}'
                                    f'{DOI_1}#hypothesis:hypothesis_id_2'
                                )
                            },
                            {
                                'type': 'web-page',
                                'url': (
                                    f'{SCIETY_ARTICLES_EVALUATIONS_URL}'
                                    'hypothesis_id_2/content'
                                )
                            }
                        ]
                    }
                ]
            }
        ]


class TestEnhancedPreprintsDocmapsProvider:
    def test_should_create_index_with_non_empty_docmaps(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = iter([
            DOCMAPS_QUERY_RESULT_ITEM_1
        ])
        docmaps_index = DocmapsProvider().get_docmaps_index()
        assert docmaps_index['docmaps'] == [
            get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        ]

    def test_should_add_is_reviewed_preprint_type_where_clause_to_query(
        self
    ):
        provider = DocmapsProvider(
            only_include_reviewed_preprint_type=True,
            only_include_evaluated_preprints=False
        )
        assert provider.docmaps_index_query.rstrip().endswith('WHERE is_reviewed_preprint_type')

    def test_should_add_has_evaluatons_where_clause_to_query(
        self
    ):
        provider = DocmapsProvider(
            only_include_reviewed_preprint_type=False,
            only_include_evaluated_preprints=True
        )
        assert provider.docmaps_index_query.rstrip().endswith('WHERE has_evaluations')

    def test_should_allow_both_reviewed_prerint_type_and_evaluated_preprints_filter(
        self
    ):
        with pytest.raises(AssertionError):
            DocmapsProvider(
                only_include_reviewed_preprint_type=True,
                only_include_evaluated_preprints=True
            )
