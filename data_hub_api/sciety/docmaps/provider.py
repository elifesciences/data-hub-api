from pathlib import Path
from typing import Iterable


from data_hub_api.utils.bigquery import (
    iter_dict_from_bq_query
)
from data_hub_api.sciety.docmaps.sql import get_sql_path


DOCMAPS_JSONLD_SCHEMA_URL = 'https://w3id.org/docmaps/context.jsonld'


def get_docmaps_item_for_query_result_item(query_result_item: dict) -> dict:
    return {
        '@context': DOCMAPS_JSONLD_SCHEMA_URL,
        'type': 'docmap',
        'first-step': '_:b0',
        'steps': {
            '_:b0': {
                'assertions': [],
                'inputs': [{
                    'doi': query_result_item['preprint_doi'],
                    'url': query_result_item['preprint_url'],
                }],
                'actions': []
            }
        }

    }


class ScietyDocmapsProvider:
    def __init__(
        self,
        gcp_project_name: str = 'elife-data-pipeline'
    ) -> None:
        self.gcp_project_name = gcp_project_name
        self.docmaps_index_query = (
          Path(get_sql_path('docmaps_index.sql')).read_text(encoding='utf-8')
        )

    def iter_docmaps(self) -> Iterable[dict]:
        bq_result_iterable = iter_dict_from_bq_query(
            self.gcp_project_name,
            self.docmaps_index_query
        )
        for bq_result in bq_result_iterable:
            yield get_docmaps_item_for_query_result_item(bq_result)

    def get_docmaps_index(self) -> dict:
        article_docmaps_list = list(self.iter_docmaps())
        return {'articles': article_docmaps_list}
