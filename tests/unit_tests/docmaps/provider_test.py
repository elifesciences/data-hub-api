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
    generate_docmap_steps,
    get_outputs_type_form_tags
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
            'annotation_created_timestamp': 'annotation_created_timestamp_1',
            'tags': ['PeerReview']
        },
        {
            'hypothesis_id': 'hypothesis_id_2',
            'annotation_created_timestamp': 'annotation_created_timestamp_2',
            'tags': ['PeerReview', 'evaluationSummary']
        }
    ],
    'elife_doi': 'elife_doi_1'
}


@pytest.fixture(name='iter_dict_from_bq_query_mock', autouse=True)
def _iter_dict_from_bq_query_mock() -> Iterable[MagicMock]:
    with patch.object(provider_module, 'iter_dict_from_bq_query') as mock:
        yield mock


class TestGetOutputsTypeFromTags:
    def test_should_return_evaluation_summary_when_summary_exist_in_tags_list(self):
        tag_list_with_summary = ['PeerReview', 'evaluationSummary']
        actual_result = get_outputs_type_form_tags(tag_list_with_summary)
        assert actual_result == 'evaluation-summary'

    def test_should_return_review_article_when_review_keyword_exists_in_tags_list(self):
        tag_list_with_summary = ['PeerReview']
        actual_result = get_outputs_type_form_tags(tag_list_with_summary)
        assert actual_result == 'review-article'

    def test_should_return_review_article_for_review_keyword_even_there_is_undefined_tag(self):
        tag_list_with_summary = ['PeerReview', 'undefinedTag']
        actual_result = get_outputs_type_form_tags(tag_list_with_summary)
        assert actual_result == 'review-article'

    def test_should_return_author_response_when_author_response_keyword_exists_in_tags_list(self):
        tag_list_with_summary = ['AuthorResponse']
        actual_result = get_outputs_type_form_tags(tag_list_with_summary)
        assert actual_result == 'author-response'

    def test_should_return_author_response_when_author_response_even_there_is_review_tag(self):
        tag_list_with_summary = ['PeerReview', 'AuthorResponse']
        actual_result = get_outputs_type_form_tags(tag_list_with_summary)
        assert actual_result == 'author-response'

    def test_should_return_none_when_empty_tags_list(self):
        tag_list_with_summary = []
        actual_result = get_outputs_type_form_tags(tag_list_with_summary)
        assert not actual_result

    def test_should_return_none_when_there_is_not_any_defined_tag_in_tags_list(self):
        tag_list_with_summary = ['undefinedTag']
        actual_result = get_outputs_type_form_tags(tag_list_with_summary)
        assert not actual_result

    def test_should_raise_error_when_summary_and_author_response_in_tag_list_at_same_time(self):
        tag_list_with_summary = ['PeerReview', 'evaluationSummary', 'AuthorResponse']
        with pytest.raises(AssertionError):
            get_outputs_type_form_tags(tag_list_with_summary)


class TestGenerateDocmapSteps:
    def test_should_return_empty_dict_if_step_list_empty(self):
        step_list = []
        steps = generate_docmap_steps(step_list)
        assert steps == {}

    def test_should_return_all_step_keys_for_each_step(self):
        step_list = [{'step_1': 1}, {'step_2': 2}, {'step_3': 3}]
        steps = generate_docmap_steps(step_list)
        step_key_list = list(steps.keys())
        assert step_key_list == ['_:b0', '_:b1', '_:b2']

    def test_should_not_have_next_or_previous_step_keys_when_there_is_only_one_step(self):
        step_list = [{'step_1': 1}]
        steps = generate_docmap_steps(step_list)
        with pytest.raises(KeyError):
            assert steps['_:b0']['previous-step']
        with pytest.raises(KeyError):
            assert steps['_:b0']['next-step']

    def test_should_only_have_next_step_for_first_step_while_there_are_more_than_one_step(self):
        step_list = [{'step_1': 1}, {'step_2': 2}]
        steps = generate_docmap_steps(step_list)
        assert steps['_:b0']['next-step'] == '_:b1'
        with pytest.raises(KeyError):
            assert steps['_:b0']['previous-step']

    def test_should_have_both_next_and_previous_steps_keys_for_a_middle_step(self):
        step_list = [{'step_1': 1}, {'step_2': 2}, {'step_3': 3}]
        steps = generate_docmap_steps(step_list)
        assert steps['_:b1']['next-step'] == '_:b2'
        assert steps['_:b1']['previous-step'] == '_:b0'

    def test_should_only_have_previous_step_for_latest_step(self):
        step_list = [{'step_1': 1}, {'step_2': 2}, {'step_3': 3}]
        steps = generate_docmap_steps(step_list)
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

    def test_should_return_empty_list_for_inputs_manuscript_published_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        manuscript_published_step = docmaps_item['steps']['_:b0']
        assert manuscript_published_step['inputs'] == []

    def test_should_populate_assertions_manuscript_published_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        manuscript_published_step = docmaps_item['steps']['_:b0']
        assert manuscript_published_step['assertions'] == [{
            'item': {
                'type': 'preprint',
                'doi': DOI_1,
                'versionIdentifier': ''
            },
            'status': 'manuscript-published'
        }]

    def test_should_populate_actions_outputs_with_doi_and_url_manuscript_published_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        manuscript_published_step = docmaps_item['steps']['_:b0']
        assert manuscript_published_step['actions'] == [{
            'participants': [],
            'outputs': [{
                'type': 'preprint',
                'doi': DOI_1,
                'url': f'{DOI_ROOT_URL}{DOI_1}',
                'published': datetime.fromisoformat('2022-01-01T01:02:03+00:00'),
                'versionIdentifier': ''
            }]
        }]

    def test_should_populate_inputs_under_review_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        under_review_step = docmaps_item['steps']['_:b1']
        assert under_review_step['inputs'] == [{
            'type': 'preprint',
            'doi': DOI_1,
            'url': DOCMAPS_QUERY_RESULT_ITEM_1['preprint_url'],
        }]

    def test_should_populate_assertions_under_review_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        under_review_step = docmaps_item['steps']['_:b1']
        assert under_review_step['assertions'] == [
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

    def test_should_populate_actions_outputs_with_doi_and_url_under_review_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        under_review_step = docmaps_item['steps']['_:b1']
        assert under_review_step['actions'] == [{
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

    def test_should_populate_inputs_peer_reviewed_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(
            DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATIONS
        )
        peer_reviewed_step = docmaps_item['steps']['_:b2']
        assert peer_reviewed_step['inputs'] == [{
            'type': 'preprint',
            'doi': DOI_1,
            'url': DOCMAPS_QUERY_RESULT_ITEM_1['preprint_url'],
        }]

    def test_should_populate_assertions_peer_reviewed_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(
            DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATIONS
        )
        peer_reviewed_step = docmaps_item['steps']['_:b2']
        assert peer_reviewed_step['assertions'] == [{
            'item': {
                'type': 'preprint',
                'doi': DOI_1,
                'versionIdentifier': ''
            },
            'status': 'peer-reviewed'
        }]

    def test_should_not_populate_actions_in_peer_reviewed_step_if_tags_are_empty(self):
        query_result_with_evaluation = dict(
            DOCMAPS_QUERY_RESULT_ITEM_1,
            **{
                'evaluations': [{
                    'hypothesis_id': 'hypothesis_id_3',
                    'annotation_created_timestamp': 'annotation_created_timestamp_3',
                    'tags': []
                }]
            }
        )
        docmaps_item = get_docmap_item_for_query_result_item(
            query_result_with_evaluation
        )
        peer_reviewed_step = docmaps_item['steps']['_:b2']
        peer_reviewed_actions = peer_reviewed_step['actions']
        assert len(peer_reviewed_actions) == 0
        assert peer_reviewed_actions == []

    def test_should_populate_actions_outputs_peer_reviewed_step_for_each_evaluation(self):
        query_result_with_evaluation = dict(
            DOCMAPS_QUERY_RESULT_ITEM_1,
            **{
                'evaluations': [{
                    'hypothesis_id': 'hypothesis_id_1',
                    'annotation_created_timestamp': 'annotation_created_timestamp_1',
                    'tags': ['PeerReview']
                }, {
                    'hypothesis_id': 'hypothesis_id_2',
                    'annotation_created_timestamp': 'annotation_created_timestamp_2',
                    'tags': ['PeerReview', 'evaluationSummary']
                }]
            }
        )
        docmaps_item = get_docmap_item_for_query_result_item(
            query_result_with_evaluation
        )
        peer_reviewed_step = docmaps_item['steps']['_:b2']
        peer_reviewed_actions = peer_reviewed_step['actions']
        assert len(peer_reviewed_actions) == 2
        assert peer_reviewed_actions[0]['outputs'][0] == {
            'type': 'review-article',
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
        assert peer_reviewed_actions[1]['outputs'][0] == {
            'type': 'evaluation-summary',
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

    def test_should_populate_outputs_type_according_to_tags_peer_reviewed_step(self):
        query_result_with_evaluation = dict(
            DOCMAPS_QUERY_RESULT_ITEM_1,
            **{
                'evaluations': [{
                    'hypothesis_id': 'hypothesis_id_1',
                    'annotation_created_timestamp': 'annotation_created_timestamp_1',
                    'tags': ['PeerReview']
                }, {
                    'hypothesis_id': 'hypothesis_id_2',
                    'annotation_created_timestamp': 'annotation_created_timestamp_2',
                    'tags': ['PeerReview', 'evaluationSummary']
                }]
            }
        )
        docmaps_item = get_docmap_item_for_query_result_item(
            query_result_with_evaluation
        )
        peer_reviewed_step = docmaps_item['steps']['_:b2']
        peer_reviewed_actions = peer_reviewed_step['actions']
        outputs_for_index_0 = peer_reviewed_actions[0]['outputs'][0]
        outputs_for_index_1 = peer_reviewed_actions[1]['outputs'][0]
        assert outputs_for_index_0['type'] == 'review-article'
        assert outputs_for_index_1['type'] == 'evaluation-summary'


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
        assert provider.docmaps_index_query.rstrip().endswith('WHERE has_evaluations\nLIMIT 20')

    def test_should_allow_both_reviewed_prerint_type_and_evaluated_preprints_filter(
        self
    ):
        with pytest.raises(AssertionError):
            DocmapsProvider(
                only_include_reviewed_preprint_type=True,
                only_include_evaluated_preprints=True
            )
