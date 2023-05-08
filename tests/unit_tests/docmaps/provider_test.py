import json
from datetime import date, datetime
from unittest.mock import patch, MagicMock
from typing import Iterable
import urllib

import pytest
from data_hub_api.docmaps.codecs.elife_manuscript import (
    get_docmap_elife_manuscript_doi_assertion_item,
    get_docmap_elife_manuscript_output,
    get_elife_manuscript_version_doi
)
from data_hub_api.docmaps.codecs.evaluation import (
    HYPOTHESIS_URL,
    get_docmap_evaluation_output,
)

from data_hub_api.docmaps.codecs.preprint import (
    get_docmap_preprint_assertion_item,
    get_docmap_preprint_input,
    get_docmap_preprint_output
)

from data_hub_api.utils.cache import InMemorySingleObjectCache
from data_hub_api.docmaps import provider as provider_module
from data_hub_api.docmaps.provider import (
    ADDITIONAL_MANUSCRIPT_IDS,
    DOCMAP_EVALUATION_TYPE_FOR_REPLY,
    DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY,
    DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE,
    get_docmap_item_for_query_result_item,
    DocmapsProvider,
    DOCMAPS_JSONLD_SCHEMA_URL,
    DOCMAP_ID_PREFIX,
    generate_docmap_steps,
    get_docmap_evaluation_type_form_tags
)


MANUSCRIPT_ID_1 = 'manuscript_id_1'

DOI_1 = '10.1101.test/doi1'

PREPRINT_VERSION_1 = '10'
PREPRINT_VERSION_2 = '11'
PREPRINT_VERSION_3 = '12'

PREPRINT_LINK_PREFIX = 'https://test-preprints/'
PREPRINT_LINK_1_PREFIX = f'{PREPRINT_LINK_PREFIX}{DOI_1}'
PREPRINT_LINK_1 = f'{PREPRINT_LINK_1_PREFIX}v{PREPRINT_VERSION_1}'
PREPRINT_LINK_2 = f'{PREPRINT_LINK_1_PREFIX}v{PREPRINT_VERSION_2}'
PREPRINT_LINK_3 = f'{PREPRINT_LINK_1_PREFIX}v{PREPRINT_VERSION_3}'

ELIFE_DOI_1 = 'elife_doi_1'

ELIFE_DOI_VERSION_STR_1 = 'elife_doi_version_str_1'
ELIFE_DOI_VERSION_STR_2 = 'elife_doi_version_str_2'
ELIFE_DOI_VERSION_STR_3 = 'elife_doi_version_str_3'

TDM_PATH_1 = 'tdm_path_1'
TDM_PATH_2 = 'tdm_path_2'
TDM_PATH_3 = 'tdm_path_3'

PREPRINT_DETAILS_1 = {
    'preprint_url': PREPRINT_LINK_1,
    'elife_doi_version_str': ELIFE_DOI_VERSION_STR_1,
    'preprint_doi': DOI_1,
    'preprint_version': PREPRINT_VERSION_1,
    'preprint_published_at_date': date.fromisoformat('2021-01-01'),
    'tdm_path': TDM_PATH_1
}

PREPRINT_DETAILS_2 = {
    'preprint_url': PREPRINT_LINK_2,
    'elife_doi_version_str': ELIFE_DOI_VERSION_STR_2,
    'preprint_doi': DOI_1,
    'preprint_version': PREPRINT_VERSION_2,
    'preprint_published_at_date': date.fromisoformat('2021-02-01'),
    'tdm_path': TDM_PATH_2
}

PREPRINT_DETAILS_3 = {
    'preprint_url': PREPRINT_LINK_3,
    'elife_doi_version_str': ELIFE_DOI_VERSION_STR_3,
    'preprint_doi': DOI_1,
    'preprint_version': PREPRINT_VERSION_3,
    'preprint_published_at_date': date.fromisoformat('2021-03-01'),
    'tdm_path': TDM_PATH_3
}

DOCMAPS_QUERY_RESULT_ITEM_1: dict = {
    'manuscript_id': 'manuscript_id_1',
    'qc_complete_timestamp': datetime.fromisoformat('2022-01-01T01:02:03+00:00'),
    'under_review_timestamp': datetime.fromisoformat('2022-02-01T01:02:03+00:00'),
    'publisher_json': '{"id": "publisher_1"}',
    'elife_doi': ELIFE_DOI_1,
    'license': 'license_1',
    'editor_details': [],
    'senior_editor_details': [],
    'evaluations': [],
    'preprints': [PREPRINT_DETAILS_1],
}

HYPOTHESIS_ID_1 = 'hypothesis_1'
HYPOTHESIS_ID_2 = 'hypothesis_2'
HYPOTHESIS_ID_3 = 'hypothesis_3'

EVALUATION_SUFFIX_1 = 'evaluation_suffix_1'
EVALUATION_SUFFIX_2 = 'evaluation_suffix_2'
EVALUATION_SUFFIX_3 = 'evaluation_suffix_3'

ANNOTATION_CREATED_TIMESTAMP_1 = 'annotation_created_timestamp_1'
ANNOTATION_CREATED_TIMESTAMP_2 = 'annotation_created_timestamp_2'
ANNOTATION_CREATED_TIMESTAMP_3 = 'annotation_created_timestamp_3'

DOCMAPS_QUERY_RESULT_EVALUATION_1 = {
    'hypothesis_id': HYPOTHESIS_ID_1,
    'annotation_created_timestamp': ANNOTATION_CREATED_TIMESTAMP_1,
    'tags': [],
    'uri': PREPRINT_LINK_1,
    'source_version': PREPRINT_VERSION_1,
    'evaluation_suffix': EVALUATION_SUFFIX_1
}

DOCMAPS_QUERY_RESULT_EVALUATION_2 = {
    'hypothesis_id': HYPOTHESIS_ID_2,
    'annotation_created_timestamp': ANNOTATION_CREATED_TIMESTAMP_2,
    'tags': [],
    'uri': PREPRINT_LINK_2,
    'source_version': PREPRINT_VERSION_2,
    'evaluation_suffix': EVALUATION_SUFFIX_2
}

DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATIONS = {
    **DOCMAPS_QUERY_RESULT_ITEM_1,
    'evaluations': [DOCMAPS_QUERY_RESULT_EVALUATION_1]
}

DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT: dict = {
    'manuscript_id': 'manuscript_id_1',
    'qc_complete_timestamp': datetime.fromisoformat('2022-01-01T01:02:03+00:00'),
    'under_review_timestamp': datetime.fromisoformat('2022-02-01T01:02:03+00:00'),
    'publisher_json': '{"id": "publisher_1"}',
    'elife_doi': ELIFE_DOI_1,
    'license': 'license_1',
    'editor_details': [],
    'senior_editor_details': [],
    'evaluations': [DOCMAPS_QUERY_RESULT_EVALUATION_1, DOCMAPS_QUERY_RESULT_EVALUATION_2],
    'preprints': [PREPRINT_DETAILS_1, PREPRINT_DETAILS_2],
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


class TestGetElifeVersionDoi:
    def test_should_return_doi_with_version_when_the_version_defined(self):
        elife_doi = 'elife_doi_1'
        elife_doi_version_str = 'elife_doi_version_str_1'
        actual_result = get_elife_manuscript_version_doi(
            elife_doi=elife_doi,
            elife_doi_version_str=elife_doi_version_str
        )
        assert actual_result == 'elife_doi_1.elife_doi_version_str_1'

    def test_should_return_doi_without_version_when_the_doi_not_defined(self):
        elife_doi = ''
        elife_doi_version_str = 'elife_doi_version_str_1'
        actual_result = get_elife_manuscript_version_doi(
            elife_doi=elife_doi,
            elife_doi_version_str=elife_doi_version_str
        )
        assert not actual_result


class TestGetEvaluationsTypeFromTags:
    def test_should_return_evaluation_summary_when_summary_exist_in_tags_list(self):
        tag_list_with_summary = ['PeerReview', 'evaluationSummary']
        actual_result = get_docmap_evaluation_type_form_tags(tag_list_with_summary)
        assert actual_result == DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY

    def test_should_return_review_article_when_review_keyword_exists_in_tags_list(self):
        tag_list_with_summary = ['PeerReview']
        actual_result = get_docmap_evaluation_type_form_tags(tag_list_with_summary)
        assert actual_result == DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE

    def test_should_return_review_article_for_review_keyword_even_there_is_undefined_tag(self):
        tag_list_with_summary = ['PeerReview', 'undefinedTag']
        actual_result = get_docmap_evaluation_type_form_tags(tag_list_with_summary)
        assert actual_result == DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE

    def test_should_return_reply_when_author_response_keyword_exists_in_tags_list(self):
        tag_list_with_summary = ['AuthorResponse']
        actual_result = get_docmap_evaluation_type_form_tags(tag_list_with_summary)
        assert actual_result == DOCMAP_EVALUATION_TYPE_FOR_REPLY

    def test_should_return_reply_when_author_response_even_there_is_review_tag(self):
        tag_list_with_summary = ['PeerReview', 'AuthorResponse']
        actual_result = get_docmap_evaluation_type_form_tags(tag_list_with_summary)
        assert actual_result == DOCMAP_EVALUATION_TYPE_FOR_REPLY

    def test_should_return_none_when_empty_tags_list(self):
        tag_list_with_summary = []
        actual_result = get_docmap_evaluation_type_form_tags(tag_list_with_summary)
        assert not actual_result

    def test_should_return_none_when_there_is_not_any_defined_tag_in_tags_list(self):
        tag_list_with_summary = ['undefinedTag']
        actual_result = get_docmap_evaluation_type_form_tags(tag_list_with_summary)
        assert not actual_result

    def test_should_raise_error_when_summary_and_author_response_in_tag_list_at_same_time(self):
        tag_list_with_summary = ['PeerReview', 'evaluationSummary', 'AuthorResponse']
        with pytest.raises(AssertionError):
            get_docmap_evaluation_type_form_tags(tag_list_with_summary)


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

    def test_should_add_prefix_and_url_encode_manuscript_id_to_id(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        id_query_param = {'manuscript_id': DOCMAPS_QUERY_RESULT_ITEM_1['manuscript_id']}
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
            'item': get_docmap_preprint_assertion_item(preprint=PREPRINT_DETAILS_1),
            'status': 'manuscript-published'
        }]

    def test_should_populate_actions_outputs_with_doi_and_url_manuscript_published_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        manuscript_published_step = docmaps_item['steps']['_:b0']
        assert manuscript_published_step['actions'] == [{
            'participants': [],
            'outputs': [get_docmap_preprint_output(preprint=PREPRINT_DETAILS_1)]
        }]

    def test_should_set_published_to_none_if_unknown(self):
        docmaps_item = get_docmap_item_for_query_result_item({
            **DOCMAPS_QUERY_RESULT_ITEM_1,
            'preprints': [{
                **PREPRINT_DETAILS_1,
                'preprint_published_at_date': None
            }]
        })
        manuscript_published_step = docmaps_item['steps']['_:b0']
        assert not manuscript_published_step['actions'][0]['outputs'][0].get('published')

    def test_should_populate_inputs_under_review_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        under_review_step = docmaps_item['steps']['_:b1']
        assert under_review_step['inputs'] == [
            get_docmap_preprint_input(preprint=PREPRINT_DETAILS_1)
        ]

    def test_should_populate_assertions_under_review_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        under_review_step = docmaps_item['steps']['_:b1']
        assert under_review_step['assertions'] == [
            {
                'item': get_docmap_preprint_assertion_item(preprint=PREPRINT_DETAILS_1),
                'status': 'under-review',
                'happened': datetime.fromisoformat('2022-02-01T01:02:03+00:00')
            },
            {
                'item': get_docmap_elife_manuscript_doi_assertion_item(
                    query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
                    preprint=PREPRINT_DETAILS_1
                ),
                'status': 'draft'
            }
        ]

    def test_should_populate_actions_outputs_with_doi_and_url_under_review_step_with_license(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        under_review_step = docmaps_item['steps']['_:b1']
        assert under_review_step['actions'] == [{
            'participants': [],
            'outputs': [get_docmap_elife_manuscript_output(
                query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
                preprint=PREPRINT_DETAILS_1
            )]
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
        assert peer_reviewed_step['inputs'] == [
            get_docmap_preprint_input(preprint=PREPRINT_DETAILS_1)
        ]

    def test_should_filter_evaluations_by_preprint_link(self):
        expected_hypothesis_ids_of_first_version = {HYPOTHESIS_ID_1, HYPOTHESIS_ID_2}
        evaluations_of_first_version = [{
            **DOCMAPS_QUERY_RESULT_EVALUATION_1,
            'hypothesis_id': HYPOTHESIS_ID_1,
            'tags': ['PeerReview'],
            'uri': f'{PREPRINT_LINK_PREFIX}{DOI_1}v{PREPRINT_VERSION_1}',
            'source_version': PREPRINT_VERSION_1,
            'evaluation_suffix': EVALUATION_SUFFIX_1
        }, {
            **DOCMAPS_QUERY_RESULT_EVALUATION_1,
            'hypothesis_id': HYPOTHESIS_ID_2,
            'tags': ['PeerReview'],
            'uri': f'{PREPRINT_LINK_PREFIX}{DOI_1}v{PREPRINT_VERSION_1}',
            'source_version': PREPRINT_VERSION_1,
            'evaluation_suffix': EVALUATION_SUFFIX_2
        }]
        evaluations_of_other_version = [{
            **DOCMAPS_QUERY_RESULT_EVALUATION_1,
            'hypothesis_id': HYPOTHESIS_ID_3,
            'tags': ['PeerReview'],
            'uri': f'{PREPRINT_LINK_PREFIX}{DOI_1}v{PREPRINT_VERSION_2}',
            'source_version': PREPRINT_VERSION_2,
            'evaluation_suffix': EVALUATION_SUFFIX_1
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
        assert peer_reviewed_step['inputs'] == [
            get_docmap_preprint_input(preprint=PREPRINT_DETAILS_1)
        ]
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
            'item': get_docmap_preprint_assertion_item(preprint=PREPRINT_DETAILS_1),
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
                    'tags': ['PeerReview'],
                }, {
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'hypothesis_id': HYPOTHESIS_ID_2,
                    'annotation_created_timestamp': ANNOTATION_CREATED_TIMESTAMP_2,
                    'tags': ['PeerReview', 'evaluationSummary'],
                    'evaluation_suffix': EVALUATION_SUFFIX_2
                }, {
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'hypothesis_id': HYPOTHESIS_ID_3,
                    'annotation_created_timestamp': ANNOTATION_CREATED_TIMESTAMP_3,
                    'tags': ['PeerReview', 'AuthorResponse'],
                    'evaluation_suffix': EVALUATION_SUFFIX_3
                }]
            }
        )
        docmaps_item = get_docmap_item_for_query_result_item(
            query_result_with_evaluation
        )
        peer_reviewed_step = docmaps_item['steps']['_:b2']
        peer_reviewed_actions = peer_reviewed_step['actions']
        assert len(peer_reviewed_actions) == 3
        assert peer_reviewed_actions[0]['outputs'][0] == get_docmap_evaluation_output(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            preprint=PREPRINT_DETAILS_1,
            hypothesis_id=HYPOTHESIS_ID_1,
            evaluation_suffix=EVALUATION_SUFFIX_1,
            annotation_created_timestamp=ANNOTATION_CREATED_TIMESTAMP_1,
            docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE
        )
        assert peer_reviewed_actions[1]['outputs'][0] == get_docmap_evaluation_output(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            preprint=PREPRINT_DETAILS_1,
            hypothesis_id=HYPOTHESIS_ID_2,
            evaluation_suffix=EVALUATION_SUFFIX_2,
            annotation_created_timestamp=ANNOTATION_CREATED_TIMESTAMP_2,
            docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY
        )
        assert peer_reviewed_actions[2]['outputs'][0] == get_docmap_evaluation_output(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            preprint=PREPRINT_DETAILS_1,
            hypothesis_id=HYPOTHESIS_ID_3,
            evaluation_suffix=EVALUATION_SUFFIX_3,
            annotation_created_timestamp=ANNOTATION_CREATED_TIMESTAMP_3,
            docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_REPLY
        )

    def test_should_populate_outputs_type_according_to_tags_peer_reviewed_step(self):
        query_result_with_evaluation = dict(
            DOCMAPS_QUERY_RESULT_ITEM_1,
            **{
                'evaluations': [{
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'tags': ['PeerReview']
                }, {
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'tags': ['PeerReview', 'evaluationSummary']
                }, {
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
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
        assert outputs_for_index_0['type'] == DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE
        assert outputs_for_index_1['type'] == DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY
        assert outputs_for_index_2['type'] == DOCMAP_EVALUATION_TYPE_FOR_REPLY

    def test_should_populate_participants_in_peer_reviewed_step_for_review_article_type(self):
        query_result_with_evaluation = dict(
            DOCMAPS_QUERY_RESULT_ITEM_1,
            **{
                'evaluations': [{
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
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

    def test_should_return_empty_list_for_inputs_manuscript_published_step_for_revised_pp(self):
        docmaps_item = get_docmap_item_for_query_result_item(
            DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT
        )
        manuscript_published_step = docmaps_item['steps']['_:b3']
        assert manuscript_published_step['inputs'] == []

    def test_should_populate_assertions_manuscript_published_step_for_revised_pp(self):
        docmaps_item = get_docmap_item_for_query_result_item(
            DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT
        )
        manuscript_published_step = docmaps_item['steps']['_:b3']
        assert manuscript_published_step['assertions'] == [{
            'item': get_docmap_preprint_assertion_item(preprint=PREPRINT_DETAILS_2),
            'status': 'manuscript-published'
        }]

    def test_should_populate_actions_outputs_manuscript_published_step_for_revised_pp(self):
        docmaps_item = get_docmap_item_for_query_result_item(
            DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT
        )
        manuscript_published_step = docmaps_item['steps']['_:b3']
        assert manuscript_published_step['actions'] == [{
            'participants': [],
            'outputs': [get_docmap_preprint_output(preprint=PREPRINT_DETAILS_2)]
        }]

    def test_should_populate_inputs_revised_step_with_one_evaluation(self):
        docmaps_item = get_docmap_item_for_query_result_item({
            **DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT,
            'evaluations': [{
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'elife_doi_version_str': ELIFE_DOI_VERSION_STR_1,
                    'evaluation_suffix': 'sa1',
                    'tags': ['PeerReview']
                }]
        })
        revised_step = docmaps_item['steps']['_:b4']
        assert revised_step['inputs'] == [
            get_docmap_preprint_input(preprint=PREPRINT_DETAILS_2),
            {
                'type': DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE,
                'doi': f'{ELIFE_DOI_1}.{ELIFE_DOI_VERSION_STR_1}.sa1'
            }
        ]

    def test_should_populate_inputs_revised_step_with_more_then_one_evaluation(self):
        docmaps_item = get_docmap_item_for_query_result_item({
            **DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT,
            'evaluations': [{
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'elife_doi_version_str': ELIFE_DOI_VERSION_STR_1,
                    'evaluation_suffix': 'sa1',
                    'tags': ['PeerReview']
                },
                {
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'elife_doi_version_str': ELIFE_DOI_VERSION_STR_1,
                    'evaluation_suffix': 'sa2',
                    'tags': ['evaluationSummary']
                }]
        })
        revised_step = docmaps_item['steps']['_:b4']
        assert revised_step['inputs'] == [
            get_docmap_preprint_input(preprint=PREPRINT_DETAILS_2),
            {
                'type': DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE,
                'doi': f'{ELIFE_DOI_1}.{ELIFE_DOI_VERSION_STR_1}.sa1'
            },
            {
                'type': DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY,
                'doi': f'{ELIFE_DOI_1}.{ELIFE_DOI_VERSION_STR_1}.sa2'
            }
        ]

    def test_should_not_add_revised_pp_evaluations_to_inputs_of_revised_pp_step(self):
        docmaps_item = get_docmap_item_for_query_result_item({
            **DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT,
            'evaluations': [{
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'elife_doi_version_str': ELIFE_DOI_VERSION_STR_1,
                    'evaluation_suffix': 'sa1',
                    'tags': ['PeerReview']
                },
                {
                    **DOCMAPS_QUERY_RESULT_EVALUATION_2,
                    'elife_doi_version_str': ELIFE_DOI_VERSION_STR_2,
                    'evaluation_suffix': 'sa1',
                    'tags': ['PeerReview']
                }]
        })
        revised_step = docmaps_item['steps']['_:b4']
        assert revised_step['inputs'] == [
            get_docmap_preprint_input(preprint=PREPRINT_DETAILS_2),
            {
                'type': DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE,
                'doi': f'{ELIFE_DOI_1}.{ELIFE_DOI_VERSION_STR_1}.sa1'
            }
        ]

    def test_should_populate_assertions_revised_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(
            DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT
        )
        revised_step = docmaps_item['steps']['_:b4']
        assert revised_step['assertions'] == [{
            'item': get_docmap_elife_manuscript_doi_assertion_item(
                query_result_item=DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT,
                preprint=PREPRINT_DETAILS_2
            ),
            'status': 'revised'
        }]

    def test_should_populate_actions_revised_step(self):
        docmaps_item = get_docmap_item_for_query_result_item({
            **DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT,
            'evaluations': [{
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'tags': ['PeerReview']
                },
                {
                    **DOCMAPS_QUERY_RESULT_EVALUATION_2,
                    'tags': ['PeerReview']
                },
                {
                    **DOCMAPS_QUERY_RESULT_EVALUATION_2,
                    'evaluation_suffix': EVALUATION_SUFFIX_3,
                    'hypothesis_id': HYPOTHESIS_ID_3,
                    'annotation_created_timestamp': ANNOTATION_CREATED_TIMESTAMP_3,
                    'tags': ['evaluationSummary']
                }]
        })
        revised_step = docmaps_item['steps']['_:b4']
        assert revised_step['actions'][0]['outputs'][0] == get_docmap_elife_manuscript_output(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            preprint=PREPRINT_DETAILS_2
        )
        assert revised_step['actions'][1]['outputs'] == [get_docmap_evaluation_output(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT,
            preprint=PREPRINT_DETAILS_2,
            hypothesis_id=HYPOTHESIS_ID_2,
            evaluation_suffix=EVALUATION_SUFFIX_2,
            annotation_created_timestamp=ANNOTATION_CREATED_TIMESTAMP_2,
            docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE
        )]
        assert revised_step['actions'][2]['outputs'] == [get_docmap_evaluation_output(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT,
            preprint=PREPRINT_DETAILS_2,
            hypothesis_id=HYPOTHESIS_ID_3,
            evaluation_suffix=EVALUATION_SUFFIX_3,
            annotation_created_timestamp=ANNOTATION_CREATED_TIMESTAMP_3,
            docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY
        )]

    def test_should_add_second_manuscript_published_and_revised_step_for_third_preprint_version(
        self
    ):
        docmaps_item = get_docmap_item_for_query_result_item({
            **DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT,
            'preprints': [PREPRINT_DETAILS_1, PREPRINT_DETAILS_2, PREPRINT_DETAILS_3]
        })
        second_manuscript_published_step = docmaps_item['steps']['_:b5']
        second_revised_step = docmaps_item['steps']['_:b6']
        assert second_revised_step['assertions'] == [{
            'item': get_docmap_elife_manuscript_doi_assertion_item(
                query_result_item=DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT,
                preprint=PREPRINT_DETAILS_3
            ),
            'status': 'revised'
        }]
        assert second_manuscript_published_step['assertions'] == [{
            'item': get_docmap_preprint_assertion_item(preprint=PREPRINT_DETAILS_3),
            'status': 'manuscript-published'
        }]


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
            additionally_include_manuscript_ids=[]
        )
        assert provider.docmaps_index_query.rstrip().endswith(
            'WHERE is_reviewed_preprint_type AND is_or_was_under_review'
        )

    def test_should_add_additional_manuscript_ids_to_query_filter(
        self
    ):
        provider = DocmapsProvider(
            only_include_reviewed_preprint_type=True,
            only_include_evaluated_preprints=False,
            additionally_include_manuscript_ids=ADDITIONAL_MANUSCRIPT_IDS
        )
        assert provider.docmaps_index_query.rstrip().endswith(
            f'OR result.manuscript_id IN {ADDITIONAL_MANUSCRIPT_IDS}'
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
