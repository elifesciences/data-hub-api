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
            'published': query_result_item['qc_complete_timestamp'],
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


def get_outputs_type_form_tags(
    tags: list
) -> Optional[str]:
    if len(tags) > 1 and 'AuthorResponse' in tags:
        for tag in tags:
            assert 'Summary' not in tag
    for tag in tags:
        if 'AuthorResponse' in tag:
            return 'author-response'
    for tag in tags:
        if 'Summary' in tag:
            return 'evaluation-summary'
    for tag in tags:
        if 'Review' in tag:
            return 'review-article'
    return None


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
        'participants': [],
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


def generate_docmap_steps(number_of_steps: int, query_result_item: dict) -> dict:
    step_number = 0
    steps_dict = {}
    while step_number < number_of_steps:
        LOGGER.debug('step_number: %r', step_number)
        step_ranking_dict = {
            'next-step': (
                '_:b' + str(step_number + 1) if step_number + 1 < number_of_steps else None
            ),
            'previous-step': '_:b' + str(step_number - 1) if step_number > 0 else None
        }
        if step_number == 0:  # manuscript-published
            step_dict = get_docmaps_step_for_manuscript_published_status(
                query_result_item=query_result_item
            )
        elif step_number == 1:  # under-review
            step_dict = get_docmaps_step_for_under_review_status(
                query_result_item=query_result_item
            )
        elif step_number == 2:  # peer-reviewed
            step_dict = get_docmaps_step_for_peer_reviewed_status(
                query_result_item=query_result_item
            )
        steps_dict['_:b'+str(step_number)] = dict(step_dict, **step_ranking_dict)
        step_number += 1
    return remove_key_with_none_value_only(steps_dict)


def get_docmap_step_count_for_query_result_item(query_result_item: dict) -> int:
    # currently maximum step we handle is peer-reviewed (which is 3)
    if not query_result_item['evaluations']:
        return 2
    return 3


def get_docmap_item_for_query_result_item(query_result_item: dict) -> dict:
    qc_complete_timestamp_str = query_result_item['qc_complete_timestamp'].isoformat()
    publisher_json = query_result_item['publisher_json']
    number_of_steps = get_docmap_step_count_for_query_result_item(
        query_result_item=query_result_item
    )
    LOGGER.debug('publisher_json: %r', publisher_json)
    LOGGER.debug('number_of_steps: %r', number_of_steps)
    return {
        '@context': DOCMAPS_JSONLD_SCHEMA_URL,
        'type': 'docmap',
        'id': DOCMAP_ID_PREFIX + query_result_item['docmap_id'] + DOCMAP_ID_SUFFIX,
        'created': qc_complete_timestamp_str,
        'updated': qc_complete_timestamp_str,
        'publisher': json.loads(publisher_json),
        'first-step': '_:b0',
        'steps': generate_docmap_steps(number_of_steps, query_result_item)
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
