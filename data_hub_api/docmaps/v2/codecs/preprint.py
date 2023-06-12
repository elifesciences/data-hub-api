
from data_hub_api.docmaps.v2.api_input_typing import ApiManuscriptDetailInput
from data_hub_api.docmaps.v2.docmap_typing import (
    DocmapAssertionItem,
    DocmapPreprintInput
)


def get_docmap_preprint_input(
    manuscript_detail: ApiManuscriptDetailInput,
    detailed: bool
) -> DocmapPreprintInput:
    if not detailed:
        return {
            'type': 'preprint',
            'doi': manuscript_detail['preprint_doi'],
            'url': manuscript_detail['preprint_url'],
            'versionIdentifier': manuscript_detail['preprint_version']
        }
    return {
        'type': 'preprint',
        'doi': manuscript_detail['preprint_doi'],
        'url': manuscript_detail['preprint_url'],
        'versionIdentifier': manuscript_detail['preprint_version'],
        'published': (
            manuscript_detail['preprint_published_at_date'].isoformat()
            if manuscript_detail['preprint_published_at_date']
            else ''
        ),
        '_tdmPath': manuscript_detail['tdm_path'],
    }


def get_docmap_preprint_assertion_item(
    manuscript_detail: ApiManuscriptDetailInput
) -> DocmapAssertionItem:
    return {
        'type': 'preprint',
        'doi': manuscript_detail['preprint_doi'],
        'versionIdentifier': manuscript_detail['preprint_version']
    }
