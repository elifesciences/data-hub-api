from datetime import datetime
import logging
from typing import Iterable, Optional, Sequence, cast, Tuple
from data_hub_api.config import DOI_ROOT_URL

from data_hub_api.docmaps.v2.codecs.elife_manuscript import get_elife_manuscript_version_doi
from data_hub_api.docmaps.v2.api_input_typing import (
    ApiEditorDetailInput,
    ApiEvaluationInput,
    ApiInput,
    ApiManuscriptVersionInput
)
from data_hub_api.docmaps.v2.docmap_typing import (
    DocmapAction,
    DocmapAnonymousActor,
    DocmapEditorActor,
    DocmapAffiliation,
    DocmapContent,
    DocmapEvaluationInput,
    DocmapEvaluationOutput,
    DocmapParticipant
)

LOGGER = logging.getLogger(__name__)

HYPOTHESIS_URL = 'https://hypothes.is/a/'
SCIETY_ARTICLES_ACTIVITY_URL = 'https://sciety.org/articles/activity/'
SCIETY_ARTICLES_EVALUATIONS_URL = 'https://sciety.org/evaluations/hypothesis:'

DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY = 'evaluation-summary'
DOCMAP_EVALUATION_TYPE_FOR_REPLY = 'reply'
DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE = 'review-article'


def get_elife_evaluation_doi(
    elife_doi_version_str: str,
    elife_doi: str,
    evaluation_suffix: str
) -> str:
    elife_version_doi = get_elife_manuscript_version_doi(
        elife_doi=elife_doi,
        elife_doi_version_str=elife_doi_version_str
    )
    return elife_version_doi + '.' + evaluation_suffix


def get_elife_evaluation_doi_url(
    elife_evaluation_doi: Optional[str] = None
) -> Optional[str]:
    if not elife_evaluation_doi:
        return None
    return f'{DOI_ROOT_URL}' + elife_evaluation_doi


def get_docmap_evaluation_input(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput,
    evaluation_suffix: str,
    docmap_evaluation_type: str
) -> DocmapEvaluationInput:
    elife_evaluation_doi = get_elife_evaluation_doi(
        elife_doi_version_str=manuscript_version['elife_doi_version_str'],
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
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput,
    hypothesis_id: str,
    evaluation_suffix: str,
    annotation_created_timestamp: datetime,
    docmap_evaluation_type: str
) -> DocmapEvaluationOutput:
    preprint_doi = manuscript_version['preprint_doi']
    elife_evaluation_doi = get_elife_evaluation_doi(
        elife_doi_version_str=manuscript_version['elife_doi_version_str'],
        elife_doi=query_result_item['elife_doi'],
        evaluation_suffix=evaluation_suffix
    )
    return {
        'type': docmap_evaluation_type,
        'published': annotation_created_timestamp.isoformat(),
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


def has_tag_containing(tags: list, text: str) -> bool:
    return any(
        text in tag
        for tag in tags
    )


def get_docmap_evaluation_type_form_tags(
    tags: list
) -> Optional[str]:
    has_author_response_tag = has_tag_containing(tags, 'AuthorResponse')
    has_summary_tag = has_tag_containing(tags, 'Summary')
    has_review_tag = has_tag_containing(tags, 'Review')
    assert not (has_author_response_tag and has_summary_tag)
    if has_author_response_tag:
        return DOCMAP_EVALUATION_TYPE_FOR_REPLY
    if has_summary_tag:
        return DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY
    if has_review_tag:
        return DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE
    return None


def get_docmap_actor_for_review_article_type() -> DocmapAnonymousActor:
    return {
        'name': 'anonymous',
        'type': 'person'
    }


def get_docmap_evaluation_participants_for_review_article_type() -> Sequence[DocmapParticipant]:
    return [{
        'actor': get_docmap_actor_for_review_article_type(),
        'role': 'peer-reviewer'
    }]


def get_docmap_affiliation_location(
    editor_detail: ApiEditorDetailInput
) -> Optional[str]:
    if editor_detail['city'] and editor_detail['country']:
        return editor_detail['city'] + ', ' + editor_detail['country']
    return editor_detail['country']


def get_docmap_affiliation(
    editor_detail: ApiEditorDetailInput
) -> DocmapAffiliation:
    return {
        'type': 'organization',
        'name': editor_detail['institution'],
        'location': get_docmap_affiliation_location(editor_detail)
    }


def get_docmap_actor_for_evaluation_summary_type(
    editor_detail: ApiEditorDetailInput
) -> DocmapEditorActor:
    return {
        'type': 'person',
        'name': editor_detail['name'],
        'firstName': editor_detail['first_name'],
        '_middleName': (editor_detail['middle_name'] if editor_detail['middle_name'] else None),
        'surname': editor_detail['last_name'],
        '_relatesToOrganization': get_related_organization_detail(editor_detail),
        'affiliation': get_docmap_affiliation(editor_detail)
    }


def get_related_organization_detail(
    editor_detail: ApiEditorDetailInput
) -> str:
    if editor_detail['country']:
        return editor_detail['institution'] + ', ' + editor_detail['country']
    return editor_detail['institution']


def get_docmap_evaluation_participants_for_evaluation_summary_type(
    editor_detail: ApiEditorDetailInput,
    role: str
) -> DocmapParticipant:
    assert role in ['editor', 'senior-editor']
    return {
        'actor': get_docmap_actor_for_evaluation_summary_type(editor_detail),
        'role': role
    }


def get_docmap_evaluation_participants_for_evalution_summary_type(
    editor_details_list: Sequence[ApiEditorDetailInput],
    senior_editor_details_list: Sequence[ApiEditorDetailInput]
) -> Sequence[DocmapParticipant]:
    participants = []
    for editor_detail in editor_details_list:
        single_editor_dict = get_docmap_evaluation_participants_for_evaluation_summary_type(
            editor_detail=editor_detail,
            role='editor'
        )
        participants.append(single_editor_dict)
    for senior_editor_detail in senior_editor_details_list:
        single_senior_editor_dict = get_docmap_evaluation_participants_for_evaluation_summary_type(
            editor_detail=senior_editor_detail,
            role='senior-editor'
        )
        participants.append(single_senior_editor_dict)
    return cast(Sequence[DocmapParticipant], participants)


def get_docmap_evaluation_participants(
    manuscript_version: ApiManuscriptVersionInput,
    docmap_evaluation_type: str
) -> Sequence[DocmapParticipant]:
    editor_details_list = manuscript_version['editor_details']
    senior_editor_details_list = manuscript_version['senior_editor_details']
    if docmap_evaluation_type == DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE:
        return get_docmap_evaluation_participants_for_review_article_type()
    if docmap_evaluation_type == DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY:
        return get_docmap_evaluation_participants_for_evalution_summary_type(
            editor_details_list=editor_details_list,
            senior_editor_details_list=senior_editor_details_list
        )
    return []


def get_docmap_actions_for_evaluations(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput,
    hypothesis_id: str,
    evaluation_suffix: str,
    annotation_created_timestamp: datetime,
    docmap_evaluation_type: str
) -> DocmapAction:
    return {
        'participants': get_docmap_evaluation_participants(
            manuscript_version=manuscript_version,
            docmap_evaluation_type=docmap_evaluation_type
        ),
        'outputs': [
            get_docmap_evaluation_output(
                query_result_item=query_result_item,
                manuscript_version=manuscript_version,
                hypothesis_id=hypothesis_id,
                annotation_created_timestamp=annotation_created_timestamp,
                evaluation_suffix=evaluation_suffix,
                docmap_evaluation_type=docmap_evaluation_type
            )
        ]
    }


def iter_evaluation_and_type_for_related_preprint_url(
    evaluations: Sequence[ApiEvaluationInput],
    preprint_url: str
) -> Iterable[Tuple[ApiEvaluationInput, str]]:
    for evaluation in evaluations:
        docmap_evaluation_type = get_docmap_evaluation_type_form_tags(evaluation['tags'])
        evaluation_preprint_url = evaluation['uri']
        if evaluation_preprint_url != preprint_url:
            LOGGER.debug(
                'ignoring evaluation on another version: %r != %r',
                evaluation_preprint_url, preprint_url
            )
            continue
        if docmap_evaluation_type in (
            DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY,
            DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE,
            DOCMAP_EVALUATION_TYPE_FOR_REPLY
        ):
            yield evaluation, docmap_evaluation_type


def iter_docmap_actions_for_evaluations(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
) -> Iterable[DocmapAction]:
    evaluations = manuscript_version['evaluations']
    preprint_url = manuscript_version['preprint_url']
    for evaluation, docmap_evaluation_type in iter_evaluation_and_type_for_related_preprint_url(
        evaluations,
        preprint_url
    ):
        hypothesis_id = evaluation['hypothesis_id']
        annotation_created_timestamp = evaluation['annotation_created_timestamp']
        evaluation_suffix = evaluation['evaluation_suffix']
        yield get_docmap_actions_for_evaluations(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version,
            hypothesis_id=hypothesis_id,
            annotation_created_timestamp=annotation_created_timestamp,
            evaluation_suffix=evaluation_suffix,
            docmap_evaluation_type=docmap_evaluation_type
        )


def iter_docmap_evaluation_input(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
):
    evaluations = manuscript_version['evaluations']
    preprint_url = manuscript_version['preprint_url']
    for evaluation, docmap_evaluation_type in iter_evaluation_and_type_for_related_preprint_url(
        evaluations,
        preprint_url
    ):
        evaluation_suffix = evaluation['evaluation_suffix']
        yield get_docmap_evaluation_input(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version,
            evaluation_suffix=evaluation_suffix,
            docmap_evaluation_type=docmap_evaluation_type
        )
