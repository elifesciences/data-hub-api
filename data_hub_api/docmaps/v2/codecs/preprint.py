
from data_hub_api.docmaps.v2.api_input_typing import ApiManuscriptVersionInput
from data_hub_api.docmaps.v2.docmap_typing import (
    DocmapAssertionItem,
    DocmapContent,
    DocmapPreprintInput,
    DocmapPreprintInputWithPublishedMecaPath
)


def get_docmap_preprint_input(
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapPreprintInput:
    return {
        'type': 'preprint',
        'doi': manuscript_version['preprint_doi'],
        'url': manuscript_version['preprint_url'],
        'versionIdentifier': manuscript_version['preprint_version']
    }


def get_meca_path_content(meca_path: str) -> DocmapContent:
    return {
        'type': 'computer-file',
        'url': meca_path
    }


def get_docmap_preprint_input_with_published_and_meca_path(
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapPreprintInputWithPublishedMecaPath:
    return {
        **get_docmap_preprint_input(manuscript_version),  # type: ignore
        'published': (
            manuscript_version['preprint_published_at_date'].isoformat()
            if manuscript_version['preprint_published_at_date']
            else None
        ),
        'content': (
            [get_meca_path_content(manuscript_version['meca_path'])]
            if manuscript_version['meca_path']
            else None
        )
    }


def get_docmap_preprint_assertion_item(
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapAssertionItem:
    return {
        'type': 'preprint',
        'doi': manuscript_version['preprint_doi'],
        'versionIdentifier': manuscript_version['preprint_version']
    }
