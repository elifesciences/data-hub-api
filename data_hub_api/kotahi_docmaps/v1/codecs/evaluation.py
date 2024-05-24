import logging
import re
from typing import Iterable, Optional, Sequence, Tuple, cast

from data_hub_api.kotahi_docmaps.v1.api_input_typing import (
    ApiEditorDetailInput,
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

EVALUATION_URL_PREFIX = (
    'https://data-hub-api.elifesciences.org/kotahi/docmaps/v1/'
    'evaluation/get-by-evaluation-id?evaluation_id='
)

DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY = 'evaluation-summary'
DOCMAP_EVALUATION_TYPE_FOR_REPLY = 'reply'
DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE = 'review-article'


def extract_elife_assessments_from_email(email_body: Optional[str]) -> Optional[str]:
    if email_body:
        pattern = r'[eE][Ll]ife [aA]ssessment(.*?)(?=(?:[Pp]ublic [Rr]eview|-{10,}|\Z))'
        match = re.search(pattern, email_body, re.S)
        if match:
            extracted_text = match.group().strip()
            return extracted_text
        return None
    return None


def extract_elife_public_reviews_from_email(email_body: Optional[str]) -> Optional[str]:
    if email_body:
        pattern = r'(?s)([pP]ublic [rR]eviews?:?\s*\n.*)-{10,}'
        match = re.search(pattern, email_body)
        if match:
            extracted_text = match.group(1).strip()
            return extracted_text
        return None
    return None


def extract_public_review_parts(public_reviews: Optional[str]):
    if public_reviews:
        pattern = r'(?=Reviewer #\d+ \(Public Review\):?)'
        parts = re.split(pattern, public_reviews)
        parts = [part.strip() for part in parts if part.strip()]
        if len(parts) > 1:
            return parts[1:]
        else:
            return None
    return None


def get_evaluation_and_type_list_from_email_body(
    email_body: Optional[str]
) -> Optional[Sequence[dict]]:
    if email_body:
        evalution_list = []

        evaluation_summary_text = extract_elife_assessments_from_email(email_body)
        if evaluation_summary_text:
            evaluation_summary_dict = {
                'evaluation_type': DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY,
                'evaluation_text': evaluation_summary_text
            }
            evalution_list.append(evaluation_summary_dict)

        joint_review_or_public_reviews = extract_elife_public_reviews_from_email(email_body)
        if joint_review_or_public_reviews:
            public_review_parts = extract_public_review_parts(joint_review_or_public_reviews)
            if public_review_parts:
                for public_review in public_review_parts:
                    review_dict = {
                        'evaluation_type': DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE,
                        'evaluation_text': public_review
                    }
                    evalution_list.append(review_dict)
            else:
                joint_review = joint_review_or_public_reviews
                review_dict = {
                    'evaluation_type': DOCMAP_EVALUATION_TYPE_FOR_REVIEW_ARTICLE,
                    'evaluation_text': joint_review
                }
                evalution_list.append(review_dict)

        return evalution_list
    return []


def get_docmap_evaluation_output_content(
    evaluation_url: str
) -> DocmapContent:
    return {
        'type': 'web-page',
        'url': evaluation_url
    }


def get_docmap_evaluation_output(
    docmap_evaluation_type: str,
    evaluation_url: str
) -> DocmapEvaluationOutput:
    return {
        'type': docmap_evaluation_type,
        'content': [get_docmap_evaluation_output_content(evaluation_url)]
    }


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
) -> Optional[DocmapAffiliation]:
    if editor_detail['institution']:
        return {
            'type': 'organization',
            'name': editor_detail['institution'],
            'location': get_docmap_affiliation_location(editor_detail)
        }
    return None


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
    editor_details = [editor_detail.get('institution'), editor_detail.get('country')]
    return ', '.join(filter(None, editor_details))


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
    docmap_evaluation_type: str,
    evaluation_url: str
) -> DocmapAction:
    return {
        'participants': get_docmap_evaluation_participants(
            manuscript_version=manuscript_version,
            docmap_evaluation_type=docmap_evaluation_type
        ),
        'outputs': [
            get_docmap_evaluation_output(
                docmap_evaluation_type=docmap_evaluation_type,
                evaluation_url=evaluation_url
            )
        ]
    }


def generate_evaluation_id(
    long_manuscript_identifier: str,
    evaluation_type: str,
    evaluation_index: int,
) -> str:
    assert long_manuscript_identifier
    assert evaluation_type
    assert evaluation_index
    return (
        f'{long_manuscript_identifier}:'
        f'{evaluation_type}:{evaluation_index}'
    )


def iter_docmap_actions_for_evaluations(
    manuscript_version: ApiManuscriptVersionInput
) -> Iterable[DocmapAction]:
    email_body = manuscript_version['email_body']
    if email_body:
        evaluation_list = get_evaluation_and_type_list_from_email_body(email_body)
        if evaluation_list:
            type_indices = {}
            for evaluation_dict in evaluation_list:
                evaluation_type = evaluation_dict['evaluation_type']
                if evaluation_type not in type_indices:
                    type_indices[evaluation_type] = 1
                else:
                    type_indices[evaluation_type] += 1
                evaluation_index = type_indices[evaluation_type]
                evaluation_id = generate_evaluation_id(
                    manuscript_version['long_manuscript_identifier'],
                    evaluation_type,
                    evaluation_index
                )
                evaluation_url = f'{EVALUATION_URL_PREFIX}{evaluation_id}'
                yield get_docmap_actions_for_evaluations(
                    manuscript_version=manuscript_version,
                    docmap_evaluation_type=evaluation_type,
                    evaluation_url=evaluation_url
                )


def iter_evaluation_id_and_text(
    manuscript_version: ApiManuscriptVersionInput
) -> Iterable[Tuple[str, str]]:
    email_body = manuscript_version['email_body']
    if email_body:
        evaluation_list = get_evaluation_and_type_list_from_email_body(email_body)
        if evaluation_list:
            type_indices = {}
            for evaluation_dict in evaluation_list:
                evaluation_type = evaluation_dict['evaluation_type']
                if evaluation_type not in type_indices:
                    type_indices[evaluation_type] = 1
                else:
                    type_indices[evaluation_type] += 1
                evaluation_index = type_indices[evaluation_type]
                evaluation_id = generate_evaluation_id(
                    manuscript_version['long_manuscript_identifier'],
                    evaluation_type,
                    evaluation_index
                )
                yield evaluation_id, evaluation_dict['evaluation_text']
