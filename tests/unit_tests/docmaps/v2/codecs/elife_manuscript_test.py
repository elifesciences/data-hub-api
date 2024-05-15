from datetime import datetime

from data_hub_api.config import (
    DOI_ROOT_URL,
    ELECTRONIC_ARTICLE_IDENTIFIER_PREFIX,
    ELIFE_FIRST_PUBLICATION_YEAR
)
from data_hub_api.docmaps.v2.codecs.elife_manuscript import (
    get_docmap_elife_manuscript_doi_assertion_item,
    get_docmap_elife_manuscript_doi_assertion_item_for_vor,
    get_docmap_elife_manuscript_input,
    get_docmap_elife_manuscript_output,
    get_docmap_elife_manuscript_output_for_published_step,
    get_docmap_elife_manuscript_output_for_vor,
    get_elife_manuscript_electronic_article_identifier,
    get_elife_manuscript_part_of_section,
    get_elife_manuscript_version,
    get_sorted_elife_manuscript_part_of_section_complement,
    iter_elife_manuscript_part_of_section_complement_for_each_record,
    iter_elife_manuscript_part_of_section_complement_for_one_record,
    get_elife_manuscript_subject_disciplines,
    get_elife_manuscript_version_doi,
    get_elife_manuscript_volume
)

from tests.unit_tests.docmaps.v2.test_data import (
    COLLECTIONS_DICT_1,
    DOCMAPS_QUERY_RESULT_ITEM_1,
    DOCMAPS_QUERY_RESULT_ITEM_2,
    DOCMAPS_QUERY_RESULT_ITEM_WITH_VOR_VERSION,
    MANUSCRIPT_VERSION_WITH_EVALUATIONS_AND_VOR_1,
    PODCAST_DICT_WITH_NO_VALUE_1,
    RELATED_ARTICLE_CONTENT_INPUT_DICT_1,
    RELATED_ARTICLE_DOCMAP_OUTPUT_1,
    RELATED_COLLECTION_CONTENT_INPUT_DICT_1,
    RELATED_COLLECTION_DOCMAP_OUTPUT_1,
    RELATED_CONTENT_DICT_WITH_NO_VALUE_1,
    RELATED_CONTENT_DICT_WITH_ALL_VALUE_1,
    RELATED_PODACST_DOCMAP_OUTPUT_1,
    RELATED_PODCAST_CONTENT_INPUT_DICT_1,
    RP_PUBLICATION_TIMESTAMP_1,
    MANUSCRIPT_VERSION_1,
    SUBJECT_AREA_NAME_1,
    SUBJECT_AREA_NAME_2,
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
                elife_doi=DOCMAPS_QUERY_RESULT_ITEM_1['elife_doi'],
                is_vor=True
            ),
            'versionIdentifier': get_elife_manuscript_version(
                MANUSCRIPT_VERSION_1['elife_doi_version_str'],
                is_vor=True
            )
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
    def test_should_return_volume_when_rp_publication_timestamp_is_defined(self):
        result = get_elife_manuscript_volume({
            **MANUSCRIPT_VERSION_1,
            'rp_publication_timestamp': datetime.fromisoformat('2020-05-05T01:02:03+00:00')
        })
        assert result == str(2020 - ELIFE_FIRST_PUBLICATION_YEAR)

    def test_should_return_none_when_rp_publication_timestamp_less_than_first_publication_year(
        self
    ):
        result = get_elife_manuscript_volume({
            **MANUSCRIPT_VERSION_1,
            'rp_publication_timestamp': datetime.fromisoformat('2010-05-05T01:02:03+00:00')
        })
        assert not result


class TestGetElifeManuscriptElectronicArticleIdentifier:
    def test_should_concat_rp_prefix_with_manuscript_id(self):
        result = get_elife_manuscript_electronic_article_identifier({
            **DOCMAPS_QUERY_RESULT_ITEM_1,
            'manuscript_id': 'manuscript_id_1'
        })
        assert result == ELECTRONIC_ARTICLE_IDENTIFIER_PREFIX + 'manuscript_id_1'


class TestGetElifeManuscriptSubjectDisciplines:
    def test_should_return_list_of_subject_disciplines(self):
        result = get_elife_manuscript_subject_disciplines(
            MANUSCRIPT_VERSION_1['subject_areas']
        )
        assert result == [SUBJECT_AREA_NAME_1, SUBJECT_AREA_NAME_2]

    def test_should_return_none_when_subject_areas_is_none(self):
        manuscript_version_without_subject_area = {
            **MANUSCRIPT_VERSION_1,
            'subject_areas': None
        }
        result = get_elife_manuscript_subject_disciplines(
            manuscript_version_without_subject_area['subject_areas']
        )
        assert not result


class TestIterElifeManuscriptPartOfSectionComplementForOneRecord:
    def test_should_have_complement_none_if_related_content_is_not_available(self):
        result_without_related_content = list(
            iter_elife_manuscript_part_of_section_complement_for_one_record(
                RELATED_CONTENT_DICT_WITH_NO_VALUE_1
            )
        )
        assert not result_without_related_content

    def test_should_populate_complement_if_related_content_for_all_value_is_available(self):
        result_with_related_content = list(
            iter_elife_manuscript_part_of_section_complement_for_one_record(
                RELATED_CONTENT_DICT_WITH_ALL_VALUE_1
            )
        )
        assert result_with_related_content == [
            RELATED_ARTICLE_DOCMAP_OUTPUT_1,
            RELATED_COLLECTION_DOCMAP_OUTPUT_1,
            RELATED_PODACST_DOCMAP_OUTPUT_1
        ]

    def test_should_populate_complement_if_only_related_article_data_available(self):
        result_with_related_content = list(
            iter_elife_manuscript_part_of_section_complement_for_one_record(
                RELATED_ARTICLE_CONTENT_INPUT_DICT_1
            )
        )
        assert result_with_related_content == [RELATED_ARTICLE_DOCMAP_OUTPUT_1]

    def test_should_populate_complement_if_only_collections_data_available(self):
        result_with_related_content = list(
            iter_elife_manuscript_part_of_section_complement_for_one_record(
                RELATED_COLLECTION_CONTENT_INPUT_DICT_1
            )
        )
        assert result_with_related_content == [RELATED_COLLECTION_DOCMAP_OUTPUT_1]

    def test_should_populate_complement_if_only_podcast_data_available(self):
        result_with_related_content = list(
            iter_elife_manuscript_part_of_section_complement_for_one_record(
                RELATED_PODCAST_CONTENT_INPUT_DICT_1
            )
        )
        assert result_with_related_content == [RELATED_PODACST_DOCMAP_OUTPUT_1]

    def test_should_populate_complement_collection_description_without_et_al_when_false(self):
        result_with_related_content = list(
            iter_elife_manuscript_part_of_section_complement_for_one_record(
                {**RELATED_CONTENT_DICT_WITH_NO_VALUE_1,
                 **PODCAST_DICT_WITH_NO_VALUE_1,
                 **COLLECTIONS_DICT_1,
                 'is_collection_curator_et_al': False}
            )
        )
        assert result_with_related_content[0]['description'] == (
            'Edited by collection_curator_name_1'
        )


class TestGetElifeManuscriptPartOfSectionComplementForEachRecord:
    def test_should_return_related_content_for_values_of_all_types_in_same_row(self):
        actual_result = list(iter_elife_manuscript_part_of_section_complement_for_each_record(
            [RELATED_CONTENT_DICT_WITH_ALL_VALUE_1]
        ))
        assert actual_result == list(
            iter_elife_manuscript_part_of_section_complement_for_one_record(
                RELATED_CONTENT_DICT_WITH_ALL_VALUE_1
            )
        )

    def test_should_return_related_content_for_values_of_all_types_in_separate_rows(self):
        actual_result = list(iter_elife_manuscript_part_of_section_complement_for_each_record([
            RELATED_ARTICLE_CONTENT_INPUT_DICT_1,
            RELATED_COLLECTION_CONTENT_INPUT_DICT_1,
            RELATED_PODCAST_CONTENT_INPUT_DICT_1
        ]))
        assert actual_result == (
            list(iter_elife_manuscript_part_of_section_complement_for_one_record(
                RELATED_ARTICLE_CONTENT_INPUT_DICT_1
            ))
            + list(iter_elife_manuscript_part_of_section_complement_for_one_record(
                RELATED_COLLECTION_CONTENT_INPUT_DICT_1
            ))
            + list(iter_elife_manuscript_part_of_section_complement_for_one_record(
                RELATED_PODCAST_CONTENT_INPUT_DICT_1
            ))
        )


class TestGetSortedElifeManuscriptPartOfSectionComplement:
    def test_should_sort_itearble_by_url(self):
        result = get_sorted_elife_manuscript_part_of_section_complement(
            [{'url': 'url_3', 'title': 'title_3'}, {'url': 'url_2'}, {'url': 'url_1'}]
        )
        assert result == [{'url': 'url_1'}, {'url': 'url_2'}, {'url': 'url_3', 'title': 'title_3'}]


class TestIterElifeManuscriptPartOfSection:
    def test_should_populate_elife_manuscript_part_of_section(self):
        result = get_elife_manuscript_part_of_section(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1
        )
        assert result == {
            'type': 'manuscript',
            'doi': DOCMAPS_QUERY_RESULT_ITEM_1['elife_doi'],
            'identifier': DOCMAPS_QUERY_RESULT_ITEM_1['manuscript_id'],
            'subjectDisciplines': get_elife_manuscript_subject_disciplines(
                MANUSCRIPT_VERSION_1['subject_areas']
            ),
            'published': MANUSCRIPT_VERSION_1['rp_publication_timestamp'].isoformat(),
            'volumeIdentifier': get_elife_manuscript_volume(MANUSCRIPT_VERSION_1),
            'electronicArticleIdentifier': get_elife_manuscript_electronic_article_identifier(
                DOCMAPS_QUERY_RESULT_ITEM_1
            ),
            'complement': list(iter_elife_manuscript_part_of_section_complement_for_one_record(
                RELATED_CONTENT_DICT_WITH_NO_VALUE_1
            ))
        }

    def test_should_populate_volume_id_caculated_by_first_publication_year_for_each_version(self):
        result_for_first_version = get_elife_manuscript_part_of_section(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1
        )
        result_for_second_version = get_elife_manuscript_part_of_section(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_2
        )
        expected_result = str(2022 - ELIFE_FIRST_PUBLICATION_YEAR)
        assert result_for_first_version['volumeIdentifier'] == expected_result
        assert result_for_second_version['volumeIdentifier'] == expected_result

    def test_should_populate_published_with_the_first_version_rp_publication(self):
        published_for_first_version = get_elife_manuscript_part_of_section(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1
        )['published']
        published_for_second_version = get_elife_manuscript_part_of_section(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_2
        )['published']
        assert published_for_first_version == RP_PUBLICATION_TIMESTAMP_1.isoformat()
        assert published_for_second_version == RP_PUBLICATION_TIMESTAMP_1.isoformat()

    def test_should_not_have_complement_if_related_content_is_not_available(self):
        result_without_related_content = get_elife_manuscript_part_of_section(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_1
        )
        assert not result_without_related_content['complement']

    def test_should_populate_complement_if_related_content_is_available(self):
        result_with_related_content = get_elife_manuscript_part_of_section(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_2
        )
        assert result_with_related_content['complement'] == list(
            iter_elife_manuscript_part_of_section_complement_for_one_record(
                RELATED_CONTENT_DICT_WITH_ALL_VALUE_1
            )
        )


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
                DOCMAPS_QUERY_RESULT_ITEM_1
            )
        }


class TestGetDocmapElifeManuscriptOutputForVor:
    def test_should_populate_docmaps_elife_manuscript_output_for_vor(self):
        result = get_docmap_elife_manuscript_output_for_vor(
            query_result_item=DOCMAPS_QUERY_RESULT_ITEM_WITH_VOR_VERSION,
            manuscript_version=MANUSCRIPT_VERSION_WITH_EVALUATIONS_AND_VOR_1
        )
        manuscript_version_doi = get_elife_manuscript_version_doi(
            elife_doi=DOCMAPS_QUERY_RESULT_ITEM_WITH_VOR_VERSION['elife_doi'],
            elife_doi_version_str=MANUSCRIPT_VERSION_WITH_EVALUATIONS_AND_VOR_1[
                'elife_doi_version_str'
            ],
            is_vor=True
        )
        assert result == {
            'type': 'version-of-record',
            'identifier': DOCMAPS_QUERY_RESULT_ITEM_WITH_VOR_VERSION['manuscript_id'],
            'doi': manuscript_version_doi,
            'versionIdentifier': MANUSCRIPT_VERSION_WITH_EVALUATIONS_AND_VOR_1['elife_doi_version_str'],
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
