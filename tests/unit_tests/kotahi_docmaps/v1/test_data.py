from datetime import date, datetime

from data_hub_api.kotahi_docmaps.v1.api_input_typing import (
    ApiEditorDetailInput,
    ApiInput,
    ApiManuscriptVersionInput
)

MANUSCRIPT_ID_1 = 'manuscript_id_1'

LONG_MANUSCRIPT_ID_1 = 'long_manuscript_id'
LONG_MANUSCRIPT_ID_2 = 'long_manuscript_id_R1'

DOI_1 = '10.1101.test/doi1'
DOI_2 = '10.1101.test/doi2'

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

LICENSE_1 = 'license_1'

SUBJECT_AREA_NAME_1 = 'subject_area_name_1'
SUBJECT_AREA_NAME_2 = 'subject_area_name_2'

MANUSCRIPT_VERSION_1: ApiManuscriptVersionInput = {
    'long_manuscript_identifier': LONG_MANUSCRIPT_ID_1,
    'position_in_overall_stage': 1,
    'qc_complete_timestamp': datetime.fromisoformat('2022-01-01T01:02:03+00:00'),
    'under_review_timestamp': datetime.fromisoformat('2022-02-01T01:02:03+00:00'),
    'editor_details': [],
    'senior_editor_details': [],
    'preprint_url': PREPRINT_LINK_1,
    'elife_doi_version_str': ELIFE_DOI_VERSION_STR_1,
    'preprint_doi': DOI_1,
    'preprint_version': PREPRINT_VERSION_1,
    'preprint_published_at_date': date.fromisoformat('2021-01-01'),
    'email_body': '',
    'email_timestamp': None
}

MANUSCRIPT_VERSION_2: ApiManuscriptVersionInput = {
    'long_manuscript_identifier': LONG_MANUSCRIPT_ID_2,
    'position_in_overall_stage': 2,
    'qc_complete_timestamp': datetime.fromisoformat('2022-02-02T02:02:02+00:00'),
    'under_review_timestamp': datetime.fromisoformat('2022-03-02T02:02:02+00:00'),
    'editor_details': [],
    'senior_editor_details': [],
    'preprint_url': PREPRINT_LINK_2,
    'elife_doi_version_str': ELIFE_DOI_VERSION_STR_2,
    'preprint_doi': DOI_2,
    'preprint_version': PREPRINT_VERSION_2,
    'preprint_published_at_date': date.fromisoformat('2021-02-02'),
    'email_body': '',
    'email_timestamp': None
}

PUBLISHER_DICT_1 = {"id": "publisher_1"}
PUBLISHER_DICT_STR_1 = f'{PUBLISHER_DICT_1}'

DOCMAPS_QUERY_RESULT_ITEM_1: ApiInput = {
    'publisher_json': PUBLISHER_DICT_STR_1,
    'manuscript_id': 'manuscript_id_1',
    'elife_doi': ELIFE_DOI_1,
    'license': LICENSE_1,
    'is_reviewed_preprint_type': True,
    'manuscript_versions': [MANUSCRIPT_VERSION_1]
}

DOCMAPS_QUERY_RESULT_ITEM_2: ApiInput = {
    'publisher_json': PUBLISHER_DICT_STR_1,
    'manuscript_id': 'manuscript_id_1',
    'elife_doi': ELIFE_DOI_1,
    'license': LICENSE_1,
    'is_reviewed_preprint_type': True,
    'manuscript_versions': [MANUSCRIPT_VERSION_1, MANUSCRIPT_VERSION_2]
}

SPACE_1 = ' '
COLON_1 = ' '

REVIEW_1 = f'''
    Reviewer #1 (Public Review){COLON_1}{SPACE_1}

    This is review_1.
'''

REVIEW_2 = f'''
    Reviewer #2 (Public Review){COLON_1}

    This is review_2.
'''

REVIEW_3 = '''
    Reviewer #3 (Public Review):

    This is review_3.
'''

ELIFE_ASSESSMENT_1 = '''
    eLife assessment

    This is eLife assessment.
'''

PUBLIC_REVIEWS_1 = f'''
    Public Reviews

    {REVIEW_1}

    {REVIEW_2}

    {REVIEW_3}
'''

JOINT_PUBLIC_REVIEW_1 = '''
    Public Review:

    Text for public review

'''

EMAIL_BODY_WITH_JOINT_PUBLIC_REVIEW_1 = f'''
    Dear Dr Huang,

    Thank you for submitting your article.

    {JOINT_PUBLIC_REVIEW_1}
    ----------
'''

PUBLIC_REVIEWS_WITHOUT_EVALUATION_1 = '''
    Public Reviews
    some text here but not review

----------
'''

EMAIL_BODY_INTRO_FOR_ELIFE_ASSESSMENT_AND_PUBLIC_REVIEWS_1 = '''
    Dear Dr Huang,

    Thank you for submitting your article.
    Please note that the reviews are in two parts: public reviews are near the top and recommendations to the authors follow further down. 

'''

EMAIL_BODY_1 = '''
    Dear Dr Huang,

    Thank you for submitting your article.
    ----------

    ----------
'''

EMAIL_BODY_WITH_ELIFE_ASSESSMENT_1 = f'''
    Dear Dr Huang,

    Thank you for submitting your article.
    ----------

    {ELIFE_ASSESSMENT_1}

    ----------

'''

EMAIL_BODY_WITH_PUBLIC_REVIEWS_1 = f'''
    {EMAIL_BODY_INTRO_FOR_ELIFE_ASSESSMENT_AND_PUBLIC_REVIEWS_1}
    ----------

    {PUBLIC_REVIEWS_1}

    ----------
'''

EMAIL_BODY_WITH_ELIFE_ASSESSMENT_AND_PUBLIC_REVIEWS_1 = f'''
    {EMAIL_BODY_INTRO_FOR_ELIFE_ASSESSMENT_AND_PUBLIC_REVIEWS_1}
    ----------

    {ELIFE_ASSESSMENT_1}

    ----------

    {PUBLIC_REVIEWS_1}

    ----------
'''

EMAIL_BODY_WITH_ELIFE_ASSESSMENT_WITHOUT_EXPECTED_END = f'''
    Dear Dr Huang,

    Thank you for submitting your article.
    ----------

    {ELIFE_ASSESSMENT_1}

    Public Review
'''

EDITOR_DETAIL_1: ApiEditorDetailInput = {
    'name': 'editor_name_1',
    'institution': 'editor_institution_1',
    'country': 'editor_country_1',
    'title': 'editor_title_1',
    'first_name': 'editor_first_name_1',
    'middle_name': 'editor_middle_name_1',
    'last_name': 'editor_last_name_1',
    'city': 'editor_city_1'
}

SENIOR_EDITOR_DETAIL_1: ApiEditorDetailInput = {
    'name': 'senior_editor_name_1',
    'institution': 'senior_editor_institution_1',
    'country': 'senior_editor_country_1',
    'title': 'senior_editor_title_1',
    'first_name': 'senior_editor_first_name_1',
    'middle_name': 'senior_editor_middle_name_1',
    'last_name': 'senior_editor_last_name_1',
    'city': 'senior_editor_city_1'
}

EMAIL_TIMESTAMP_1 = datetime.fromisoformat('2023-01-01T01:00:03+00:00')

MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_1: ApiManuscriptVersionInput = {
    **MANUSCRIPT_VERSION_1,  # type: ignore
    'email_body': EMAIL_BODY_WITH_ELIFE_ASSESSMENT_1,
    'email_timestamp': EMAIL_TIMESTAMP_1,
}

DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATION_EMAILS_1 = {
    **DOCMAPS_QUERY_RESULT_ITEM_1,  # type: ignore
    'manuscript_versions': [MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_1]
}

MANUSCRIPT_VERSION_WITH_EVALUATION_EMAILS_2: ApiManuscriptVersionInput = {
    **MANUSCRIPT_VERSION_2,  # type: ignore
    'email_body': EMAIL_BODY_WITH_PUBLIC_REVIEWS_1,
    'email_timestamp': EMAIL_TIMESTAMP_1,
}

MANUSCRIPT_VERSION_WITH_ELIFE_ASSESSMENT_AND_PUBLIC_REVIEWS_1: ApiManuscriptVersionInput = {
    **MANUSCRIPT_VERSION_2,  # type: ignore
    'email_body': EMAIL_BODY_WITH_ELIFE_ASSESSMENT_AND_PUBLIC_REVIEWS_1,
    'email_timestamp': EMAIL_TIMESTAMP_1,
}
