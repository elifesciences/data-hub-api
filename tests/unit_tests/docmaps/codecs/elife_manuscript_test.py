from datetime import datetime
from data_hub_api.docmaps.codecs.elife_manuscript import (
    get_docmap_elife_manuscript_doi_assertion_item,
    get_elife_manuscript_version_doi
)

PREPRINT_DETAILS_1 = {
    'preprint_url': 'preprint_url_1',
    'elife_doi_version_str': 'elife_doi_version_str_1',
    'preprint_doi': 'doi_1',
    'preprint_version': 'preprint_version_1',
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


class TestGetElifeVersionDoi:
    def test_should_return_none_if_elife_doi_not_defined(self):
        assert not get_elife_manuscript_version_doi(
            elife_doi_version_str='elife_doi_version_str_1',
            elife_doi=''
        )

    def test_should_return_elife_version_doi(self):
        result = get_elife_manuscript_version_doi(
            elife_doi_version_str='elife_doi_version_str_1',
            elife_doi='elife_doi_1'
        )
        assert result == 'elife_doi_1.elife_doi_version_str_1'


class TestGetDocmapPreprintAssertionItem:
    def test_should_populate_docmaps_preprint_input(self):
        result = get_docmap_elife_manuscript_doi_assertion_item(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            preprint=PREPRINT_DETAILS_1
        )
        assert result == {
            'type': 'preprint',
            'doi': get_elife_manuscript_version_doi(
                elife_doi_version_str=PREPRINT_DETAILS_1['elife_doi_version_str'],
                elife_doi=DOCMAPS_QUERY_RESULT_ITEM_1['elife_doi']
            ),
            'versionIdentifier': PREPRINT_DETAILS_1['elife_doi_version_str']
        }
