from data_hub_api.config import DOI_ROOT_URL
from data_hub_api.docmaps.v2.codecs.elife_manuscript import (
    get_docmap_elife_manuscript_doi_assertion_item,
    get_docmap_elife_manuscript_doi_assertion_item_for_vor,
    get_docmap_elife_manuscript_input,
    get_docmap_elife_manuscript_output,
    get_docmap_elife_manuscript_output_for_published_step,
    get_docmap_elife_manuscript_output_for_vor,
    get_elife_manuscript_version_doi
)
from data_hub_api.utils.format_datetime import format_datetime_with_utc_offset

from tests.unit_tests.docmaps.v2.test_data import (
    DOCMAPS_QUERY_RESULT_ITEM_1,
    RP_PUBLICATION_TIMESTAMP_1,
    MANUSCRIPT_VERSION_1
)


class TestGetElifeVersionDoi:
    def test_should_return_elife_version_doi(self):
        result = get_elife_manuscript_version_doi(
            elife_doi_version_str='elife_doi_version_str_1',
            elife_doi='elife_doi_1'
        )
        assert result == 'elife_doi_1.elife_doi_version_str_1'


class TestGetDocmapElifeManuscriptDoiAssertionItem:
    def test_should_populate_docmaps_elife_manuscript_doi_assertion_item(self):
        result = get_docmap_elife_manuscript_doi_assertion_item(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            manuscript_version=MANUSCRIPT_VERSION_1
        )
        assert result == {
            'type': 'preprint',
            'doi': get_elife_manuscript_version_doi(
                elife_doi_version_str=MANUSCRIPT_VERSION_1['elife_doi_version_str'],
                elife_doi=DOCMAPS_QUERY_RESULT_ITEM_1['elife_doi']
            ),
            'versionIdentifier': MANUSCRIPT_VERSION_1['elife_doi_version_str']
        }


class TestGetDocmapElifeManuscriptDoiAssertionItemForVor:
    def test_should_populate_docmaps_elife_manuscript_doi_assertion_item_for_vor(self):
        result = get_docmap_elife_manuscript_doi_assertion_item_for_vor(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            manuscript_version=MANUSCRIPT_VERSION_1
        )
        assert result == {
            'type': 'version-of-record',
            'doi': get_elife_manuscript_version_doi(
                elife_doi_version_str=MANUSCRIPT_VERSION_1['elife_doi_version_str'],
                elife_doi=DOCMAPS_QUERY_RESULT_ITEM_1['elife_doi']
            ),
            'versionIdentifier': MANUSCRIPT_VERSION_1['elife_doi_version_str']
        }


class TestGetDocmapElifeManuscriptOutput:
    def test_should_populate_docmaps_elife_manuscript_output(self):
        result = get_docmap_elife_manuscript_output(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            manuscript_version=MANUSCRIPT_VERSION_1
        )
        assert result == {
            'type': 'preprint',
            'identifier': DOCMAPS_QUERY_RESULT_ITEM_1['manuscript_id'],
            'doi': get_elife_manuscript_version_doi(
                elife_doi_version_str=MANUSCRIPT_VERSION_1['elife_doi_version_str'],
                elife_doi=DOCMAPS_QUERY_RESULT_ITEM_1['elife_doi']
            ),
            'versionIdentifier': MANUSCRIPT_VERSION_1['elife_doi_version_str'],
            'license': DOCMAPS_QUERY_RESULT_ITEM_1['license']
        }


class TestGetDocmapElifeManuscriptOutputForPublishedStep:
    def test_should_populate_docmaps_elife_manuscript_output_for_published_step(self):
        result = get_docmap_elife_manuscript_output_for_published_step(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            manuscript_version=MANUSCRIPT_VERSION_1
        )
        assert result == {
            'type': 'preprint',
            'published': format_datetime_with_utc_offset(
                date_string=RP_PUBLICATION_TIMESTAMP_1
            ),
            'identifier': DOCMAPS_QUERY_RESULT_ITEM_1['manuscript_id'],
            'doi': get_elife_manuscript_version_doi(
                elife_doi_version_str=MANUSCRIPT_VERSION_1['elife_doi_version_str'],
                elife_doi=DOCMAPS_QUERY_RESULT_ITEM_1['elife_doi']
            ),
            'versionIdentifier': MANUSCRIPT_VERSION_1['elife_doi_version_str'],
            'license': DOCMAPS_QUERY_RESULT_ITEM_1['license']
        }

    def test_should_not_populate_published_if_rp_publication_timestamp_is_none(self):
        manuscript_version = {
            **MANUSCRIPT_VERSION_1,
            'rp_publication_timestamp': None
        }
        result = get_docmap_elife_manuscript_output_for_published_step(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            manuscript_version=manuscript_version
        )
        assert result == {
            'type': 'preprint',
            'published': None,
            'identifier': DOCMAPS_QUERY_RESULT_ITEM_1['manuscript_id'],
            'doi': get_elife_manuscript_version_doi(
                elife_doi_version_str=MANUSCRIPT_VERSION_1['elife_doi_version_str'],
                elife_doi=DOCMAPS_QUERY_RESULT_ITEM_1['elife_doi']
            ),
            'versionIdentifier': MANUSCRIPT_VERSION_1['elife_doi_version_str'],
            'license': DOCMAPS_QUERY_RESULT_ITEM_1['license']
        }


class TestGetDocmapElifeManuscriptOutputForVor:
    def test_should_populate_docmaps_elife_manuscript_output_for_vor(self):
        result = get_docmap_elife_manuscript_output_for_vor(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            manuscript_version=MANUSCRIPT_VERSION_1
        )
        manuscript_version_doi = get_elife_manuscript_version_doi(
            elife_doi=DOCMAPS_QUERY_RESULT_ITEM_1['elife_doi'],
            elife_doi_version_str=MANUSCRIPT_VERSION_1['elife_doi_version_str']
        )
        assert result == {
            'type': 'version-of-record',
            'doi': manuscript_version_doi,
            'url': f'{DOI_ROOT_URL}' + manuscript_version_doi,
            'content': [{
                'type': 'web-page',
                'url': (
                    'https://elifesciences.org/articles/'
                    + DOCMAPS_QUERY_RESULT_ITEM_1['manuscript_id']
                )
            }]
        }


class TestGetDocmapElifeManuscriptInput:
    def test_should_populate_docmaps_elife_manuscript_input(self):
        result = get_docmap_elife_manuscript_input(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            manuscript_version=MANUSCRIPT_VERSION_1
        )
        assert result == {
            'type': 'preprint',
            'doi': get_elife_manuscript_version_doi(
                elife_doi_version_str=MANUSCRIPT_VERSION_1['elife_doi_version_str'],
                elife_doi=DOCMAPS_QUERY_RESULT_ITEM_1['elife_doi']
            ),
            'identifier': DOCMAPS_QUERY_RESULT_ITEM_1['manuscript_id'],
            'versionIdentifier': MANUSCRIPT_VERSION_1['elife_doi_version_str']
        }
