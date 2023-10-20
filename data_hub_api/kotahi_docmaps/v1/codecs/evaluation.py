import logging
import re
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


def extract_elife_assessments_from_email(evaluation_email: str):
    pattern = r'(?s)([eE][Ll]ife [aA]ssessment(.*?))-{10,}'
    match = re.search(pattern, evaluation_email)
    if match:
        extracted_text = match.group(1).strip()
        return extracted_text
    return None


def get_evaluation_and_type_list_from_email(evaluation_email: str):
    evalution_list = []
    evaluation_summary_dict = {
        'evaluation_type': DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY,
        'evaluation_text': extract_elife_assessments_from_email(evaluation_email)
    }
    evalution_list.append(evaluation_summary_dict)
    return evalution_list


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



def iter_docmap_actions_for_evaluations(
    manuscript_version: ApiManuscriptVersionInput
) -> Iterable[DocmapAction]:
    evaluation_emails = manuscript_version['evaluation_emails']
    for _evaluation in evaluation_emails:
        yield get_docmap_actions_for_evaluations(
            manuscript_version=manuscript_version,
            docmap_evaluation_type=DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY
        )
