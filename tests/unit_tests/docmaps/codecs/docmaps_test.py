import json
from typing import Iterable
import urllib

import pytest
from data_hub_api.docmaps.codecs.elife_manuscript import (
    get_docmap_elife_manuscript_doi_assertion_item,
    get_docmap_elife_manuscript_output,
    get_elife_manuscript_version_doi
)
from data_hub_api.docmaps.codecs.evaluation import (
    DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY,
    DOCMAP_EVALUATION_TYPE_FOR_REPLY,
    DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE,
    HYPOTHESIS_URL,
    get_docmap_evaluation_input,
    get_docmap_evaluation_output,
    get_docmap_evaluation_participants_for_evalution_summary_type,
    get_docmap_evaluation_participants_for_review_article_type
)

from data_hub_api.docmaps.codecs.preprint import (
    get_docmap_preprint_assertion_item,
    get_docmap_preprint_input,
    get_docmap_preprint_output
)

from data_hub_api.docmaps.codecs.docmaps import (
    get_docmap_item_for_query_result_item,
    DOCMAPS_JSONLD_SCHEMA_URL,
    DOCMAP_ID_PREFIX,
    generate_docmap_steps,
)
from tests.unit_tests.docmaps.test_data import (
    ANNOTATION_CREATED_TIMESTAMP_1,
    ANNOTATION_CREATED_TIMESTAMP_2,
    ANNOTATION_CREATED_TIMESTAMP_3,
    DOCMAPS_QUERY_RESULT_EVALUATION_1,
    DOCMAPS_QUERY_RESULT_EVALUATION_2,
    DOCMAPS_QUERY_RESULT_ITEM_1,
    DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATIONS,
    DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT,
    DOI_1,
    EDITOR_DETAIL_1,
    EVALUATION_SUFFIX_1,
    EVALUATION_SUFFIX_2,
    EVALUATION_SUFFIX_3,
    HYPOTHESIS_ID_1,
    HYPOTHESIS_ID_2,
    HYPOTHESIS_ID_3,
    PREPRINT_DETAILS_1,
    PREPRINT_DETAILS_2,
    PREPRINT_DETAILS_3,
    PREPRINT_LINK_1,
    PREPRINT_LINK_PREFIX,
    PREPRINT_VERSION_1,
    PREPRINT_VERSION_2,
    SENIOR_EDITOR_DETAIL_1
)


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
        assert docmaps_item['publisher'] == json.loads(json.dumps(
            DOCMAPS_QUERY_RESULT_ITEM_1['publisher_json']
        ))

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

    def test_should_populate_actions_outputs_manuscript_published_step(self):
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
                'happened': '2022-02-01 01:02:03+00:00'
            },
            {
                'item': get_docmap_elife_manuscript_doi_assertion_item(
                    query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
                    preprint=PREPRINT_DETAILS_1
                ),
                'status': 'draft'
            }
        ]

    def test_should_populate_actions_outputs_under_review_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        under_review_step = docmaps_item['steps']['_:b1']
        assert under_review_step['actions'] == [{
            'participants': [],
            'outputs': [get_docmap_elife_manuscript_output(
                query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
                preprint=PREPRINT_DETAILS_1
            )]
        }]

    def test_should_populate_inputs_peer_reviewed_step(self):
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

    def test_should_not_populate_actions_peer_reviewed_step_if_tags_are_empty(self):
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

    def test_should_populate_outputs_evaluation_type_according_to_tags_peer_reviewed_step(self):
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

    def test_should_populate_participants_peer_reviewed_step_for_review_article_type(self):
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
        assert participants_for_review_article == (
            get_docmap_evaluation_participants_for_review_article_type()
        )

    def test_should_populate_participants_peer_reviewed_step_for_evaluation_summary_type(self):
        query_result_with_evaluation = dict(
            DOCMAPS_QUERY_RESULT_ITEM_1,
            **{
                'evaluations': [{
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'tags': ['PeerReview', 'evaluationSummary']
                }]
            }
        )
        editor_details = [EDITOR_DETAIL_1]
        senior_editor_details = [SENIOR_EDITOR_DETAIL_1]
        query_result_with_editor_details = dict(
            query_result_with_evaluation,
            **{
                'editor_details': editor_details,
                'senior_editor_details': senior_editor_details
            }
        )
        docmaps_item = get_docmap_item_for_query_result_item(
            query_result_with_editor_details
        )
        peer_reviewed_step = docmaps_item['steps']['_:b2']
        peer_reviewed_actions = peer_reviewed_step['actions']
        participants_for_evaluation_summary = peer_reviewed_actions[0]['participants']
        assert participants_for_evaluation_summary == (
            get_docmap_evaluation_participants_for_evalution_summary_type(
                editor_details_list=editor_details,
                senior_editor_details_list=senior_editor_details
            )
        )

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

    def test_should_populate_inputs_revised_step_with_more_than_one_evaluation(self):
        docmaps_item = get_docmap_item_for_query_result_item({
            **DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT,
            'evaluations': [{
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'tags': ['PeerReview']
                },
                {
                    **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                    'evaluation_suffix': EVALUATION_SUFFIX_2,
                    'tags': ['evaluationSummary']
                }]
        })
        revised_step = docmaps_item['steps']['_:b4']
        assert revised_step['inputs'] == [
            get_docmap_preprint_input(preprint=PREPRINT_DETAILS_2),
            get_docmap_evaluation_input(
                query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
                preprint=PREPRINT_DETAILS_1,
                evaluation_suffix=EVALUATION_SUFFIX_1,
                docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE
            ),
            get_docmap_evaluation_input(
                query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
                preprint=PREPRINT_DETAILS_1,
                evaluation_suffix=EVALUATION_SUFFIX_2,
                docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY
            )
        ]

    def test_should_not_add_revised_pp_evaluations_to_inputs_of_revised_pp_step(self):
        docmaps_item = get_docmap_item_for_query_result_item({
            **DOCMAPS_QUERY_RESULT_ITEM_WITH_REVISED_PREPRPINT,
            'evaluations': [{
                **DOCMAPS_QUERY_RESULT_EVALUATION_1,
                'tags': ['PeerReview']
            }],
            'preprints': [PREPRINT_DETAILS_1, PREPRINT_DETAILS_2]
        })
        revised_step = docmaps_item['steps']['_:b4']
        assert revised_step['inputs'] == [
            get_docmap_preprint_input(preprint=PREPRINT_DETAILS_2),
            get_docmap_evaluation_input(
                query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
                preprint=PREPRINT_DETAILS_1,
                evaluation_suffix=EVALUATION_SUFFIX_1,
                docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE
            )
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
