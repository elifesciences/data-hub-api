import logging
import json
from pathlib import Path
from typing import Iterable


from data_hub_api.utils.bigquery import (
    iter_dict_from_bq_query
)
from data_hub_api.docmaps.sql import get_sql_path
from data_hub_api.utils.json import remove_key_with_none_value_only


LOGGER = logging.getLogger(__name__)

DOCMAPS_JSONLD_SCHEMA_URL = 'https://w3id.org/docmaps/context.jsonld'

DOCMAP_ID_PREFIX = 'https://data-hub-api.elifesciences.org/enhanced-preprints/docmaps/v1/articles/'
DOCMAP_ID_SUFFIX = '/docmap.json'


def get_docmap_inputs_value_from_query_result(
    step_number: int,
    query_result_item: dict
) -> list:
    if step_number == 0:
        return []
    return [{
        'type': 'preprint',
        'doi': query_result_item['preprint_doi'],
        'url': query_result_item['preprint_url'],
    }]


def get_docmap_assertions_value_from_query_result(
    step_number: int,
    query_result_item: dict
) -> list:
    preprint_doi = query_result_item['preprint_doi']
    elife_doi = query_result_item['elife_doi']
    if step_number == 0:
        return [{
            'item': {
                'type': 'preprint',
                'doi': preprint_doi
            },
            'status': 'manuscript-published'
        }]
    return [
        {
            'item': {
                'type': 'preprint',
                'doi': preprint_doi
            },
            'status': 'under-review'
        },
        {
            'item': {
                'type': 'preprint',
                'doi': elife_doi
            },
            'status': 'draft'
        }
    ]


def iter_single_actions_value_from_query_result_for_evaluations(
    step_number: int,
    query_result_item: dict
) -> Iterable[dict]:
    preprint_doi = query_result_item["preprint_doi"]
    evaluations = query_result_item['evaluations']
    elife_doi = query_result_item['elife_doi']
    url = f'https://doi.org/{elife_doi}'
    if evaluations:
        for evaluation in evaluations:
            hypothesis_id = evaluation["hypothesis_id"]
            yield {
                'participants': [],
                'outputs': [
                    {
                        'type': '',
                        'doi': elife_doi,
                        'published': (
                            evaluation['annotation_created_timestamp'] if evaluations else ''
                        ),
                        'url': url,
                        'content': [
                            {
                                'type': 'web-page',
                                'url': f'https://hypothes.is/a/{hypothesis_id}'
                            },
                            {
                                'type': 'web-page',
                                'url': (
                                    'https://sciety.org/articles/activity/'
                                    f'{preprint_doi}#hypothesis:{hypothesis_id}'
                                )
                            },
                            {
                                'type': 'web-page',
                                'url': (
                                    'https://sciety.org/evaluations/hypothesis:'
                                    f'{hypothesis_id}/content'
                                )
                            }
                        ]
                    }
                ]
            }
    elif step_number == 0:
        yield {
            'participants': [],
            'outputs': [{
                'type': 'preprint',
                'doi': preprint_doi,
                'url': f'https://doi.org/{preprint_doi}',
                'published': '',
                'versionIdentifier': ''
            }]
        }


def get_docmap_actions_value_from_query_result(
    step_number: int,
    query_result_item: dict
) -> list:
    return list(iter_single_actions_value_from_query_result_for_evaluations(
        step_number,
        query_result_item
    ))


def generate_docmap_steps(number_of_steps: int, query_result_item: dict) -> dict:
    step_number = 0
    steps_dict = {}
    while step_number < number_of_steps:
        LOGGER.debug('step_number: %r', step_number)
        step_dict = {
            'actions': get_docmap_actions_value_from_query_result(
                step_number,
                query_result_item
            ),
            'assertions': get_docmap_assertions_value_from_query_result(
                step_number,
                query_result_item
            ),
            'inputs': get_docmap_inputs_value_from_query_result(
                step_number,
                query_result_item
            ),
            'next-step': (
                '_:b' + str(step_number + 1) if step_number + 1 < number_of_steps else None
            ),
            'previous-step': '_:b' + str(step_number - 1) if step_number > 0 else None
        }

        steps_dict['_:b'+str(step_number)] = step_dict

        step_number += 1
    return remove_key_with_none_value_only(steps_dict)


def get_docmap_item_for_query_result_item(query_result_item: dict) -> dict:
    qc_complete_timestamp_str = query_result_item['qc_complete_timestamp'].isoformat()
    publisher_json = query_result_item['publisher_json']
    number_of_steps = 2  # we need to know which stage we are in
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
            self.docmaps_index_query += '\nWHERE has_evaluations'

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
