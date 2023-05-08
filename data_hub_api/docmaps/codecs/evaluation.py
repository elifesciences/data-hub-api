from typing import Optional

from data_hub_api.docmaps.codecs.elife_manuscript import get_elife_manuscript_version_doi
from data_hub_api.docmaps.docmap_typing import (
    DocmapContent,
    DocmapEvaluationInput,
    DocmapEvaluationOutput
)

DOI_ROOT_URL = 'https://doi.org/'

HYPOTHESIS_URL = 'https://hypothes.is/a/'
SCIETY_ARTICLES_ACTIVITY_URL = 'https://sciety.org/articles/activity/'
SCIETY_ARTICLES_EVALUATIONS_URL = 'https://sciety.org/evaluations/hypothesis:'


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


def get_docmap_evaluation_input(
    query_result_item: dict,
    preprint: dict,
    evaluation_suffix: str,
    docmap_evaluation_type: str
) -> DocmapEvaluationInput:
    elife_evaluation_doi = get_elife_evaluation_doi(
        elife_doi_version_str=preprint['elife_doi_version_str'],
        elife_doi=query_result_item['elife_doi'],
        evaluation_suffix=evaluation_suffix
    )
    return {
        'type': docmap_evaluation_type,
        'doi': elife_evaluation_doi
    }


def get_docmap_evaluation_output_content_url(
    base_url: str,
    hypothesis_id: str,
    preprint_doi: Optional[str] = None
) -> str:
    assert base_url in [
        HYPOTHESIS_URL, SCIETY_ARTICLES_ACTIVITY_URL, SCIETY_ARTICLES_EVALUATIONS_URL
    ]
    if base_url == HYPOTHESIS_URL:
        return base_url + hypothesis_id
    if base_url == SCIETY_ARTICLES_ACTIVITY_URL:
        assert preprint_doi
        return base_url + preprint_doi + '#hypothesis:' + hypothesis_id
    return base_url + hypothesis_id + '/content'


def get_docmap_evaluation_output_content(
    base_url: str,
    hypothesis_id: str,
    preprint_doi: Optional[str] = None
) -> DocmapContent:
    return {
        'type': 'web-page',
        'url': get_docmap_evaluation_output_content_url(
            base_url=base_url,
            hypothesis_id=hypothesis_id,
            preprint_doi=preprint_doi
        )
    }


def get_docmap_evaluation_output(
    query_result_item: dict,
    preprint: dict,
    hypothesis_id: str,
    evaluation_suffix: str,
    annotation_created_timestamp: str,
    docmap_evaluation_type: str
) -> DocmapEvaluationOutput:
    preprint_doi = preprint['preprint_doi']
    elife_evaluation_doi = get_elife_evaluation_doi(
        elife_doi_version_str=preprint['elife_doi_version_str'],
        elife_doi=query_result_item['elife_doi'],
        evaluation_suffix=evaluation_suffix
    )
    return {
        'type': docmap_evaluation_type,
        'published': annotation_created_timestamp,
        'doi': elife_evaluation_doi,
        'license': query_result_item['license'],
        'url': get_elife_evaluation_doi_url(elife_evaluation_doi=elife_evaluation_doi),
        'content': [
            get_docmap_evaluation_output_content(
                base_url=HYPOTHESIS_URL,
                hypothesis_id=hypothesis_id
            ),
            get_docmap_evaluation_output_content(
                base_url=SCIETY_ARTICLES_ACTIVITY_URL,
                hypothesis_id=hypothesis_id,
                preprint_doi=preprint_doi
            ),
            get_docmap_evaluation_output_content(
                base_url=SCIETY_ARTICLES_EVALUATIONS_URL,
                hypothesis_id=hypothesis_id
            )
        ]
    }