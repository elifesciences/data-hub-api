from typing import Sequence
from data_hub_api.config import DOI_ROOT_URL
from data_hub_api.docmaps.v2.api_input_typing import ApiInput, ApiManuscriptVersionInput
from data_hub_api.docmaps.v2.docmap_typing import (
    DocmapAssertionItem,
    DocmapContent,
    DocmapElifeManuscriptInput,
    DocmapElifeManuscriptOutput,
    DocmapElifeManuscriptVorOutput,
    DocmapPublishedElifeManuscriptOutput,
    DocmapPublishedElifeManuscriptPartOf
)


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


def get_elife_manuscript_part_of_section(
    query_result_item: ApiInput
) -> DocmapPublishedElifeManuscriptPartOf:
    return {
        'type': 'manuscript',
        'doi': query_result_item['elife_doi'],
        'identifier': query_result_item['manuscript_id'],
        'volumeIdentifier': '',
        'electronicArticleIdentifier': ''
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
