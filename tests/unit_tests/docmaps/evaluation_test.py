from datetime import datetime
from unittest import mock
from unittest.mock import patch
import pytest
from data_hub_api.docmaps.codecs import evaluation as evaluation_module
from data_hub_api.docmaps.codecs.evaluation import (
    DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY,
    DOCMAP_EVALUATION_TYPE_FOR_REPLY,
    DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE,
    DOI_ROOT_URL,
    HYPOTHESIS_URL,
    SCIETY_ARTICLES_ACTIVITY_URL,
    SCIETY_ARTICLES_EVALUATIONS_URL,
    get_docmap_actions_for_evaluations,
    get_docmap_evaluation_input,
    get_docmap_evaluation_output,
    get_docmap_evaluation_output_content,
    get_docmap_evaluation_output_content_url,
    get_docmap_evaluation_participants,
    get_docmap_evaluation_participants_for_evaluation_summary_type,
    get_docmap_evaluation_participants_for_evalution_summary_type,
    get_docmap_evaluation_type_form_tags,
    get_elife_evaluation_doi,
    get_elife_evaluation_doi_url,
    get_related_organization_detail
)

PREPRINT_DOI_1 = 'preprint_doi_1'
PREPRINT_VERSION_1 = 'preprint_version_1'

ELIFE_DOI_1 = 'elife_doi_1'
ELIFE_DOI_VERSION_STR_1 = 'elife_doi_version_str_1'

LICENSE_1 = 'license_1'

PREPRINT_DETAILS_1 = {
    'preprint_url': 'preprint_url_1',
    'elife_doi_version_str': 'elife_doi_version_str_1',
    'preprint_doi': PREPRINT_DOI_1,
    'preprint_version': PREPRINT_VERSION_1,
    'preprint_published_at_date': datetime.fromisoformat('2021-01-01'),
    'tdm_path': 'tdm_path_1'
}

DOCMAPS_QUERY_RESULT_ITEM_1: dict = {
    'manuscript_id': 'manuscript_id_1',
    'qc_complete_timestamp': datetime.fromisoformat('2022-01-01T01:02:03+00:00'),
    'under_review_timestamp': datetime.fromisoformat('2022-02-01T01:02:03+00:00'),
    'publisher_json': '{"id": "publisher_1"}',
    'elife_doi': 'elife_doi_1',
    'license': 'license_1',
    'editor_details': [],
    'senior_editor_details': [],
    'evaluations': [],
    'preprints': [PREPRINT_DETAILS_1],
}

HYPOTHESIS_ID_1 = 'hypothesis_id_1'
EVALUATION_SUFFIX_1 = 'evaluation_suffix_1'
ANNOTATION_CREATED_TIMESTAMP_1 = 'annotation_created_timestamp_1'

PREPRINT_LINK_PREFIX = 'https://test-preprints/'
PREPRINT_LINK_1_PREFIX = f'{PREPRINT_LINK_PREFIX}{PREPRINT_DOI_1}'
PREPRINT_LINK_1 = f'{PREPRINT_LINK_1_PREFIX}v{PREPRINT_VERSION_1}'

DOCMAPS_QUERY_RESULT_EVALUATION_1 = {
    'hypothesis_id': HYPOTHESIS_ID_1,
    'annotation_created_timestamp': ANNOTATION_CREATED_TIMESTAMP_1,
    'tags': [],
    'uri': PREPRINT_LINK_1,
    'source_version': PREPRINT_VERSION_1,
    'evaluation_suffix': EVALUATION_SUFFIX_1
}


class TestGetElifeEvaluationDoi:
    def test_should_return_evaluation_doi_with_suffix_if_defined(self):
        elife_doi = 'elife_doi_1'
        elife_doi_version_str = 'elife_doi_version_str_1'
        evaluation_suffix = 'evaluation_suffix_1'
        actual_result = get_elife_evaluation_doi(
            elife_doi=elife_doi,
            elife_doi_version_str=elife_doi_version_str,
            evaluation_suffix=evaluation_suffix
        )
        assert actual_result == 'elife_doi_1.elife_doi_version_str_1.evaluation_suffix_1'

    def test_should_return_evaluation_doi_without_suffix_if_not_defined(self):
        elife_doi = 'elife_doi_1'
        elife_doi_version_str = 'elife_doi_version_str_1'
        evaluation_suffix = ''
        actual_result = get_elife_evaluation_doi(
            elife_doi=elife_doi,
            elife_doi_version_str=elife_doi_version_str,
            evaluation_suffix=evaluation_suffix
        )
        assert actual_result == 'elife_doi_1.elife_doi_version_str_1'

    def test_should_return_none_if_elife_doi_not_defined(self):
        elife_doi = ''
        elife_doi_version_str = 'elife_doi_version_str_1'
        evaluation_suffix = ''
        actual_result = get_elife_evaluation_doi(
            elife_doi=elife_doi,
            elife_doi_version_str=elife_doi_version_str,
            evaluation_suffix=evaluation_suffix
        )
        assert not actual_result


class TestGetElifeEvaluationDoiUrl:
    def test_should_return_none_if_elife_doi_is_none(self):
        assert not get_elife_evaluation_doi_url(
            elife_evaluation_doi=None,
        )

    def test_should_return_elife_evaluation_doi_url_when_defined(self):
        result = get_elife_evaluation_doi_url(
            elife_evaluation_doi='elife_evaluation_doi_1',
        )
        assert result == f'{DOI_ROOT_URL}elife_evaluation_doi_1'


class TestGetDocmapEvaluationInput:
    def test_should_populate_evaluation_input(self):
        result = get_docmap_evaluation_input(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            preprint=PREPRINT_DETAILS_1,
            evaluation_suffix=EVALUATION_SUFFIX_1,
            docmap_evaluation_type='docmap_evaluation_type_1'
        )
        assert result == {
            'type': 'docmap_evaluation_type_1',
            'doi': get_elife_evaluation_doi(
                elife_doi=ELIFE_DOI_1,
                elife_doi_version_str=ELIFE_DOI_VERSION_STR_1,
                evaluation_suffix=EVALUATION_SUFFIX_1
            )
        }


class TestGetDocmapEvaluationOutputContentUrl:
    def test_should_raise_error_if_base_url_not_one_expected(self):
        base_url = 'base_url_1'
        hypothesis_id = 'hypothesis_id_1'
        with pytest.raises(AssertionError):
            get_docmap_evaluation_output_content_url(base_url, hypothesis_id)

    def test_should_populate_the_content_url_correctly_per_given_base_url(self):
        hypothesis_id = 'hypothesis_id_1'
        preprint_doi = 'preprint_doi_1'

        result = get_docmap_evaluation_output_content_url(HYPOTHESIS_URL, hypothesis_id)
        assert result == 'https://hypothes.is/a/hypothesis_id_1'

        result = get_docmap_evaluation_output_content_url(
            SCIETY_ARTICLES_ACTIVITY_URL, hypothesis_id, preprint_doi
        )
        assert result == (
            'https://sciety.org/articles/activity/preprint_doi_1#hypothesis:hypothesis_id_1'
        )
        result = get_docmap_evaluation_output_content_url(
            SCIETY_ARTICLES_EVALUATIONS_URL, hypothesis_id
        )
        assert result == 'https://sciety.org/evaluations/hypothesis:hypothesis_id_1/content'

    def test_should_raise_error_with_activity_url_if_preprint_doi_not_defined(self):
        hypothesis_id = 'hypothesis_id_1'
        with pytest.raises(AssertionError):
            get_docmap_evaluation_output_content_url(
                base_url=SCIETY_ARTICLES_ACTIVITY_URL,
                hypothesis_id=hypothesis_id,
                preprint_doi=None
            )


class TestGetDocmapEvaluationOutputContent:
    def test_should_populate_evaluation_output_content(self):
        hypothesis_id = 'hypothesis_id_1'
        result = get_docmap_evaluation_output_content(HYPOTHESIS_URL, hypothesis_id)
        assert result == {
            'type': 'web-page',
            'url': 'https://hypothes.is/a/hypothesis_id_1'
        }


class TestGetDocmapEvaluationOutput:
    def test_should_populate_evaluation_output(self):
        result = get_docmap_evaluation_output(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            preprint=PREPRINT_DETAILS_1,
            hypothesis_id=HYPOTHESIS_ID_1,
            evaluation_suffix=EVALUATION_SUFFIX_1,
            annotation_created_timestamp=ANNOTATION_CREATED_TIMESTAMP_1,
            docmap_evaluation_type='docmap_evaluation_type_1'
        )
        elife_evaluation_doi = get_elife_evaluation_doi(
            elife_doi=ELIFE_DOI_1,
            elife_doi_version_str=ELIFE_DOI_VERSION_STR_1,
            evaluation_suffix=EVALUATION_SUFFIX_1
        )
        assert result == {
            'type': 'docmap_evaluation_type_1',
            'published': ANNOTATION_CREATED_TIMESTAMP_1,
            'doi': elife_evaluation_doi,
            'license': LICENSE_1,
            'url': get_elife_evaluation_doi_url(
                elife_evaluation_doi=elife_evaluation_doi,
            ),
            'content': [
                {
                    'type': 'web-page',
                    'url': f'{HYPOTHESIS_URL}{HYPOTHESIS_ID_1}'
                },
                {
                    'type': 'web-page',
                    'url': (
                        f'{SCIETY_ARTICLES_ACTIVITY_URL}'
                        f'{PREPRINT_DOI_1}#hypothesis:{HYPOTHESIS_ID_1}'
                    )
                },
                {
                    'type': 'web-page',
                    'url': (
                        f'{SCIETY_ARTICLES_EVALUATIONS_URL}'
                        f'{HYPOTHESIS_ID_1}/content'
                    )
                }
            ]
        }


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


class TestGetRelatedOrganizationDetail:
    def test_should_return_only_institution_if_country_not_defined(self):
        editor_detail_dict = {'institution': 'institution_1', 'country': None}
        result = get_related_organization_detail(editor_detail_dict)
        assert result == 'institution_1'

    def test_should_return_institution_and_country_if_defined(self):
        editor_detail_dict = {'institution': 'institution_1', 'country': 'country_1'}
        result = get_related_organization_detail(editor_detail_dict)
        assert result == 'institution_1, country_1'

class TestGetDocmapEvaluationParticipantsForEvaluationSummaryType:
    def test_should_raise_assertion_error_if_the_role_not_editor_or_senior_editor(self):
        editor_detail_dict = {'name': 'name_1', 'institution': 'institution_1', 'country': None}
        role = 'role_1'
        with pytest.raises(AssertionError):
            get_docmap_evaluation_participants_for_evaluation_summary_type(
                editor_detail=editor_detail_dict,
                role=role
            )

    def test_should_populate_participants_with_and_given_reviewing_editor_detail_(self):
        editor_detail_dict = {'name': 'name_1', 'institution': 'institution_1', 'country': None}
        role = 'editor'
        result = get_docmap_evaluation_participants_for_evaluation_summary_type(
            editor_detail=editor_detail_dict,
            role=role
        )
        assert result == {
            'actor': {
                'name': 'name_1',
                'type': 'person',
                '_relatesToOrganization': get_related_organization_detail(editor_detail_dict)
            },
            'role': 'editor'
        }


class TestGetDocmapEvaluationParticipantsForEvalutionSummaryType:
    def test_should_populate_evaluation_participants_for_evaluation_summary_type(self):
        editor_detail_1 = {
            'name': 'editor_name_1',
            'institution': 'editor_institution_1',
            'country': 'editor_country_1'
        }
        editor_detail_2 = {
            'name': 'editor_name_2',
            'institution': 'editor_institution_2',
            'country': None
        }
        senior_editor_detail_1 = {
            'name': 'senior_editor_name_1',
            'institution': 'senior_editor_institution_1',
            'country': 'senior_editor_country_1'
        }
        result = get_docmap_evaluation_participants_for_evalution_summary_type(
            editor_details_list=[editor_detail_1, editor_detail_2],
            senior_editor_details_list=[senior_editor_detail_1]
        )
        assert result == [
            get_docmap_evaluation_participants_for_evaluation_summary_type(
                editor_detail=editor_detail_1,
                role= 'editor'
            ),
            get_docmap_evaluation_participants_for_evaluation_summary_type(
                editor_detail=editor_detail_2,
                role= 'editor'
            ),
            get_docmap_evaluation_participants_for_evaluation_summary_type(
                editor_detail=senior_editor_detail_1,
                role= 'senior-editor'
            )
        ]


class TestGetDocmapEvaluationParticipants:
    def test_should_call_func_review_article_type_when_evaluation_type_review_article(self):
        with patch.object(
            evaluation_module,
            'get_docmap_evaluation_participants_for_review_article_type'
        ) as mock:
            get_docmap_evaluation_participants(
                query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
                docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE
            )
            mock.assert_called_once()

    def test_should_call_func_evaluation_summary_type_when_evaluation_type_valuation_summary(self):
        with patch.object(
            evaluation_module,
            'get_docmap_evaluation_participants_for_evalution_summary_type'
        ) as mock:
            get_docmap_evaluation_participants(
                query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
                docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY
            )
            mock.assert_called_once()

