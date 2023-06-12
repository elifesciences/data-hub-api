from typing import Optional
from data_hub_api.docmaps.v2.api_input_typing import ApiInput, ApiManuscriptDetailInput
from data_hub_api.docmaps.v2.docmap_typing import (
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
    manuscript_detail: ApiManuscriptDetailInput
) -> DocmapAssertionItem:
    return {
        'type': 'preprint',
        'doi': get_elife_manuscript_version_doi(
            elife_doi=query_result_item['elife_doi'],
            elife_doi_version_str=manuscript_detail['elife_doi_version_str']
        ),
        'versionIdentifier': manuscript_detail['elife_doi_version_str']
    }


def get_docmap_elife_manuscript_output(
    query_result_item: ApiInput,
    manuscript_detail: ApiManuscriptDetailInput
) -> DocmapElifeManuscriptOutput:
    return {
        'type': 'preprint',
        'identifier': query_result_item['manuscript_id'],
        'doi': get_elife_manuscript_version_doi(
            elife_doi=query_result_item['elife_doi'],
            elife_doi_version_str=manuscript_detail['elife_doi_version_str']
        ),
        'versionIdentifier': manuscript_detail['elife_doi_version_str'],
        'published': '',
        'license': query_result_item['license']
    }
