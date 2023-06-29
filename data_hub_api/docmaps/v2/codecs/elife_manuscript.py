from typing import Sequence
from data_hub_api.docmaps.v2.api_input_typing import ApiInput, ApiManuscriptVersionInput
from data_hub_api.docmaps.v2.docmap_typing import (
    DocmapAssertionItem,
    DocmapElifeManuscriptInput,
    DocmapElifeManuscriptOutput
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


def get_docmap_elife_manuscript_doi_assertion_item_for_vor_published_step(
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


def get_docmap_elife_manuscript_input(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
) -> Sequence[DocmapElifeManuscriptInput]:
    return [{
        'type': 'preprint',
        'doi': get_elife_manuscript_version_doi(
            elife_doi=query_result_item['elife_doi'],
            elife_doi_version_str=manuscript_version['elife_doi_version_str']
        ),
        'identifier': query_result_item['manuscript_id'],
        'versionIdentifier': manuscript_version['elife_doi_version_str']
    }]
