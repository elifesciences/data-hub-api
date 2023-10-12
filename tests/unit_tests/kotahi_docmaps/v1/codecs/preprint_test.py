from data_hub_api.kotahi_docmaps.v1.codecs.preprint import (
    get_docmap_preprint_assertion_item,
    get_docmap_preprint_input,
    get_docmap_preprint_input_with_published,
    get_meca_path_content
)
from tests.unit_tests.kotahi_docmaps.v1.test_data import (
    DOI_1,
    MANUSCRIPT_VERSION_1,
    PREPRINT_LINK_1,
    PREPRINT_VERSION_1,
    MECA_PATH_1
)


class TestGetDocmapPreprintInput:
    def test_should_populate_docmap_preprint_input(self):
        result = get_docmap_preprint_input(
            manuscript_version=MANUSCRIPT_VERSION_1
        )
        assert result == {
            'type': 'preprint',
            'doi': DOI_1,
            'url': PREPRINT_LINK_1,
            'versionIdentifier': PREPRINT_VERSION_1,
        }


class TestGetMecaPathContent:
    def test_should_populate_meca_path_content(self):
        result = get_meca_path_content(MECA_PATH_1)
        assert result == {
            'type': 'computer-file',
            'url': MECA_PATH_1
        }


class TestGetDocmapPreprintInputWithPublished:
    def test_should_populate_docmap_preprint_input(self):
        result = get_docmap_preprint_input_with_published(
            manuscript_version=MANUSCRIPT_VERSION_1
        )
        assert result == {
            'type': 'preprint',
            'doi': DOI_1,
            'url': PREPRINT_LINK_1,
            'versionIdentifier': PREPRINT_VERSION_1,
            'published': '2021-01-01'
        }

    def test_should_return_none_for_published_if_not_defined(self):
        manuscript_version = {
            **MANUSCRIPT_VERSION_1,
            'preprint_published_at_date': None
        }
        result = get_docmap_preprint_input_with_published(
            manuscript_version=manuscript_version
        )
        assert not result['published']


class TestGetDocmapPreprintAssertionItem:
    def test_should_populate_docmaps_preprint_input(self):
        result = get_docmap_preprint_assertion_item(manuscript_version=MANUSCRIPT_VERSION_1)
        assert result == {
            'type': 'preprint',
            'doi': DOI_1,
            'versionIdentifier': PREPRINT_VERSION_1
        }
