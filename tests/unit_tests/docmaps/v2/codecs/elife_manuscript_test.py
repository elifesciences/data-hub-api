from data_hub_api.config import DOI_ROOT_URL, ELIFE_FIRST_PUBLICATION_YEAR
from data_hub_api.docmaps.v2.codecs.elife_manuscript import (
    get_docmap_elife_manuscript_doi_assertion_item,
    get_docmap_elife_manuscript_doi_assertion_item_for_vor,
    get_docmap_elife_manuscript_input,
    get_docmap_elife_manuscript_output,
    get_docmap_elife_manuscript_output_for_published_step,
    get_docmap_elife_manuscript_output_for_vor,
    get_elife_manuscript_part_of_section,
    get_elife_manuscript_version_doi,
    get_elife_manuscript_volume
)

from tests.unit_tests.docmaps.v2.test_data import (
    DOCMAPS_QUERY_RESULT_ITEM_1,
    DOCMAPS_QUERY_RESULT_ITEM_WITH_VOR_VERSION,
    MANUSCRIPT_VOR_VERSION_1,
    RP_PUBLICATION_TIMESTAMP_1,
    MANUSCRIPT_VERSION_1,
    VOR_PUBLICATION_DATE_1
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


class TestGetElifeManuscriptVolume:
    def test_should_return_none_if_rp_publication_year_is_none(self):
        result = get_elife_manuscript_volume({
            **MANUSCRIPT_VERSION_1,
            'rp_publication_year': None
        })
        assert not result

    def test_should_return_volume_when_rp_publication_year_is_defined(self):
        result = get_elife_manuscript_volume({
            **MANUSCRIPT_VERSION_1,
            'rp_publication_year': 2020
        })
        assert result == 2020 - ELIFE_FIRST_PUBLICATION_YEAR

    def test_should_return_none_when_rp_publication_year_less_than_elife_first_publication_year(
        self
    ):
        result = get_elife_manuscript_volume({
            **MANUSCRIPT_VERSION_1,
            'rp_publication_year': 2010
        })
        assert not result


class TestGetElifeManuscriptPartOfSection:
    def test_should_populate_elife_manuscript_part_of_section(self):
        result = get_elife_manuscript_part_of_section(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            manuscript_version=MANUSCRIPT_VERSION_1
        )
        assert result == {
            'type': 'manuscript',
            'doi': DOCMAPS_QUERY_RESULT_ITEM_1['elife_doi'],
            'identifier': DOCMAPS_QUERY_RESULT_ITEM_1['manuscript_id'],
            'volumeIdentifier': get_elife_manuscript_volume(MANUSCRIPT_VERSION_1),
            'electronicArticleIdentifier': ''
        }


class TestGetDocmapElifeManuscriptOutputForPublishedStep:
    def test_should_populate_docmaps_elife_manuscript_output_for_published_step(self):
        result = get_docmap_elife_manuscript_output_for_published_step(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1,
            manuscript_version=MANUSCRIPT_VERSION_1
        )
        assert result == {
            'type': 'preprint',
            'published': RP_PUBLICATION_TIMESTAMP_1.isoformat(),
            'identifier': DOCMAPS_QUERY_RESULT_ITEM_1['manuscript_id'],
            'doi': get_elife_manuscript_version_doi(
                elife_doi_version_str=MANUSCRIPT_VERSION_1['elife_doi_version_str'],
                elife_doi=DOCMAPS_QUERY_RESULT_ITEM_1['elife_doi']
            ),
            'versionIdentifier': MANUSCRIPT_VERSION_1['elife_doi_version_str'],
            'license': DOCMAPS_QUERY_RESULT_ITEM_1['license'],
            'partOf': get_elife_manuscript_part_of_section(
                DOCMAPS_QUERY_RESULT_ITEM_1,
                MANUSCRIPT_VERSION_1
            )
        }


class TestGetDocmapElifeManuscriptOutputForVor:
    def test_should_populate_docmaps_elife_manuscript_output_for_vor(self):
        result = get_docmap_elife_manuscript_output_for_vor(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_WITH_VOR_VERSION,
            manuscript_version=MANUSCRIPT_VOR_VERSION_1
        )
        manuscript_version_doi = get_elife_manuscript_version_doi(
            elife_doi=DOCMAPS_QUERY_RESULT_ITEM_WITH_VOR_VERSION['elife_doi'],
            elife_doi_version_str=MANUSCRIPT_VOR_VERSION_1['elife_doi_version_str']
        )
        assert result == {
            'type': 'version-of-record',
            'doi': manuscript_version_doi,
            'published': VOR_PUBLICATION_DATE_1.isoformat(),
            'url': f'{DOI_ROOT_URL}' + manuscript_version_doi,
            'content': [{
                'type': 'web-page',
                'url': (
                    'https://elifesciences.org/articles/'
                    + DOCMAPS_QUERY_RESULT_ITEM_WITH_VOR_VERSION['manuscript_id']
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
