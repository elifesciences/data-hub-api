from typing import Optional

from data_hub_api.docmaps.codecs.elife_manuscript import get_elife_manuscript_version_doi

DOI_ROOT_URL = 'https://doi.org/'


def get_elife_evaluation_doi(
    elife_doi_version_str: str,
    elife_doi: Optional[str] = None,
    evaluation_suffix: Optional[str] = None
) -> Optional[str]:
    elife_version_doi = get_elife_manuscript_version_doi(
        elife_doi=elife_doi,
        elife_doi_version_str=elife_doi_version_str
    )
    if not elife_version_doi:
        return None
    if not evaluation_suffix:
        return elife_version_doi
    return elife_version_doi + '.' + evaluation_suffix


def get_elife_evaluation_doi_url(
    elife_evaluation_doi: Optional[str] = None
) -> Optional[str]:
    if not elife_evaluation_doi:
        return None
    return f'{DOI_ROOT_URL}' + elife_evaluation_doi
