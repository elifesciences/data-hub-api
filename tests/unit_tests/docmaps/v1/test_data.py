from datetime import date, datetime

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

LICENSE_1 = 'license_1'

DOCMAPS_QUERY_RESULT_ITEM_1: dict = {
    'manuscript_id': 'manuscript_id_1',
    'qc_complete_timestamp': datetime.fromisoformat('2022-01-01T01:02:03+00:00'),
    'under_review_timestamp': datetime.fromisoformat('2022-02-01T01:02:03+00:00'),
    'publisher_json': '{"id": "publisher_1"}',
    'elife_doi': ELIFE_DOI_1,
    'license': LICENSE_1,
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

ANNOTATION_CREATED_TIMESTAMP_1 = datetime.fromisoformat('2020-01-01T01:02:03+00:00')
ANNOTATION_CREATED_TIMESTAMP_2 = datetime.fromisoformat('2021-01-01T01:02:03+00:00')
ANNOTATION_CREATED_TIMESTAMP_3 = datetime.fromisoformat('2022-01-01T01:02:03+00:00')

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

EDITOR_DETAIL_1 = {
    'name': 'editor_name_1',
    'institution': 'editor_institution_1',
    'country': 'editor_country_1'
}

SENIOR_EDITOR_DETAIL_1 = {
    'name': 'senior_editor_name_1',
    'institution': 'senior_editor_institution_1',
    'country': 'senior_editor_country_1'
}
