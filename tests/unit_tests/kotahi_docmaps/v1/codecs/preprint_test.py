from data_hub_api.kotahi_docmaps.v1.codecs.preprint import (
    get_docmap_preprint_assertion_item,
    get_docmap_preprint_input
)
from tests.unit_tests.kotahi_docmaps.v1.test_data import (
    DOI_1,
    MANUSCRIPT_VERSION_1
)


class TestGetDocmapPreprintInput:
    def test_should_populate_docmap_preprint_input(self):
        result = get_docmap_preprint_input(
            manuscript_version=MANUSCRIPT_VERSION_1
        )
        assert result == {
            'type': 'preprint',
            'doi': DOI_1
        }


class TestGetDocmapPreprintAssertionItem:
    def test_should_populate_docmaps_preprint_input(self):
        result = get_docmap_preprint_assertion_item(manuscript_version=MANUSCRIPT_VERSION_1)
        assert result == {
            'type': 'preprint',
            'doi': DOI_1
        }
