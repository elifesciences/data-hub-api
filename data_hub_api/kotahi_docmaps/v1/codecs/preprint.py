from data_hub_api.kotahi_docmaps.v1.api_input_typing import ApiManuscriptVersionInput
from data_hub_api.kotahi_docmaps.v1.docmap_typing import (
    DocmapAssertionItem,
    DocmapPreprintInput,
    DocmapPreprintInputWithPublishedMecaPath
)


def get_docmap_preprint_input(
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapPreprintInput:
    return {
        'type': 'preprint',
        'doi': manuscript_version['preprint_doi']
    }


def get_docmap_preprint_input_with_published(
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapPreprintInputWithPublishedMecaPath:
    return {
        **get_docmap_preprint_input(manuscript_version),  # type: ignore
    }


def get_docmap_preprint_assertion_item(
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapAssertionItem:
    return {
        'type': 'preprint',
        'doi': manuscript_version['preprint_doi']
    }
