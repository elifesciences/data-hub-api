from typing import Optional, Sequence
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
from data_hub_api.utils.json import remove_key_with_none_value_only


def get_elife_manuscript_version_doi(
    elife_doi_version_str: str,
    elife_doi: str
) -> str:
    return elife_doi + '.' + elife_doi_version_str


def get_docmap_elife_manuscript_doi_assertion_item(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapAssertionItem:
    return {
        'type': 'preprint',
        'doi': get_elife_manuscript_version_doi(
            elife_doi=query_result_item['elife_doi'],
            elife_doi_version_str=manuscript_version['elife_doi_version_str']
        ),
        'versionIdentifier': manuscript_version['elife_doi_version_str']
    }


def get_docmap_elife_manuscript_doi_assertion_item_for_vor(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapAssertionItem:
    return {
        **get_docmap_elife_manuscript_doi_assertion_item(  # type: ignore
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
        ),
        'type': 'version-of-record'
    }


def get_docmap_elife_manuscript_output(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapElifeManuscriptOutput:
    return {
        'type': 'preprint',
        'identifier': query_result_item['manuscript_id'],
        'doi': get_elife_manuscript_version_doi(
            elife_doi=query_result_item['elife_doi'],
            elife_doi_version_str=manuscript_version['elife_doi_version_str']
        ),
        'versionIdentifier': manuscript_version['elife_doi_version_str'],
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


def get_elife_manuscript_part_of_section_complement(
    related_content: Optional[ApiRelatedContentInput]
) -> Optional[Sequence[DocmapPartOfComplement]]:
    related_article_dict: Optional[dict] = None
    collection_dict: Optional[dict] = None
    podcast_dict: Optional[dict] = None
    if related_content and any(related_content.values()):
        if related_content['manuscript_id']:
            related_article_dict = {
                'type': related_content['manuscript_type'],
                'url': 'https://elifesciences.org/articles/' + related_content['manuscript_id'],
                'title': related_content['manuscript_title'],
                'description': related_content['manuscript_authors_csv']
            }
        if related_content['collection_id']:
            assert related_content['collection_curator_name']
            collection_dict = {
                'type': 'Collection',
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
            podcast_dict = {
                'type': 'Podcast',
                'url': 'https://elifesciences.org/podcast/episode'+ related_content['podcast_id'],
                'title': related_content['podcast_title'],
                'description': related_content['podcast_desc']
            }
        return remove_key_with_none_value_only(
            [related_article_dict, collection_dict, podcast_dict]
        )  # type: ignore
    return None


def get_elife_manuscript_part_of_section(
    query_result_item: ApiInput
) -> DocmapPublishedElifeManuscriptPartOf:
    first_manuscript_version = query_result_item['manuscript_versions'][0]
    assert first_manuscript_version['rp_publication_timestamp']
    related_content = (
        query_result_item['related_content'][0]
        if query_result_item['related_content']
        else None
    )
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
        'complement': get_elife_manuscript_part_of_section_complement(related_content)
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
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapElifeManuscriptVorOutput:
    manuscript_version_doi = get_elife_manuscript_version_doi(
        elife_doi=query_result_item['elife_doi'],
        elife_doi_version_str=manuscript_version['elife_doi_version_str']
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
