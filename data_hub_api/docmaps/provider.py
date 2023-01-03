import logging
import json
from pathlib import Path
from typing import Iterable, Optional

from data_hub_api.utils.bigquery import (
    iter_dict_from_bq_query
)
from data_hub_api.docmaps.sql import get_sql_path
from data_hub_api.utils.json import remove_key_with_none_value_only


LOGGER = logging.getLogger(__name__)

DOCMAPS_JSONLD_SCHEMA_URL = 'https://w3id.org/docmaps/context.jsonld'

DOCMAP_ID_PREFIX = 'https://data-hub-api.elifesciences.org/enhanced-preprints/docmaps/v1/articles/'
DOCMAP_ID_SUFFIX = '/docmap.json'

DOI_ROOT_URL = 'https://doi.org/'
ELIFE_REVIEWED_PREPRINTS_URL = 'https://elifesciences.org/reviewed-preprints/'
HYPOTHESIS_URL = 'https://hypothes.is/a/'
SCIETY_ARTICLES_ACTIVITY_URL = 'https://sciety.org/articles/activity/'
SCIETY_ARTICLES_EVALUATIONS_URL = 'https://sciety.org/evaluations/hypothesis:'


def get_docmap_assertions_value_for_preprint_manuscript_published_step(
    query_result_item: dict
) -> list:
    return [{
        'item': {
            'type': 'preprint',
            'doi': query_result_item['preprint_doi'],
            'versionIdentifier': ''
        },
        'status': 'manuscript-published'
    }]


def get_docmap_actions_value_for_preprint_manuscript_published_step(
    query_result_item: dict
) -> list:
    preprint_doi = query_result_item['preprint_doi']
    return [{
        'participants': [],
        'outputs': [{
            'type': 'preprint',
            'doi': preprint_doi,
            'url': f'{DOI_ROOT_URL}{preprint_doi}',
            'published': '',
            'versionIdentifier': ''
        }]
    }]


def get_docmaps_step_for_manuscript_published_status(
    query_result_item
) -> dict:
    return {
        'actions': get_docmap_actions_value_for_preprint_manuscript_published_step(
            query_result_item=query_result_item
        ),
        'assertions': get_docmap_assertions_value_for_preprint_manuscript_published_step(
            query_result_item=query_result_item
        ),
        'inputs': []
    }


def get_docmap_assertions_value_for_preprint_under_review_step(
    query_result_item: dict
) -> list:
    return [{
        'item': {
            'type': 'preprint',
            'doi': query_result_item['preprint_doi'],
            'versionIdentifier': ''
        },
        'status': 'under-review',
        'happened': query_result_item['qc_complete_timestamp']
    }, {
        'item': {
            'type': 'preprint',
            'doi': query_result_item['elife_doi'],
            'versionIdentifier': ''
        },
        'status': 'draft'
    }]


def get_docmap_actions_value_for_preprint_under_review_step(
    query_result_item: dict
) -> list:
    manuscript_id = query_result_item['manuscript_id']
    elife_doi = query_result_item['elife_doi']
    elife_doi_url = f'{DOI_ROOT_URL}{elife_doi}'
    return [{
        'participants': [],
        'outputs': [{
            'identifier': manuscript_id,
            'versionIdentifier': '',
            'type': 'preprint',
            'doi': elife_doi,
            'url': elife_doi_url,
            'content': [{
                'type': 'web-page',
                'url': f'{ELIFE_REVIEWED_PREPRINTS_URL}{manuscript_id}'
            }]
        }]
    }]


def get_docmap_inputs_value_for_review_steps(
    query_result_item: dict
) -> list:
    return [{
        'type': 'preprint',
        'doi': query_result_item['preprint_doi'],
        'url': query_result_item['preprint_url'],
    }]


def get_docmaps_step_for_under_review_status(
    query_result_item
):
    return {
        'actions': get_docmap_actions_value_for_preprint_under_review_step(
            query_result_item=query_result_item
        ),
        'assertions': get_docmap_assertions_value_for_preprint_under_review_step(
            query_result_item=query_result_item
        ),
        'inputs': get_docmap_inputs_value_for_review_steps(
            query_result_item=query_result_item
        )
    }


def get_docmap_assertions_value_for_preprint_peer_reviewed_step(
    query_result_item: dict
) -> list:
    return [{
        'item': {
            'type': 'preprint',
            'doi': query_result_item['preprint_doi'],
            'versionIdentifier': ''
        },
        'status': 'peer-reviewed'
    }]


def has_tag_containing(tags: list, text: str) -> bool:
    return any(text in tag for tag in tags)


def get_outputs_type_form_tags(
    tags: list
) -> Optional[str]:
    has_author_response_tag = has_tag_containing(tags, 'AuthorResponse')
    has_summary_tag = has_tag_containing(tags, 'Summary')
    has_review_tag = has_tag_containing(tags, 'Review')
    assert not (has_author_response_tag and has_summary_tag)
    if has_author_response_tag:
        return 'author-response'
    if has_summary_tag:
        return 'evaluation-summary'
    if has_review_tag:
        return 'review-article'
    return None


def get_participants_for_peer_reviewed_review_article_type() -> list:
    return [
        {
            'actor': {
                'name': 'anonymous',
                'type': 'person'
            },
            'role': 'peer-reviewer'
        }
    ]


def get_participants_for_peer_reviewed_evalution_summary_type(
    editor_names_list,
    senior_editor_names_list
) -> list:
    participants = []
    for editor_name in editor_names_list:
        single_editor_dict = {
            'actor': {
                'name': editor_name,
                'type': 'person'
            },
            'role': 'editor'
        }
        participants.append(single_editor_dict)
    for senior_editor_name in senior_editor_names_list:
        single_senior_editor_dict = {
            'actor': {
                'name': senior_editor_name,
                'type': 'person'
            },
            'role': 'senior-editor'
        }
        participants.append(single_senior_editor_dict)
    return participants


def get_participants_for_preprint_peer_reviewed_step(
    query_result_item: dict,
    outputs_type: str
) -> list:
    editor_names_list = query_result_item['editor_names']
    senior_editor_names_list = query_result_item['senior_editor_names']
    if outputs_type == 'review-article':
        return get_participants_for_peer_reviewed_review_article_type()
    return get_participants_for_peer_reviewed_evalution_summary_type(
        editor_names_list=editor_names_list,
        senior_editor_names_list=senior_editor_names_list
    )


def get_single_actions_value_for_preprint_peer_reviewed_step(
    query_result_item: dict,
    hypothesis_id: str,
    annotation_created_timestamp: str,
    outputs_type: str
) -> dict:
    preprint_doi = query_result_item['preprint_doi']
    elife_doi = query_result_item['elife_doi']
    elife_doi_url = f'{DOI_ROOT_URL}{elife_doi}'
    return {
        'participants': get_participants_for_preprint_peer_reviewed_step(
            query_result_item=query_result_item,
            outputs_type=outputs_type
        ),
        'outputs': [
            {
                'type': outputs_type,
                'doi': elife_doi,
                'published': annotation_created_timestamp,
                'url': elife_doi_url,
                'content': [
                    {
                        'type': 'web-page',
                        'url': f'{HYPOTHESIS_URL}{hypothesis_id}'
                    },
                    {
                        'type': 'web-page',
                        'url': (
                            f'{SCIETY_ARTICLES_ACTIVITY_URL}'
                            f'{preprint_doi}#hypothesis:{hypothesis_id}'
                        )
                    },
                    {
                        'type': 'web-page',
                        'url': (
                            f'{SCIETY_ARTICLES_EVALUATIONS_URL}'
                            f'{hypothesis_id}/content'
                        )
                    }
                ]
            }
        ]
    }


def iter_single_actions_value_from_query_result_for_peer_reviewed_step(
    query_result_item: dict
) -> Iterable[dict]:
    evaluations = query_result_item['evaluations']
    for evaluation in evaluations:
        hypothesis_id = evaluation['hypothesis_id']
        annotation_created_timestamp = evaluation['annotation_created_timestamp']
        outputs_type = get_outputs_type_form_tags(evaluation['tags'])
        if outputs_type in ('evaluation-summary', 'review-article'):
            yield get_single_actions_value_for_preprint_peer_reviewed_step(
                query_result_item=query_result_item,
                hypothesis_id=hypothesis_id,
                annotation_created_timestamp=annotation_created_timestamp,
                outputs_type=outputs_type
            )


def get_docmaps_step_for_peer_reviewed_status(
    query_result_item
):
    return {
        'actions': list(iter_single_actions_value_from_query_result_for_peer_reviewed_step(
            query_result_item=query_result_item
            )
        ),
        'assertions': get_docmap_assertions_value_for_preprint_peer_reviewed_step(
            query_result_item=query_result_item
        ),
        'inputs': get_docmap_inputs_value_for_review_steps(
            query_result_item=query_result_item
        )
    }


def iter_docmap_steps_for_query_result_item(query_result_item: dict) -> Iterable[dict]:
    yield get_docmaps_step_for_manuscript_published_status(query_result_item)
    yield get_docmaps_step_for_under_review_status(query_result_item)
    if query_result_item['evaluations']:
        yield get_docmaps_step_for_peer_reviewed_status(query_result_item)


def generate_docmap_steps(step_itearble: Iterable[dict]) -> dict:
    steps_dict = {}
    step_list = list(step_itearble)
    for step_index, step in enumerate(step_list):
        LOGGER.debug('step_index: %r', step_index)
        step_ranking_dict = {
            'next-step': ('_:b' + str(step_index + 1) if step_index + 1 < len(step_list) else None),
            'previous-step': '_:b' + str(step_index - 1) if step_index > 0 else None
        }
        steps_dict['_:b'+str(step_index)] = dict(step, **step_ranking_dict)
    return remove_key_with_none_value_only(steps_dict)


def get_docmap_item_for_query_result_item(query_result_item: dict) -> dict:
    qc_complete_timestamp_str = query_result_item['qc_complete_timestamp'].isoformat()
    publisher_json = query_result_item['publisher_json']
    LOGGER.debug('publisher_json: %r', publisher_json)
    return {
        '@context': DOCMAPS_JSONLD_SCHEMA_URL,
        'type': 'docmap',
        'id': DOCMAP_ID_PREFIX + query_result_item['docmap_id'] + DOCMAP_ID_SUFFIX,
        'created': qc_complete_timestamp_str,
        'updated': qc_complete_timestamp_str,
        'publisher': json.loads(publisher_json),
        'first-step': '_:b0',
        'steps': generate_docmap_steps(iter_docmap_steps_for_query_result_item(query_result_item))
    }


class DocmapsProvider:
    def __init__(
        self,
        gcp_project_name: str = 'elife-data-pipeline',
        only_include_reviewed_preprint_type: bool = True,
        only_include_evaluated_preprints: bool = False
    ) -> None:
        self.gcp_project_name = gcp_project_name
        self.docmaps_index_query = (
            Path(get_sql_path('docmaps_index.sql')).read_text(encoding='utf-8')
        )
        assert not (only_include_reviewed_preprint_type and only_include_evaluated_preprints)
        if only_include_reviewed_preprint_type:
            self.docmaps_index_query += '\nWHERE is_reviewed_preprint_type'
        if only_include_evaluated_preprints:
            self.docmaps_index_query += '\nWHERE has_evaluations\nLIMIT 20'

    def iter_docmaps(self) -> Iterable[dict]:
        bq_result_iterable = iter_dict_from_bq_query(
            self.gcp_project_name,
            self.docmaps_index_query
        )
        for bq_result in bq_result_iterable:
            yield get_docmap_item_for_query_result_item(bq_result)

    def get_docmaps_index(self) -> dict:
        article_docmaps_list = list(self.iter_docmaps())
        return {'docmaps': article_docmaps_list}
