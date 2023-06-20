from datetime import date
from data_hub_api.docmaps.v2.codecs.preprint import (
    get_docmap_preprint_assertion_item,
    get_docmap_preprint_input,
    get_docmap_preprint_input_with_published_and_tdmpath
)
from tests.unit_tests.docmaps.v2.test_data import (
    DOI_1,
    MANUSCRIPT_VERSION_1,
    PREPRINT_LINK_1,
    PREPRINT_VERSION_1,
    TDM_PATH_1
)


class TestGetDocmapPreprintInput:
    def test_should_populate_published_and_tdm_path_if_detailed_param_true(self):
        result = get_docmap_preprint_input_with_published_and_tdmpath(
            manuscript_version=MANUSCRIPT_VERSION_1
        )
        assert result == {
            'type': 'preprint',
            'doi': DOI_1,
            'url': PREPRINT_LINK_1,
            'versionIdentifier': PREPRINT_VERSION_1,
            'published': date.fromisoformat('2021-01-01').isoformat(),
            '_tdmPath': TDM_PATH_1
        }

    def test_should_return_empty_str_for_published_if_not_defined(self):
        manuscript_version = {
            **MANUSCRIPT_VERSION_1,
            'preprint_published_at_date': None
        }
        result = get_docmap_preprint_input_with_published_and_tdmpath(
            manuscript_version=manuscript_version
        )
        assert result == {
            'type': 'preprint',
            'doi': DOI_1,
            'url': PREPRINT_LINK_1,
            'versionIdentifier': PREPRINT_VERSION_1,
            'published': '',
            '_tdmPath': TDM_PATH_1
        }

    def test_should_not_populate_published_and_tdm_path_if_detailed_param_false(self):
        result = get_docmap_preprint_input(manuscript_version=MANUSCRIPT_VERSION_1)
        assert result == {
            'type': 'preprint',
            'doi': DOI_1,
            'url': PREPRINT_LINK_1,
            'versionIdentifier': PREPRINT_VERSION_1
        }


class TestGetDocmapPreprintAssertionItem:
    def test_should_populate_docmaps_preprint_input(self):
        result = get_docmap_preprint_assertion_item(manuscript_version=MANUSCRIPT_VERSION_1)
        assert result == {
            'type': 'preprint',
            'doi': DOI_1,
            'versionIdentifier': PREPRINT_VERSION_1
        }
