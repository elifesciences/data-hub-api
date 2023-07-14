from datetime import date
from data_hub_api.docmaps.v2.codecs.preprint import (
    get_docmap_preprint_assertion_item,
    get_docmap_preprint_input,
    get_docmap_preprint_input_with_published_and_meca_path,
    get_meca_path_content
)
from tests.unit_tests.docmaps.v2.test_data import (
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
            'type': 'web-manifestation',
            'url': MECA_PATH_1
        }


class TestGetDocmapPreprintInputWithPublishedAndMecaPath:
    def get_docmap_preprint_input_with_published_and_meca_path(self):
        result = get_docmap_preprint_input(
            manuscript_version=MANUSCRIPT_VERSION_1
        )
        assert result == {
            'type': 'preprint',
            'doi': DOI_1,
            'url': PREPRINT_LINK_1,
            'versionIdentifier': PREPRINT_VERSION_1,
            'published': date.fromisoformat('2021-01-01').isoformat(),
            'content': [
                get_meca_path_content(MECA_PATH_1)
            ]
        }

    def test_should_return_none_for_published_if_not_defined(self):
        manuscript_version = {
            **MANUSCRIPT_VERSION_1,
            'preprint_published_at_date': None
        }
        result = get_docmap_preprint_input_with_published_and_meca_path(
            manuscript_version=manuscript_version
        )
        assert not result['published']

    def test_should_return_none_for_meca_path_content_if_not_defined(self):
        manuscript_version = {
            **MANUSCRIPT_VERSION_1,
            'meca_path': None
        }
        result = get_docmap_preprint_input_with_published_and_meca_path(
            manuscript_version=manuscript_version
        )
        assert not result['content']


class TestGetDocmapPreprintAssertionItem:
    def test_should_populate_docmaps_preprint_input(self):
        result = get_docmap_preprint_assertion_item(manuscript_version=MANUSCRIPT_VERSION_1)
        assert result == {
            'type': 'preprint',
            'doi': DOI_1,
            'versionIdentifier': PREPRINT_VERSION_1
        }
