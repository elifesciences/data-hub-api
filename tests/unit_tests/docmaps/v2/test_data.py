from datetime import date, datetime

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

TDM_PATH_1 = 'tdm_path_1'
TDM_PATH_2 = 'tdm_path_2'
TDM_PATH_3 = 'tdm_path_3'


LICENSE_1 = 'license_1'

MANUSCRIPT_VERSION_1: dict = {
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
    'tdm_path': TDM_PATH_1,
    'evaluations': []
}

MANUSCRIPT_VERSION_2: dict = {
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
    'tdm_path': TDM_PATH_2,
    'evaluations': []
}

DOCMAPS_QUERY_RESULT_ITEM_1: dict = {
    'publisher_json': '{"id": "publisher_1"}',
    'manuscript_id': 'manuscript_id_1',
    'elife_doi': ELIFE_DOI_1,
    'license': LICENSE_1,
    'is_reviewed_preprint_type': True,
    'manuscript_versions': [MANUSCRIPT_VERSION_1]
}

DOCMAPS_QUERY_RESULT_ITEM_2: dict = {
    'publisher_json': '{"id": "publisher_1"}',
    'manuscript_id': 'manuscript_id_1',
    'elife_doi': ELIFE_DOI_1,
    'license': LICENSE_1,
    'is_reviewed_preprint_type': True,
    'manuscript_versions': [MANUSCRIPT_VERSION_1, MANUSCRIPT_VERSION_2]
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

MANUSCRIPT_VERSION_WITH_EVALUATIONS_1 = {
    **MANUSCRIPT_VERSION_1,
    'evaluations': [DOCMAPS_QUERY_RESULT_EVALUATION_1]
}

MANUSCRIPT_VERSION_WITH_EVALUATIONS_2 = {
    **MANUSCRIPT_VERSION_2,
    'evaluations': [DOCMAPS_QUERY_RESULT_EVALUATION_2]
}

DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATIONS = {
    **DOCMAPS_QUERY_RESULT_ITEM_1,
    'manuscript_versions': [MANUSCRIPT_VERSION_WITH_EVALUATIONS_1]
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