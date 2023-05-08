from datetime import datetime

from data_hub_api.docmaps.codecs.evaluation import (
    DOI_ROOT_URL,
    HYPOTHESIS_URL,
    SCIETY_ARTICLES_ACTIVITY_URL,
    SCIETY_ARTICLES_EVALUATIONS_URL,
    get_docmap_evaluation_output,
    get_elife_evaluation_doi,
    get_elife_evaluation_doi_url
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
