from data_hub_api.docmaps.codecs.preprint import (
    get_docmap_preprint_assertion_item,
    get_docmap_preprint_input,
    get_docmap_preprint_output
)
from tests.unit_tests.docmaps.test_data import (
    DOI_1,
    PREPRINT_DETAILS_1,
    PREPRINT_LINK_1,
    PREPRINT_VERSION_1,
    TDM_PATH_1
)


class TestGetDocmapPreprintOutputs:
    def test_should_populate_docmaps_preprint_output(self):
        result = get_docmap_preprint_output(preprint=PREPRINT_DETAILS_1)
        assert result == {
            'type': 'preprint',
            'doi': DOI_1,
            'url': PREPRINT_LINK_1,
            'published': (
                PREPRINT_DETAILS_1['preprint_published_at_date']
                .isoformat()
            ),
            'versionIdentifier': PREPRINT_VERSION_1,
            '_tdmPath': TDM_PATH_1
        }

    def test_should_set_published_date_none_if_not_available(self):
        result = get_docmap_preprint_output(preprint={
            **PREPRINT_DETAILS_1,
            'preprint_published_at_date': ''
        })
        assert result == {
            'type': 'preprint',
            'doi': DOI_1,
            'url': PREPRINT_LINK_1,
            'published': None,
            'versionIdentifier': PREPRINT_VERSION_1,
            '_tdmPath': TDM_PATH_1
        }


class TestGetDocmapPreprintInput:
    def test_should_populate_docmaps_preprint_input(self):
        result = get_docmap_preprint_input(preprint=PREPRINT_DETAILS_1)
        assert result == {
            'type': 'preprint',
            'doi': DOI_1,
            'url': PREPRINT_LINK_1,
            'versionIdentifier': PREPRINT_VERSION_1
        }


class TestGetDocmapPreprintAssertionItem:
    def test_should_populate_docmaps_preprint_input(self):
        result = get_docmap_preprint_assertion_item(preprint=PREPRINT_DETAILS_1)
        assert result == {
            'type': 'preprint',
            'doi': DOI_1,
            'versionIdentifier': PREPRINT_VERSION_1
        }
