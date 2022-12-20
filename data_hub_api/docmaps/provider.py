import logging
import json
from pathlib import Path
from typing import Iterable


from data_hub_api.utils.bigquery import (
    iter_dict_from_bq_query
)
from data_hub_api.docmaps.sql import get_sql_path


LOGGER = logging.getLogger(__name__)

DOCMAPS_JSONLD_SCHEMA_URL = 'https://w3id.org/docmaps/context.jsonld'

DOCMAP_ID_PREFIX = 'https://data-hub-api.elifesciences.org/enhanced-preprints/docmaps/v1/articles/'
DOCMAP_ID_SUFFIX = '/docmap.json'


def get_docmap_inputs_value_from_query_result(query_result_item: dict) -> list:
    return [{
        'doi': query_result_item['preprint_doi'],
        'url': query_result_item['preprint_url'],
    }]


def get_docmap_actions_value_from_query_result(query_result_item: dict) -> list:
    return [{
        'outputs': [
            {
                'type': '',
                'doi': query_result_item['elife_doi'],
                'published': '',
                'url': '',
                'content': []
            }
        ]
    }]


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
        'steps': {
            '_:b0': {
                'assertions': [],
                'inputs': get_docmap_inputs_value_from_query_result(query_result_item),
                'actions': get_docmap_actions_value_from_query_result(query_result_item)
            }
        }
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
