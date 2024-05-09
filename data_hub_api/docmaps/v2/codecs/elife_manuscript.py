import re
from typing import Iterable, Optional, Sequence
from data_hub_api.config import (
    DOI_ROOT_URL,
    ELECTRONIC_ARTICLE_IDENTIFIER_PREFIX,
    ELIFE_FIRST_PUBLICATION_YEAR
)
from data_hub_api.docmaps.v2.api_input_typing import (
    ApiInput,
    ApiManuscriptVersionInput,
    ApiRelatedContentInput,
    ApiSubjectAreaInput
)
from data_hub_api.docmaps.v2.docmap_typing import (
    DocmapAssertionItem,
    DocmapContent,
    DocmapElifeManuscriptInput,
    DocmapElifeManuscriptOutput,
    DocmapElifeManuscriptVorOutput,
    DocmapPartOfComplement,
    DocmapPublishedElifeManuscriptOutput,
    DocmapPublishedElifeManuscriptPartOf
)


def get_elife_manuscript_version(
    elife_doi_version_str: str,
    is_vor: bool = False
) -> str:
    if is_vor:
        elife_doi_version_str = str(int(elife_doi_version_str) + 1)
    return elife_doi_version_str


def get_elife_manuscript_version_doi(
    elife_doi_version_str: str,
    elife_doi: str,
    is_vor: bool = False
) -> str:
    return (
        elife_doi
        + '.'
        + get_elife_manuscript_version(elife_doi_version_str, is_vor)
    )


def get_docmap_elife_manuscript_doi_assertion_item(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput,
    is_vor: bool = False
) -> DocmapAssertionItem:
    return {
        'type': 'preprint',
        'doi': get_elife_manuscript_version_doi(
            elife_doi=query_result_item['elife_doi'],
            elife_doi_version_str=manuscript_version['elife_doi_version_str'],
            is_vor=is_vor
        ),
        'versionIdentifier': get_elife_manuscript_version(
            manuscript_version['elife_doi_version_str'],
            is_vor
        )
    }


def get_docmap_elife_manuscript_doi_assertion_item_for_vor(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapAssertionItem:
    return {
        **get_docmap_elife_manuscript_doi_assertion_item(  # type: ignore
            query_result_item=query_result_item,
            manuscript_version=manuscript_version,
            is_vor=True
        ),
        'type': 'version-of-record'
    }


def get_docmap_elife_manuscript_output(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput,
    is_vor: bool = False
) -> DocmapElifeManuscriptOutput:
    return {
        'type': 'preprint',
        'identifier': query_result_item['manuscript_id'],
        'doi': get_elife_manuscript_version_doi(
            elife_doi=query_result_item['elife_doi'],
            elife_doi_version_str=manuscript_version['elife_doi_version_str'],
            is_vor=is_vor
        ),
        'versionIdentifier': get_elife_manuscript_version(
            manuscript_version['elife_doi_version_str'],
            is_vor
        ),
        'license': query_result_item['license']
    }


def get_elife_manuscript_volume(
    first_manuscript_version: ApiManuscriptVersionInput
) -> Optional[str]:
    assert first_manuscript_version['rp_publication_timestamp']
    first_rp_publication_year = first_manuscript_version['rp_publication_timestamp'].year
    if first_rp_publication_year >= ELIFE_FIRST_PUBLICATION_YEAR:
        return str(first_rp_publication_year - ELIFE_FIRST_PUBLICATION_YEAR)
    return None


def get_elife_manuscript_electronic_article_identifier(
    query_result_item: ApiInput
) -> str:
    return ELECTRONIC_ARTICLE_IDENTIFIER_PREFIX + query_result_item['manuscript_id']


def get_elife_manuscript_subject_disciplines(
    subject_areas: Sequence[ApiSubjectAreaInput]
) -> Optional[Sequence[str]]:
    subject_area_list = []
    if subject_areas:
        for subject_area in subject_areas:
            subject_area_list.append(subject_area['subject_area_name'])
        return subject_area_list
    return None


def iter_elife_manuscript_part_of_section_complement_for_one_record(
    related_content: ApiRelatedContentInput
) -> Iterable[DocmapPartOfComplement]:
    if related_content['manuscript_id']:
        assert related_content['manuscript_type']
        manuscript_type_parts = re.findall(r'\w+', related_content['manuscript_type'])
        manuscript_type = manuscript_type_parts[0].lower()
        manuscript_type += ''.join([part.capitalize() for part in manuscript_type_parts[1:]])
        yield {
            'type': manuscript_type,
            'url': 'https://elifesciences.org/articles/' + related_content['manuscript_id'],
            'title': related_content['manuscript_title'],
            'description': related_content['manuscript_authors_csv']
        }
    if related_content['collection_id']:
        assert related_content['collection_curator_name']
        yield {
            'type': 'collection',
            'url': ('https://elifesciences.org/collections/'
                    + related_content['collection_id']
                    + '/meta-research-a-collection-of-articles'),
            'title': related_content['collection_title'],
            'description': (
                'Edited by ' + related_content['collection_curator_name'] + ' et al'
                if related_content['is_collection_curator_et_al']
                else 'Edited by ' + related_content['collection_curator_name']
            ),
            'thumbnail': related_content['collection_thumbnail_url']
        }
    if related_content['podcast_id']:
        yield {
            'type': 'podcastChapterEpisode',
            'url': (
                'https://elifesciences.org/podcast/episode'
                + str(related_content['podcast_id'])
                + '#'
                + str(related_content['podcast_chapter_time'])
            ),
            'title': related_content['podcast_chapter_title']
        }


def iter_elife_manuscript_part_of_section_complement_for_each_record(
    related_content_array: Optional[Sequence[ApiRelatedContentInput]]
) -> Iterable[DocmapPartOfComplement]:
    if related_content_array:
        for related_content in related_content_array:
            yield from iter_elife_manuscript_part_of_section_complement_for_one_record(
                related_content
            )


def get_sorted_elife_manuscript_part_of_section_complement(
    complement_iterable: Iterable[DocmapPartOfComplement]
) -> Sequence[DocmapPartOfComplement]:
    return sorted(complement_iterable, key=lambda complement: complement['url'])


def get_elife_manuscript_part_of_section(
    query_result_item: ApiInput
) -> DocmapPublishedElifeManuscriptPartOf:
    first_manuscript_version = query_result_item['manuscript_versions'][0]
    assert first_manuscript_version['rp_publication_timestamp']
    return {
        'type': 'manuscript',
        'doi': query_result_item['elife_doi'],
        'identifier': query_result_item['manuscript_id'],
        'subjectDisciplines': get_elife_manuscript_subject_disciplines(
            first_manuscript_version['subject_areas']
        ),
        'published': first_manuscript_version['rp_publication_timestamp'].isoformat(),
        'volumeIdentifier': get_elife_manuscript_volume(first_manuscript_version),
        'electronicArticleIdentifier': get_elife_manuscript_electronic_article_identifier(
            query_result_item
        ),
        'complement': get_sorted_elife_manuscript_part_of_section_complement(
            iter_elife_manuscript_part_of_section_complement_for_each_record(
                query_result_item['related_content']
            )
        )
    }


def get_docmap_elife_manuscript_output_for_published_step(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapPublishedElifeManuscriptOutput:
    return {
        **get_docmap_elife_manuscript_output(  # type: ignore
            query_result_item,
            manuscript_version
        ),
        'published': (
            manuscript_version['rp_publication_timestamp'].isoformat()
        ),
        'partOf': get_elife_manuscript_part_of_section(
            query_result_item=query_result_item
        )
    }


def get_docmap_elife_manuscript_output_content_for_vor(
    query_result_item: ApiInput
) -> Sequence[DocmapContent]:
    return [{
        'type': 'web-page',
        'url': 'https://elifesciences.org/articles/' + query_result_item['manuscript_id']
    }]


def get_docmap_elife_manuscript_output_for_vor(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput,
    is_vor: bool = True
) -> DocmapElifeManuscriptVorOutput:
    manuscript_version_doi = get_elife_manuscript_version_doi(
        elife_doi=query_result_item['elife_doi'],
        elife_doi_version_str=manuscript_version['elife_doi_version_str'],
        is_vor=is_vor
    )
    return {
        'type': 'version-of-record',
        'doi': manuscript_version_doi,
        'published': (
            manuscript_version['vor_publication_date'].isoformat()
            if manuscript_version['vor_publication_date']
            else None
        ),
        'url': f'{DOI_ROOT_URL}' + manuscript_version_doi,
        'content': get_docmap_elife_manuscript_output_content_for_vor(
            query_result_item=query_result_item
        )
    }


def get_docmap_elife_manuscript_input(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapElifeManuscriptInput:
    return {
        'type': 'preprint',
        'doi': get_elife_manuscript_version_doi(
            elife_doi=query_result_item['elife_doi'],
            elife_doi_version_str=manuscript_version['elife_doi_version_str']
        ),
        'identifier': query_result_item['manuscript_id'],
        'versionIdentifier': manuscript_version['elife_doi_version_str']
    }
