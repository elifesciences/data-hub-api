import urllib

import pytest
from data_hub_api.kotahi_docmaps.v1.codecs.elife_manuscript import (
    get_docmap_elife_manuscript_doi_assertion_item,
    get_docmap_elife_manuscript_output,
    get_elife_manuscript_version_doi
)
from data_hub_api.kotahi_docmaps.v1.codecs.evaluation import (
    DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY,
    DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE,
    get_docmap_evaluation_output,
    get_docmap_evaluation_participants_for_evalution_summary_type,
    get_docmap_evaluation_participants_for_review_article_type
)

from data_hub_api.kotahi_docmaps.v1.codecs.preprint import (
    get_docmap_preprint_assertion_item,
    get_docmap_preprint_input,
    get_docmap_preprint_input_with_published
)

from data_hub_api.kotahi_docmaps.v1.codecs.docmaps import (
    get_docmap_actions_for_under_review_step,
    get_docmap_assertions_for_under_review_step,
    get_docmap_item_for_query_result_item,
    DOCMAPS_JSONLD_SCHEMA_URL,
    DOCMAP_ID_PREFIX,
    generate_docmap_steps,
)
from tests.unit_tests.docmaps.v2.test_data import SENIOR_EDITOR_DETAIL_1

from tests.unit_tests.kotahi_docmaps.v1.test_data import (
    DOCMAPS_QUERY_RESULT_ITEM_1,
    DOCMAPS_QUERY_RESULT_ITEM_2,
    DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATION_EMAILS_1,
    EDITOR_DETAIL_1,
    EMAIL_BODY_1,
    EMAIL_BODY_WITH_ELIFE_ASSESSMENT_1,
    EMAIL_BODY_WITH_PUBLIC_REVIEWS_1,
    MANUSCRIPT_VERSION_1,
    MANUSCRIPT_VERSION_2,
    MANUSCRIPT_VERSION_WITH_ELIFE_ASSESSMENT_AND_PUBLIC_REVIEWS_1,
    MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_1,
    MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_2,
    PUBLISHER_DICT_1
)


class TestGetElifeVersionDoi:
    def test_should_return_doi_with_version_when_the_version_defined(self):
        elife_doi = 'elife_doi_1'
        elife_doi_version_str = 'elife_doi_version_str_1'
        actual_result = get_elife_manuscript_version_doi(
            elife_doi=elife_doi,
            elife_doi_version_str=elife_doi_version_str
        )
        assert actual_result == 'elife_doi_1.elife_doi_version_str_1'


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

    def test_should_populate_create_and_updated_timestamp_with_first_qc_complete_timestamp(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_2)
        assert docmaps_item['created'] == (
            MANUSCRIPT_VERSION_1['qc_complete_timestamp'].isoformat()
        )
        assert docmaps_item['updated'] == docmaps_item['created']

    def test_should_parse_and_include_publisher_json(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        assert docmaps_item['publisher'] == PUBLISHER_DICT_1

    def test_should_populate_inputs_for_first_under_review_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_2)
        under_review_step = docmaps_item['steps']['_:b0']
        assert under_review_step['inputs'] == [
            get_docmap_preprint_input_with_published(
                manuscript_version=MANUSCRIPT_VERSION_1
            )
        ]

    def test_should_populate_assertions_for_first_under_review_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        under_review_step = docmaps_item['steps']['_:b0']
        assert under_review_step['assertions'] == [
            {
                'item': get_docmap_preprint_assertion_item(manuscript_version=MANUSCRIPT_VERSION_1),
                'status': 'under-review',
                'happened': '2022-02-01T01:02:03+00:00'
            },
            {
                'item': get_docmap_elife_manuscript_doi_assertion_item(
                    query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
                    manuscript_version=MANUSCRIPT_VERSION_1
                ),
                'status': 'draft'
            }
        ]

    def test_should_populate_actions_outputs_for_first_under_review_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(DOCMAPS_QUERY_RESULT_ITEM_1)
        under_review_step = docmaps_item['steps']['_:b0']
        assert under_review_step['actions'] == [{
            'participants': [],
            'outputs': [get_docmap_elife_manuscript_output(
                query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
                manuscript_version=MANUSCRIPT_VERSION_1
            )]
        }]

    def test_should_populate_assertions_peer_reviewed_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(
            DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATION_EMAILS_1
        )
        peer_reviewed_step = docmaps_item['steps']['_:b1']
        assert peer_reviewed_step['assertions'] == [{
            'item': get_docmap_preprint_assertion_item(
                manuscript_version=MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_1
            ),
            'status': 'peer-reviewed'
        }]

    def test_should_populate_inputs_peer_reviewed_step(self):
        docmaps_item = get_docmap_item_for_query_result_item(
            DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATION_EMAILS_1
        )
        peer_reviewed_step = docmaps_item['steps']['_:b1']
        assert peer_reviewed_step['inputs'] == [
            get_docmap_preprint_input(
                manuscript_version=MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_1
            )
        ]

    def test_should_not_populate_actions_peer_reviewed_step_if_no_evaluations_in_email_body(self):
        query_result_with_evaluation = {
            **DOCMAPS_QUERY_RESULT_ITEM_1,
            'manuscript_versions': [{
                **MANUSCRIPT_VERSION_1,
                'email_body': EMAIL_BODY_1
            }]
        }
        docmaps_item = get_docmap_item_for_query_result_item(
            query_result_with_evaluation
        )
        peer_reviewed_step = docmaps_item['steps']['_:b1']
        peer_reviewed_actions = peer_reviewed_step['actions']
        assert not peer_reviewed_actions

    def test_should_not_have_peer_reviewed_step_if_there_is_no_email_body(self):
        query_result_with_evaluation = DOCMAPS_QUERY_RESULT_ITEM_1
        docmaps_item = get_docmap_item_for_query_result_item(
            query_result_with_evaluation
        )
        assert '_b1' not in docmaps_item['steps']

    def test_should_populate_actions_outputs_peer_reviewed_step_for_each_evaluation(self):
        query_result_with_evaluation = {
            **DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATION_EMAILS_1,
            'manuscript_versions': [MANUSCRIPT_VERSION_WITH_ELIFE_ASSESSMENT_AND_PUBLIC_REVIEWS_1]
        }
        docmaps_item = get_docmap_item_for_query_result_item(
            query_result_with_evaluation
        )
        peer_reviewed_step = docmaps_item['steps']['_:b1']
        peer_reviewed_actions = peer_reviewed_step['actions']
        assert len(peer_reviewed_actions) > 0
        assert peer_reviewed_actions[0]['outputs'][0] == get_docmap_evaluation_output(
            docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY
        )
        assert peer_reviewed_actions[1]['outputs'][0] == get_docmap_evaluation_output(
            docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE
        )

    def test_should_populate_participants_peer_reviewed_step_for_review_article_type(self):
        query_result_with_evaluation = {
            **DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATION_EMAILS_1,
            'manuscript_versions': [{
                **MANUSCRIPT_VERSION_1,
                'email_body': EMAIL_BODY_WITH_PUBLIC_REVIEWS_1
            }]
        }
        docmaps_item = get_docmap_item_for_query_result_item(
            query_result_with_evaluation
        )
        peer_reviewed_step = docmaps_item['steps']['_:b1']
        peer_reviewed_actions = peer_reviewed_step['actions']
        participants_for_review_article = peer_reviewed_actions[0]['participants']
        assert participants_for_review_article == (
            get_docmap_evaluation_participants_for_review_article_type()
        )

    def test_should_populate_participants_peer_reviewed_step_for_evaluation_summary_type(self):
        editor_details = [EDITOR_DETAIL_1]
        senior_editor_details = [SENIOR_EDITOR_DETAIL_1]
        query_result_with_evaluation_and_editor_details = {
            **DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATION_EMAILS_1,
            'manuscript_versions': [{
                **MANUSCRIPT_VERSION_1,
                'email_body': EMAIL_BODY_WITH_ELIFE_ASSESSMENT_1,
                'editor_details': editor_details,
                'senior_editor_details': senior_editor_details
            }]
        }
        docmaps_item = get_docmap_item_for_query_result_item(
            query_result_with_evaluation_and_editor_details
        )
        peer_reviewed_step = docmaps_item['steps']['_:b1']
        peer_reviewed_actions = peer_reviewed_step['actions']
        participants_for_evaluation_summary = peer_reviewed_actions[0]['participants']
        assert participants_for_evaluation_summary == (
            get_docmap_evaluation_participants_for_evalution_summary_type(
                editor_details_list=editor_details,
                senior_editor_details_list=senior_editor_details
            )
        )

    def test_should_populate_inputs_for_second_under_review_step(self):
        query_result_item = {
            **DOCMAPS_QUERY_RESULT_ITEM_1,
            'manuscript_versions': [
                MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_1,
                MANUSCRIPT_VERSION_2
            ]
        }
        docmaps_item = get_docmap_item_for_query_result_item(query_result_item)
        under_review_step = docmaps_item['steps']['_:b2']
        assert under_review_step['inputs'] == [
            get_docmap_preprint_input_with_published(
                manuscript_version=MANUSCRIPT_VERSION_2
            )
        ]

    def test_should_populate_actions_for_second_under_review_step(self):
        query_result_item = {
            **DOCMAPS_QUERY_RESULT_ITEM_1,
            'manuscript_versions': [
                MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_1,
                MANUSCRIPT_VERSION_2
            ]
        }
        docmaps_item = get_docmap_item_for_query_result_item(query_result_item)
        under_review_step = docmaps_item['steps']['_:b2']
        assert under_review_step['actions'] == (
            get_docmap_actions_for_under_review_step(query_result_item, MANUSCRIPT_VERSION_2)
        )

    def test_should_populate_assertions_for_second_under_review_step(self):
        query_result_item = {
            **DOCMAPS_QUERY_RESULT_ITEM_1,
            'manuscript_versions': [
                MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_1,
                MANUSCRIPT_VERSION_2
            ]
        }
        docmaps_item = get_docmap_item_for_query_result_item(query_result_item)
        under_review_step = docmaps_item['steps']['_:b2']
        assert under_review_step['assertions'] == (
            get_docmap_assertions_for_under_review_step(query_result_item, MANUSCRIPT_VERSION_2)
        )

    def test_should_populate_assertions_revised_step(self):
        query_result_item = {
            **DOCMAPS_QUERY_RESULT_ITEM_1,
            'manuscript_versions': [
                MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_1,
                MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_2
            ]
        }
        docmaps_item = get_docmap_item_for_query_result_item(query_result_item)
        revised_step = docmaps_item['steps']['_:b3']
        assert revised_step['assertions'] == [{
            'item': get_docmap_preprint_assertion_item(MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_2),
            'status': 'revised'
        }]

    def test_should_populate_inputs_revised_step(self):
        query_result_item = {
            **DOCMAPS_QUERY_RESULT_ITEM_1,
            'manuscript_versions': [
                MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_1,
                MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_2
            ]
        }
        docmaps_item = get_docmap_item_for_query_result_item(query_result_item)
        peer_reviewed_step = docmaps_item['steps']['_:b3']
        assert peer_reviewed_step['inputs'] == [
            get_docmap_preprint_input(MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_2)
        ]
