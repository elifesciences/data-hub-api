import logging
from pathlib import Path
from time import monotonic
from typing import Iterable, Optional, Sequence, cast
import objsize

from data_hub_api.docmaps.v2.codecs.docmaps import get_docmap_item_for_query_result_item
from data_hub_api.docmaps.v2.api_input_typing import ApiInput
from data_hub_api.docmaps.v2.docmap_typing import Docmap

from data_hub_api.utils.bigquery import iter_dict_from_bq_query
from data_hub_api.utils.cache import SingleObjectCache, DummySingleObjectCache
from data_hub_api.docmaps.v2.sql import get_sql_path

LOGGER = logging.getLogger(__name__)


class DocmapsProvider:
    def __init__(
        self,
        sql_query_name: str,
        gcp_project_name: str = 'elife-data-pipeline',
        query_results_cache: Optional[SingleObjectCache[Sequence[dict]]] = None,
    ) -> None:
        self.gcp_project_name = gcp_project_name
        self.docmaps_index_query = (
            Path(get_sql_path(sql_query_name)).read_text(encoding='utf-8')
        )
        if query_results_cache is None:
            query_results_cache = DummySingleObjectCache[Sequence[dict]]()
        self._query_results_cache = query_results_cache

    def _load_query_results_from_bq(self) -> Sequence[dict]:
        LOGGER.info('Loading query results from BigQuery...')
        start_time = monotonic()
        result = list(iter_dict_from_bq_query(
            self.gcp_project_name,
            self.docmaps_index_query
        ))
        end_time = monotonic()
        LOGGER.info(
            'Loaded query results from BigQuery, rows=%d, approx_size=%.3fMB, time=%.3f seconds',
            len(result),
            objsize.get_deep_size(result) / 1024 / 1024,
            (end_time - start_time)
        )
        return result

    def iter_docmaps_by_manuscript_id(
        self,
        manuscript_id: Optional[str] = None
    ) -> Iterable[Docmap]:
        bq_result_list = self._query_results_cache.get_or_load(
            load_fn=self._load_query_results_from_bq
        )
        if manuscript_id:
            bq_result_list = [
                bq_result
                for bq_result in bq_result_list
                if bq_result['manuscript_id'] == manuscript_id
            ]
        for bq_result in bq_result_list:
            yield get_docmap_item_for_query_result_item(cast(ApiInput, bq_result))

    def get_docmaps_by_manuscript_id(self, manuscript_id: str) -> Sequence[Docmap]:
        return list(self.iter_docmaps_by_manuscript_id(manuscript_id))

    def get_docmaps_index(self) -> dict:
        article_docmaps_list = list(self.iter_docmaps_by_manuscript_id())
        return {'docmaps': article_docmaps_list}
