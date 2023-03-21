import json
from datetime import date, datetime
from unittest.mock import patch, MagicMock
from typing import Iterable
import urllib

import pytest

from data_hub_api.utils.cache import InMemorySingleObjectCache
from data_hub_api.docmaps import provider as provider_module
from data_hub_api.docmaps.provider import (
    ADDITIONAL_PREPRINT_DOIS,
    DOCMAP_OUTPUT_TYPE_FOR_REPLY,
    DOCMAP_OUTPUT_TYPE_FOR_EVALUATION_SUMMARY,
    DOCMAP_OUTPUT_TYPE_FOR_REVIEW_ARTICLE,
    DOI_ROOT_URL,
    HYPOTHESIS_URL,
    SCIETY_ARTICLES_ACTIVITY_URL,
    SCIETY_ARTICLES_EVALUATIONS_URL,
    get_docmap_item_for_query_result_item,
    DocmapsProvider,
    DOCMAPS_JSONLD_SCHEMA_URL,
    DOCMAP_ID_PREFIX,
    generate_docmap_steps,
    get_outputs_type_form_tags
)


DOI_1 = '10.1101.test/doi1'
DOI_2 = '10.1101.test/doi2'

PREPRINT_VERSION_1 = '10'
PREPRINT_VERSION_2 = '11'

PREPRINT_LINK_PREFIX = 'https://test-preprints/'
PREPRINT_LINK_1_PREFIX = f'{PREPRINT_LINK_PREFIX}{DOI_1}'
PREPRINT_LINK_1 = f'{PREPRINT_LINK_1_PREFIX}v{PREPRINT_VERSION_1}'


DOCMAPS_QUERY_RESULT_ITEM_1: dict = {
    'manuscript_id': 'manuscript_id_1',
    'qc_complete_timestamp': datetime.fromisoformat('2022-01-01T01:02:03+00:00'),
    'preprint_published_at_date': date.fromisoformat('2021-01-01'),
    'preprint_doi': DOI_1,
    'preprint_version': PREPRINT_VERSION_1,
    'preprint_url': PREPRINT_LINK_1,
    'publisher_json': '{"id": "publisher_1"}',
    'evaluations': [],
    'elife_doi': 'elife_doi_1',
    'elife_doi_version_str': 'elife_doi_version_str_1',
    'editor_details': [],
    'senior_editor_details': [],
    'tdm_path': 'tdm_path_1'
}

HYPOTHESIS_ID_1 = 'hypothesis_1'
HYPOTHESIS_ID_2 = 'hypothesis_2'
HYPOTHESIS_ID_3 = 'hypothesis_3'

PEER_REVIEW_SUFFIX_1 = 'peer_review_suffix_1'
PEER_REVIEW_SUFFIX_2 = 'peer_review_suffix_2'
PEER_REVIEW_SUFFIX_3 = 'peer_review_suffix_3'

DOCMAPS_QUERY_RESULT_EVALUATION_1 = {
    'hypothesis_id': HYPOTHESIS_ID_1,
    'annotation_created_timestamp': '',
    'tags': [],
    'uri': PREPRINT_LINK_1,
    'source_version': PREPRINT_VERSION_1,
    'peer_review_suffix': PEER_REVIEW_SUFFIX_1
}


DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATIONS = {
    **DOCMAPS_QUERY_RESULT_ITEM_1,
    'evaluations': [DOCMAPS_QUERY_RESULT_EVALUATION_1]
}


@pytest.fixture(name='iter_dict_from_bq_query_mock', autouse=True)
def _iter_dict_from_bq_query_mock() -> Iterable[MagicMock]:
    with patch.object(provider_module, 'iter_dict_from_bq_query') as mock:
        yield mock


def get_hypothesis_urls_from_step_dict(step_dict: dict) -> Iterable[str]:
    return [
        content['url']
        for action in step_dict['actions']
        for output in action['outputs']
        for content in output['content']
        if content['url'].startswith(HYPOTHESIS_URL)
    ]


def get_hypothesis_ids_from_urls(hypothesis_urls: Iterable[str]) -> Iterable[str]:
    return [
        hypothesis_url[len(HYPOTHESIS_URL):]
        for hypothesis_url in hypothesis_urls
        if hypothesis_url.startswith(HYPOTHESIS_URL)
    ]


class TestGetOutputsTypeFromTags:
    def test_should_return_evaluation_summary_when_summary_exist_in_tags_list(self):
        tag_list_with_summary = ['PeerReview', 'evaluationSummary']
        actual_result = get_outputs_type_form_tags(tag_list_with_summary)
        assert actual_result == DOCMAP_OUTPUT_TYPE_FOR_EVALUATION_SUMMARY

    def test_should_return_review_article_when_review_keyword_exists_in_tags_list(self):
        tag_list_with_summary = ['PeerReview']
        actual_result = get_outputs_type_form_tags(tag_list_with_summary)
        assert actual_result == DOCMAP_OUTPUT_TYPE_FOR_REVIEW_ARTICLE

    def test_should_return_review_article_for_review_keyword_even_there_is_undefined_tag(self):
        tag_list_with_summary = ['PeerReview', 'undefinedTag']
        actual_result = get_outputs_type_form_tags(tag_list_with_summary)
        assert actual_result == DOCMAP_OUTPUT_TYPE_FOR_REVIEW_ARTICLE

    def test_should_return_reply_when_author_response_keyword_exists_in_tags_list(self):
        tag_list_with_summary = ['AuthorResponse']
        actual_result = get_outputs_type_form_tags(tag_list_with_summary)
        assert actual_result == DOCMAP_OUTPUT_TYPE_FOR_REPLY

    def test_should_return_reply_when_author_response_even_there_is_review_tag(self):
        tag_list_with_summary = ['PeerReview', 'AuthorResponse']
        actual_result = get_outputs_type_form_tags(tag_list_with_summary)
        assert actual_result == DOCMAP_OUTPUT_TYPE_FOR_REPLY

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

    def test_should_add_prefix_and_url_encode_preprint_doi_to_id(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        id_query_param = {'preprint_doi': DOCMAPS_QUERY_RESULT_ITEM_1['preprint_doi']}
        assert docmaps_item['id'] == (
            DOCMAP_ID_PREFIX + urllib.parse.urlencode(id_query_param)
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
                'versionIdentifier': DOCMAPS_QUERY_RESULT_ITEM_1['preprint_version']
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
                'url': PREPRINT_LINK_1,
                'published': (
                    DOCMAPS_QUERY_RESULT_ITEM_1['preprint_published_at_date']
                    .isoformat()
                ),
                'versionIdentifier': DOCMAPS_QUERY_RESULT_ITEM_1['preprint_version'],
                '_tdmPath': 'tdm_path_1'
            }]
        }]

    def test_should_set_published_to_none_if_unknown(self):
        docmaps_item = get_docmap_item_for_query_result_item({
            **DOCMAPS_QUERY_RESULT_ITEM_1,
            'preprint_published_at_date': None
        })
        manuscript_published_step = docmaps_item['steps']['_:b0']
        assert not manuscript_published_step['actions'][0]['outputs'][0].get('published')

    def test_should_populate_inputs_under_review_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        under_review_step = docmaps_item['steps']['_:b1']
        assert under_review_step['inputs'] == [{
            'type': 'preprint',
            'doi': DOI_1,
            'url': DOCMAPS_QUERY_RESULT_ITEM_1['preprint_url'],
            'versionIdentifier': DOCMAPS_QUERY_RESULT_ITEM_1['preprint_version']
        }]

    def test_should_populate_assertions_under_review_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        under_review_step = docmaps_item['steps']['_:b1']
        assert under_review_step['assertions'] == [
            {
                'item': {
                    'type': 'preprint',
                    'doi': DOI_1,
                    'versionIdentifier': DOCMAPS_QUERY_RESULT_ITEM_1['preprint_version']
                },
                'status': 'under-review',
                'happened': datetime.fromisoformat('2022-01-01T01:02:03+00:00')
            },
            {
                'item': {
                    'type': 'preprint',
                    'doi': 'elife_doi_1' + '.' + 'elife_doi_version_str_1',
                    'versionIdentifier': 'elife_doi_version_str_1'
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
                'versionIdentifier': 'elife_doi_version_str_1',
                'type': 'preprint',
                'doi': 'elife_doi_1' + '.' + 'elife_doi_version_str_1'
            }]
        }]

    def test_should_populate_inputs_peer_reviewed_step_from_preprint_url(self):
        docmaps_item = get_docmap_item_for_query_result_item(
            {
                **DOCMAPS_QUERY_RESULT_ITEM_1,
                'preprint_url': PREPRINT_LINK_1,
                'preprint_version': PREPRINT_VERSION_1,
                'evaluations': [{
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'uri': f'{PREPRINT_LINK_PREFIX}{DOI_1}v{PREPRINT_VERSION_2}',
                    'source_version': PREPRINT_VERSION_2
                }]
            }
        )
        peer_reviewed_step = docmaps_item['steps']['_:b2']
        assert peer_reviewed_step['inputs'] == [{
            'type': 'preprint',
            'doi': DOI_1,
            'url': PREPRINT_LINK_1,
            'versionIdentifier': PREPRINT_VERSION_1
        }]

    def test_should_filter_evaluations_by_preprint_link(self):
        expected_hypothesis_ids_of_first_version = {HYPOTHESIS_ID_1, HYPOTHESIS_ID_2}
        evaluations_of_first_version = [{
            **DOCMAPS_QUERY_RESULT_EVALUATION_1,
            'hypothesis_id': HYPOTHESIS_ID_1,
            'tags': ['PeerReview'],
            'uri': f'{PREPRINT_LINK_PREFIX}{DOI_1}v{PREPRINT_VERSION_1}',
            'source_version': PREPRINT_VERSION_1,
            'peer_review_suffix': PEER_REVIEW_SUFFIX_1
        }, {
            **DOCMAPS_QUERY_RESULT_EVALUATION_1,
            'hypothesis_id': HYPOTHESIS_ID_2,
            'tags': ['PeerReview'],
            'uri': f'{PREPRINT_LINK_PREFIX}{DOI_1}v{PREPRINT_VERSION_1}',
            'source_version': PREPRINT_VERSION_1,
            'peer_review_suffix': PEER_REVIEW_SUFFIX_2
        }]
        evaluations_of_other_version = [{
            **DOCMAPS_QUERY_RESULT_EVALUATION_1,
            'hypothesis_id': HYPOTHESIS_ID_3,
            'tags': ['PeerReview'],
            'uri': f'{PREPRINT_LINK_PREFIX}{DOI_1}v{PREPRINT_VERSION_2}',
            'source_version': PREPRINT_VERSION_2,
            'peer_review_suffix': PEER_REVIEW_SUFFIX_1
        }]
        docmaps_item = get_docmap_item_for_query_result_item({
            **DOCMAPS_QUERY_RESULT_ITEM_1,
            'preprint_version': PREPRINT_VERSION_1,
            'preprint_url': PREPRINT_LINK_1,
            'evaluations': (
                evaluations_of_first_version
                + evaluations_of_other_version
            )
        })
        peer_reviewed_step = docmaps_item['steps']['_:b2']
        assert peer_reviewed_step['inputs'] == [{
            'type': 'preprint',
            'doi': DOI_1,
            'url': f'{PREPRINT_LINK_PREFIX}{DOI_1}v{PREPRINT_VERSION_1}',
            'versionIdentifier': PREPRINT_VERSION_1
        }]
        actual_hypothesis_ids = set(get_hypothesis_ids_from_urls(
            get_hypothesis_urls_from_step_dict(peer_reviewed_step)
        ))
        assert actual_hypothesis_ids == expected_hypothesis_ids_of_first_version

    def test_should_populate_assertions_peer_reviewed_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(
            DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATIONS
        )
        peer_reviewed_step = docmaps_item['steps']['_:b2']
        assert peer_reviewed_step['assertions'] == [{
            'item': {
                'type': 'preprint',
                'doi': DOI_1,
                'versionIdentifier': (
                    DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATIONS['preprint_version']
                )
            },
            'status': 'peer-reviewed'
        }]

    def test_should_not_populate_actions_in_peer_reviewed_step_if_tags_are_empty(self):
        query_result_with_evaluation = dict(
            DOCMAPS_QUERY_RESULT_ITEM_1,
            **{
                'evaluations': [{
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
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
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'hypothesis_id': 'hypothesis_id_1',
                    'annotation_created_timestamp': 'annotation_created_timestamp_1',
                    'tags': ['PeerReview'],
                    'peer_review_suffix': 'peer_review_suffix_1'
                }, {
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'hypothesis_id': 'hypothesis_id_2',
                    'annotation_created_timestamp': 'annotation_created_timestamp_2',
                    'tags': ['PeerReview', 'evaluationSummary'],
                    'peer_review_suffix': 'peer_review_suffix_2'
                }, {
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'hypothesis_id': 'hypothesis_id_3',
                    'annotation_created_timestamp': 'annotation_created_timestamp_3',
                    'tags': ['PeerReview', 'AuthorResponse'],
                    'peer_review_suffix': 'peer_review_suffix_3'
                }]
            }
        )
        docmaps_item = get_docmap_item_for_query_result_item(
            query_result_with_evaluation
        )
        peer_reviewed_step = docmaps_item['steps']['_:b2']
        peer_reviewed_actions = peer_reviewed_step['actions']
        assert len(peer_reviewed_actions) == 3
        assert peer_reviewed_actions[0]['outputs'][0] == {
            'type': DOCMAP_OUTPUT_TYPE_FOR_REVIEW_ARTICLE,
            'published': 'annotation_created_timestamp_1',
            'doi': 'elife_doi_1'+'.'+'elife_doi_version_str_1'+'.'+'peer_review_suffix_1',
            'url': (
                f'{DOI_ROOT_URL}'
                + 'elife_doi_1' + '.'
                + 'elife_doi_version_str_1' + '.'
                + 'peer_review_suffix_1'
            ),
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
            'type': DOCMAP_OUTPUT_TYPE_FOR_EVALUATION_SUMMARY,
            'published': 'annotation_created_timestamp_2',
            'doi': 'elife_doi_1'+'.'+'elife_doi_version_str_1'+'.'+'peer_review_suffix_2',
            'url': (
                f'{DOI_ROOT_URL}'
                + 'elife_doi_1' + '.'
                + 'elife_doi_version_str_1' + '.'
                + 'peer_review_suffix_2'
            ),
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
        assert peer_reviewed_actions[2]['outputs'][0] == {
            'type': DOCMAP_OUTPUT_TYPE_FOR_REPLY,
            'published': 'annotation_created_timestamp_3',
            'doi': 'elife_doi_1'+'.'+'elife_doi_version_str_1'+'.'+'peer_review_suffix_3',
            'url': (
                f'{DOI_ROOT_URL}'
                + 'elife_doi_1' + '.'
                + 'elife_doi_version_str_1' + '.'
                + 'peer_review_suffix_3'
            ),
            'content': [
                {
                    'type': 'web-page',
                    'url': f'{HYPOTHESIS_URL}hypothesis_id_3'
                },
                {
                    'type': 'web-page',
                    'url': (
                        f'{SCIETY_ARTICLES_ACTIVITY_URL}'
                        f'{DOI_1}#hypothesis:hypothesis_id_3'
                    )
                },
                {
                    'type': 'web-page',
                    'url': (
                        f'{SCIETY_ARTICLES_EVALUATIONS_URL}'
                        'hypothesis_id_3/content'
                    )
                }
            ]
        }

    def test_should_populate_outputs_type_according_to_tags_peer_reviewed_step(self):
        query_result_with_evaluation = dict(
            DOCMAPS_QUERY_RESULT_ITEM_1,
            **{
                'evaluations': [{
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'hypothesis_id': 'hypothesis_id_1',
                    'annotation_created_timestamp': 'annotation_created_timestamp_1',
                    'tags': ['PeerReview']
                }, {
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'hypothesis_id': 'hypothesis_id_2',
                    'annotation_created_timestamp': 'annotation_created_timestamp_2',
                    'tags': ['PeerReview', 'evaluationSummary']
                }, {
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'hypothesis_id': 'hypothesis_id_3',
                    'annotation_created_timestamp': 'annotation_created_timestamp_3',
                    'tags': ['PeerReview', 'AuthorResponse']
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
        outputs_for_index_2 = peer_reviewed_actions[2]['outputs'][0]
        assert outputs_for_index_0['type'] == DOCMAP_OUTPUT_TYPE_FOR_REVIEW_ARTICLE
        assert outputs_for_index_1['type'] == DOCMAP_OUTPUT_TYPE_FOR_EVALUATION_SUMMARY
        assert outputs_for_index_2['type'] == DOCMAP_OUTPUT_TYPE_FOR_REPLY

    def test_should_populate_participants_in_peer_reviewed_step_for_review_article_type(self):
        query_result_with_evaluation = dict(
            DOCMAPS_QUERY_RESULT_ITEM_1,
            **{
                'evaluations': [{
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'hypothesis_id': 'hypothesis_id_1',
                    'annotation_created_timestamp': 'annotation_created_timestamp_1',
                    'tags': ['PeerReview']
                }]
            }
        )
        docmaps_item = get_docmap_item_for_query_result_item(
            query_result_with_evaluation
        )
        peer_reviewed_step = docmaps_item['steps']['_:b2']
        peer_reviewed_actions = peer_reviewed_step['actions']
        participants_for_review_article = peer_reviewed_actions[0]['participants']
        assert participants_for_review_article == [
            {
                'actor': {
                    'name': 'anonymous',
                    'type': 'person'
                },
                'role': 'peer-reviewer'
            }
        ]

    def test_should_populate_participants_in_peer_reviewed_step_for_evaluation_summary_type(self):
        query_result_with_evaluation = dict(
            DOCMAPS_QUERY_RESULT_ITEM_1,
            **{
                'evaluations': [{
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'hypothesis_id': 'hypothesis_id_2',
                    'annotation_created_timestamp': 'annotation_created_timestamp_2',
                    'tags': ['PeerReview', 'evaluationSummary']
                }]
            }
        )
        query_result_with_editor_details = dict(
            query_result_with_evaluation,
            **{
                'editor_details': [{
                    'name': 'editor_name_1',
                    'institution': 'editor_institution_1',
                    'country': 'editor_country_1'
                }, {
                    'name': 'editor_name_2',
                    'institution': 'editor_institution_2',
                    'country': ''
                }],
                'senior_editor_details': [{
                    'name': 'senior_editor_name_1',
                    'institution': 'senior_editor_institution_1',
                    'country': 'senior_editor_country_1'
                }]
            }
        )
        docmaps_item = get_docmap_item_for_query_result_item(
            query_result_with_editor_details
        )
        peer_reviewed_step = docmaps_item['steps']['_:b2']
        peer_reviewed_actions = peer_reviewed_step['actions']
        participants_for_evaluation_summary = peer_reviewed_actions[0]['participants']
        assert participants_for_evaluation_summary == [
            {
                'actor': {
                    'name': 'editor_name_1',
                    'type': 'person',
                    '_relatesToOrganization': 'editor_institution_1, editor_country_1'
                },
                'role': 'editor'
            },
            {
                'actor': {
                    'name': 'editor_name_2',
                    'type': 'person',
                    '_relatesToOrganization': 'editor_institution_2'
                },
                'role': 'editor'
            },
            {
                'actor': {
                    'name': 'senior_editor_name_1',
                    'type': 'person',
                    '_relatesToOrganization': 'senior_editor_institution_1, senior_editor_country_1'
                },
                'role': 'senior-editor'
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

    def test_should_cache_docmaps_query_results(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = [
            DOCMAPS_QUERY_RESULT_ITEM_1
        ]
        docmaps_provider = DocmapsProvider(
            query_results_cache=InMemorySingleObjectCache(max_age_in_seconds=10)
        )
        docmaps_provider.get_docmaps_index()
        docmaps_index = docmaps_provider.get_docmaps_index()
        assert iter_dict_from_bq_query_mock.call_count == 1
        assert docmaps_index['docmaps'] == [
            get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        ]

    def test_should_add_is_reviewed_preprint_and_is_under_review_type_where_clause_to_query(
        self
    ):
        provider = DocmapsProvider(
            only_include_reviewed_preprint_type=True,
            only_include_evaluated_preprints=False,
            additionally_include_preprint_dois=[]
        )
        assert provider.docmaps_index_query.rstrip().endswith(
            'WHERE is_reviewed_preprint_type AND is_or_was_under_review'
        )

    def test_should_add_additional_preprint_dois_to_query_filter(
        self
    ):
        provider = DocmapsProvider(
            only_include_reviewed_preprint_type=True,
            only_include_evaluated_preprints=False,
            additionally_include_preprint_dois=ADDITIONAL_PREPRINT_DOIS
        )
        assert provider.docmaps_index_query.rstrip().endswith(
            f'OR preprint_doi IN {ADDITIONAL_PREPRINT_DOIS}'
        )

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
