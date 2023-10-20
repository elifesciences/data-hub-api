from unittest.mock import patch
import pytest
from data_hub_api.kotahi_docmaps.v1.codecs import evaluation as evaluation_module
from data_hub_api.kotahi_docmaps.v1.codecs.evaluation import (
    DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY,
    DOCMAP_EVALUATION_TYPE_FOR_REPLY,
    DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE,
    DOI_ROOT_URL,
    get_docmap_affiliation,
    get_docmap_affiliation_location,
    get_docmap_evaluation_output,
    get_docmap_evaluation_output_content,
    get_docmap_evaluation_participants,
    get_docmap_evaluation_participants_for_evaluation_summary_type,
    get_docmap_evaluation_participants_for_evalution_summary_type,
    get_docmap_evaluation_type_form_tags,
    get_related_organization_detail
)
from tests.unit_tests.kotahi_docmaps.v1.test_data import (
    EDITOR_DETAIL_1,
    MANUSCRIPT_VERSION_1,
    SENIOR_EDITOR_DETAIL_1
)


class TestGetDocmapEvaluationOutputContent:
    def test_should_populate_evaluation_output_content(self):
        result = get_docmap_evaluation_output_content()
        assert result == {
            'type': 'web-page',
            'url': 'TODO'
        }


class TestGetDocmapEvaluationOutput:
    def test_should_populate_evaluation_output(self):
        result = get_docmap_evaluation_output(
            docmap_evaluation_type='docmap_evaluation_type_1'
        )
        assert result == {
            'type': 'docmap_evaluation_type_1',
            'content': [
                {
                    'type': 'web-page',
                    'url': 'TODO'
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


class TestGetDocmapAffiliationLocation:
    def test_should_populate_docmap_location_with_given_details(self):
        result = get_docmap_affiliation_location(EDITOR_DETAIL_1)
        assert result == 'editor_city_1, editor_country_1'

    def test_should_populate_docmap_location_with_only_country_if_city_none(self):
        result = get_docmap_affiliation_location({
            **EDITOR_DETAIL_1,
            'city': None
        })
        assert result == 'editor_country_1'


class TestGetDocmapAffiliation:
    def test_should_populate_affiliation_with_given_details(self):
        result = get_docmap_affiliation(EDITOR_DETAIL_1)
        assert result == {
            'type': 'organization',
            'name': 'editor_institution_1',
            'location': 'editor_city_1, editor_country_1'
        }

    def test_should_return_none_for_location_if_country_none(self):
        result = get_docmap_affiliation({
            **EDITOR_DETAIL_1,
            'country': None
        })
        assert result == {
            'type': 'organization',
            'name': 'editor_institution_1',
            'location': None
        }

    def test_should_populate_location_only_with_country_if_city_none(self):
        result = get_docmap_affiliation({
            **EDITOR_DETAIL_1,
            'country': 'editor_country_1',
            'city': None
        })
        assert result == {
            'type': 'organization',
            'name': 'editor_institution_1',
            'location': 'editor_country_1'
        }


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
        editor_detail_dict = EDITOR_DETAIL_1
        role = 'editor'
        result = get_docmap_evaluation_participants_for_evaluation_summary_type(
            editor_detail=editor_detail_dict,
            role=role
        )
        assert result == {
            'actor': {
                'name': 'editor_name_1',
                'type': 'person',
                'firstName': 'editor_first_name_1',
                '_middleName': 'editor_middle_name_1',
                'surname': 'editor_last_name_1',
                '_relatesToOrganization': get_related_organization_detail(editor_detail_dict),
                'affiliation': get_docmap_affiliation(editor_detail_dict)
            },
            'role': 'editor'
        }

    def test_should_return_none_for_middle_name_if_not_defined(self):
        editor_detail_dict = {
            **EDITOR_DETAIL_1,
            'middle_name': None
        }
        role = 'editor'
        result = get_docmap_evaluation_participants_for_evaluation_summary_type(
            editor_detail=editor_detail_dict,
            role=role
        )
        assert result == {
            'actor': {
                'name': 'editor_name_1',
                'type': 'person',
                'firstName': 'editor_first_name_1',
                '_middleName': None,
                'surname': 'editor_last_name_1',
                '_relatesToOrganization': get_related_organization_detail(editor_detail_dict),
                'affiliation': get_docmap_affiliation(editor_detail_dict)
            },
            'role': 'editor'
        }


class TestGetDocmapEvaluationParticipantsForEvalutionSummaryType:
    def test_should_populate_evaluation_participants_for_evaluation_summary_type(self):
        result = get_docmap_evaluation_participants_for_evalution_summary_type(
            editor_details_list=[EDITOR_DETAIL_1],
            senior_editor_details_list=[SENIOR_EDITOR_DETAIL_1]
        )
        assert result == [
            get_docmap_evaluation_participants_for_evaluation_summary_type(
                editor_detail=EDITOR_DETAIL_1,
                role='editor'
            ),
            get_docmap_evaluation_participants_for_evaluation_summary_type(
                editor_detail=SENIOR_EDITOR_DETAIL_1,
                role='senior-editor'
            )
        ]


class TestGetDocmapEvaluationParticipants:
    def test_should_call_func_review_article_type_when_evaluation_type_review_article(self):
        with patch.object(
            evaluation_module,
            'get_docmap_evaluation_participants_for_review_article_type'
        ) as mock:
            get_docmap_evaluation_participants(
                manuscript_version=MANUSCRIPT_VERSION_1,
                docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE
            )
            mock.assert_called_once()

    def test_should_call_func_evaluation_summary_type_when_evaluation_type_valuation_summary(self):
        with patch.object(
            evaluation_module,
            'get_docmap_evaluation_participants_for_evalution_summary_type'
        ) as mock:
            get_docmap_evaluation_participants(
                manuscript_version=MANUSCRIPT_VERSION_1,
                docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY
            )
            mock.assert_called_once()
