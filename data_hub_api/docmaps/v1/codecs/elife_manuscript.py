from typing import Optional
from data_hub_api.docmaps.v1.api_input_typing import ApiInput, ApiPreprintInput
from data_hub_api.docmaps.v1.docmap_typing import (
    DocmapAssertionItem,
    DocmapElifeManuscriptOutput
)


def get_elife_manuscript_version_doi(
    elife_doi_version_str: str,
    elife_doi: Optional[str] = None
) -> Optional[str]:
    if not elife_doi:
        return None
    return elife_doi + '.' + elife_doi_version_str


def get_docmap_elife_manuscript_doi_assertion_item(
    query_result_item: ApiInput,
    preprint: ApiPreprintInput
) -> DocmapAssertionItem:
    return {
        'type': 'preprint',
        'doi': get_elife_manuscript_version_doi(
            elife_doi=query_result_item['elife_doi'],
            elife_doi_version_str=preprint['elife_doi_version_str']
        ),
        'versionIdentifier': preprint['elife_doi_version_str']
    }


def get_docmap_elife_manuscript_output(
    query_result_item: ApiInput,
    preprint: ApiPreprintInput
) -> DocmapElifeManuscriptOutput:
    return {
        'type': 'preprint',
        'identifier': query_result_item['manuscript_id'],
        'doi': get_elife_manuscript_version_doi(
            elife_doi=query_result_item['elife_doi'],
            elife_doi_version_str=preprint['elife_doi_version_str']
        ),
        'versionIdentifier': preprint['elife_doi_version_str'],
        'license': query_result_item['license']
    }
