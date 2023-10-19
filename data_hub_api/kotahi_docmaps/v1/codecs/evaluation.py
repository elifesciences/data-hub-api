import re
import logging
from typing import Iterable, Optional, Sequence, cast, Tuple
from data_hub_api.config import DOI_ROOT_URL

from data_hub_api.kotahi_docmaps.v1.codecs.elife_manuscript import get_elife_manuscript_version_doi
from data_hub_api.kotahi_docmaps.v1.api_input_typing import (
    ApiEditorDetailInput,
    ApiEvaluationEmailInput,
    ApiManuscriptVersionInput
)
from data_hub_api.kotahi_docmaps.v1.docmap_typing import (
    DocmapAction,
    DocmapAnonymousActor,
    DocmapEditorActor,
    DocmapAffiliation,
    DocmapContent,
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


def get_docmap_evaluation_output_content() -> DocmapContent:
    return {
        'type': 'web-page',
        'url': 'TODO'
    }


def get_docmap_evaluation_output(
    docmap_evaluation_type: str
) -> DocmapEvaluationOutput:
    return {
        'type': docmap_evaluation_type,
        'content': [get_docmap_evaluation_output_content()]
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
    manuscript_version: ApiManuscriptVersionInput,
    docmap_evaluation_type: str
) -> DocmapAction:
    return {
        'participants': get_docmap_evaluation_participants(
            manuscript_version=manuscript_version,
            docmap_evaluation_type=docmap_evaluation_type
        ),
        'outputs': [
            get_docmap_evaluation_output(
                docmap_evaluation_type=docmap_evaluation_type
            )
        ]
    }


def iter_evaluation_and_type_for_related_preprint_url(
    evaluations: Sequence[ApiEvaluationEmailInput],
    preprint_url: str
) -> Iterable[Tuple[ApiEvaluationEmailInput, str]]:
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
    manuscript_version: ApiManuscriptVersionInput
) -> Iterable[DocmapAction]:
    evaluations = manuscript_version['evaluations']
    preprint_url = manuscript_version['preprint_url']
    for _evaluation, docmap_evaluation_type in iter_evaluation_and_type_for_related_preprint_url(
        evaluations,
        preprint_url
    ):
        yield get_docmap_actions_for_evaluations(
            manuscript_version=manuscript_version,
            docmap_evaluation_type=docmap_evaluation_type
        )
