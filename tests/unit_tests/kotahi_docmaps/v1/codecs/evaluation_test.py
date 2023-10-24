from unittest.mock import patch
import pytest
from data_hub_api.kotahi_docmaps.v1.codecs import evaluation as evaluation_module
from data_hub_api.kotahi_docmaps.v1.codecs.evaluation import (
    DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY,
    DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE,
    extract_elife_assessments_from_email,
    extract_elife_public_reviews_from_email,
    extract_public_review_parts,
    get_docmap_affiliation,
    get_docmap_affiliation_location,
    get_docmap_evaluation_output,
    get_docmap_evaluation_output_content,
    get_docmap_evaluation_participants,
    get_docmap_evaluation_participants_for_evaluation_summary_type,
    get_docmap_evaluation_participants_for_evalution_summary_type,
    get_evaluation_and_type_list_from_email,
    get_related_organization_detail
)
from tests.unit_tests.kotahi_docmaps.v1.test_data import (
    EDITOR_DETAIL_1,
    ELIFE_ASSESSMENT_1,
    EMAIL_BODY_1,
    EMAIL_BODY_WITH_ELIFE_ASSESSMENT_AND_PUBLIC_REVIEWS_1,
    MANUSCRIPT_VERSION_1,
    PUBLIC_REVIEWS_1,
    PUBLIC_REVIEWS_WITHOUT_EVALUATION_1,
    REVIEW_1,
    REVIEW_2,
    REVIEW_3,
    SENIOR_EDITOR_DETAIL_1
)


class TestExtractElifeAssessmentsFromEmail:
    def test_should_extract_elife_assessment_from_email(self):
        result = extract_elife_assessments_from_email(
            EMAIL_BODY_WITH_ELIFE_ASSESSMENT_AND_PUBLIC_REVIEWS_1
        )
        assert result == ELIFE_ASSESSMENT_1.strip()

    def test_should_return_none_if_there_is_no_elife_assessment_in_email(self):
        assert not extract_elife_assessments_from_email(EMAIL_BODY_1)

    def test_should_return_none_if_there_is_no_email_body(self):
        assert not extract_elife_assessments_from_email(None)


class TestExtractElifePublicReviewsFromEmail:
    def test_should_extract_elife_public_reviews_from_email(self):
        result = extract_elife_public_reviews_from_email(
            EMAIL_BODY_WITH_ELIFE_ASSESSMENT_AND_PUBLIC_REVIEWS_1
        ).strip()
        assert result == PUBLIC_REVIEWS_1.strip()

    def test_should_return_none_if_there_is_no_public_reviews_available(self):
        assert not extract_elife_public_reviews_from_email(EMAIL_BODY_1)

    def test_should_return_none_if_there_is_no_email_body(self):
        assert not extract_elife_public_reviews_from_email(None)


class TestExtractPublicReviewParts:
    def test_should_extract_all_public_reviews_individually(self):
        result = extract_public_review_parts(PUBLIC_REVIEWS_1)
        assert result[0] == REVIEW_1.strip()
        assert result[1] == REVIEW_2.strip()
        assert result[2] == REVIEW_3.strip()

    def test_should_return_none_when_there_is_no_public_reviews(self):
        assert not extract_public_review_parts(None)

    def test_should_return_none_when_there_is_review_extracted(self):
        assert not extract_public_review_parts(PUBLIC_REVIEWS_WITHOUT_EVALUATION_1)


class TestGetEvaluationAndTypeListFromEmail:
    def test_should_return_elife_assessment_type_and_text_when_available(self):
        result = get_evaluation_and_type_list_from_email(
            EMAIL_BODY_WITH_ELIFE_ASSESSMENT_AND_PUBLIC_REVIEWS_1
        )
        assert len(result) > 0
        assert result[0]['evaluation_type'] == DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY
        assert result[0]['evaluation_text'] == ELIFE_ASSESSMENT_1.strip()
        assert result[1]['evaluation_type'] == DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE
        assert result[1]['evaluation_text'] == REVIEW_1.strip()
        assert result[2]['evaluation_type'] == DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE
        assert result[2]['evaluation_text'] == REVIEW_2.strip()
        assert result[3]['evaluation_type'] == DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE
        assert result[3]['evaluation_text'] == REVIEW_3.strip()

    def test_should_return_empty_list_if_there_is_no_email_body(self):
        assert not get_evaluation_and_type_list_from_email(None)

    def test_should_return_empty_list_if_there_is_no_evalutaion_in_email_body(self):
        assert not get_evaluation_and_type_list_from_email(EMAIL_BODY_1)


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
