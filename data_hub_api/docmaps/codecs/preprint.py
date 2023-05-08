
from data_hub_api.docmaps.docmap_typing import (
    DocmapAssertionItem,
    DocmapPreprintInput,
    DocmapPreprintOutput
)


def get_docmap_preprint_output(preprint: dict) -> DocmapPreprintOutput:
    preprint_doi = preprint['preprint_doi']
    preprint_published_at_date = preprint['preprint_published_at_date']
    return {
        'type': 'preprint',
        'doi': preprint_doi,
        'url': preprint['preprint_url'],
        'published': (
            preprint_published_at_date.isoformat()
            if preprint_published_at_date
            else None
        ),
        'versionIdentifier': preprint['preprint_version'],
        '_tdmPath': preprint['tdm_path']
    }


def get_docmap_preprint_input(preprint: dict) -> DocmapPreprintInput:
    return {
        'type': 'preprint',
        'doi': preprint['preprint_doi'],
        'url': preprint['preprint_url'],
        'versionIdentifier': preprint['preprint_version']
    }


def get_docmap_preprint_assertion_item(preprint: dict) -> DocmapAssertionItem:
    return {
        'type': 'preprint',
        'doi': preprint['preprint_doi'],
        'versionIdentifier': preprint['preprint_version']
    }
