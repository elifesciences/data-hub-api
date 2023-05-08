

from datetime import date
from data_hub_api.docmaps.codecs.preprint import get_docmap_preprint_output

PREPRINT_DETAILS_1 = {
    'preprint_url': 'preprint_url_1',
    'elife_doi_version_str': '',
    'preprint_doi': 'doi_1',
    'preprint_version': '',
    'preprint_published_at_date': date.fromisoformat('2021-01-01'),
    'tdm_path': 'tdm_path_1'
}


class TestGetDocmapPreprintOutputs:
    def test_should_populate_docmaps_preprint_output(self):
        result = get_docmap_preprint_output(preprint=PREPRINT_DETAILS_1)
        assert result == {
            'type': 'preprint',
            'doi': 'doi_1',
            'url': 'preprint_url_1',
            'published': (
                PREPRINT_DETAILS_1['preprint_published_at_date']
                .isoformat()
            ),
            'versionIdentifier': PREPRINT_DETAILS_1['preprint_version'],
            '_tdmPath': 'tdm_path_1'
        }

    def test_should_set_published_date_none_if_not_available(self):
        result = get_docmap_preprint_output(preprint={
            **PREPRINT_DETAILS_1,
            'preprint_published_at_date': ''
        })
        assert result == {
            'type': 'preprint',
            'doi': 'doi_1',
            'url': 'preprint_url_1',
            'published': None,
            'versionIdentifier': PREPRINT_DETAILS_1['preprint_version'],
            '_tdmPath': 'tdm_path_1'
        }
