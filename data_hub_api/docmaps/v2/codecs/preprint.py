
from data_hub_api.docmaps.v2.api_input_typing import ApiPreprintInput
from data_hub_api.docmaps.v2.docmap_typing import (
    DocmapAssertionItem,
    DocmapPreprintInput
)


def get_docmap_preprint_input(
    preprint: ApiPreprintInput,
    detailed: bool
) -> DocmapPreprintInput:
    if not detailed:
        return {
            'type': 'preprint',
            'doi': preprint['preprint_doi'],
            'url': preprint['preprint_url'],
            'versionIdentifier': preprint['preprint_version']
        }
    return {
        'type': 'preprint',
        'doi': preprint['preprint_doi'],
        'url': preprint['preprint_url'],
        'versionIdentifier': preprint['preprint_version'],
        'published': (
            preprint['preprint_published_at_date'].isoformat()
            if preprint['preprint_published_at_date']
            else ''
        ),
        '_tdmPath': preprint['tdm_path'],
    }


def get_docmap_preprint_assertion_item(preprint: ApiPreprintInput) -> DocmapAssertionItem:
    return {
        'type': 'preprint',
        'doi': preprint['preprint_doi'],
        'versionIdentifier': preprint['preprint_version']
    }
