from dataclasses import dataclass
import logging
from pathlib import Path
from time import monotonic
from typing import Iterable, Mapping, Optional, Sequence, cast

from data_hub_api.utils.html import convert_plain_text_to_html
import objsize
from data_hub_api.kotahi_docmaps.v1.codecs.docmaps import get_docmap_item_for_query_result_item
from data_hub_api.kotahi_docmaps.v1.api_input_typing import ApiInput
from data_hub_api.kotahi_docmaps.v1.codecs.evaluation import iter_evaluation_id_and_text
from data_hub_api.kotahi_docmaps.v1.docmap_typing import (
    Docmap
)

from data_hub_api.utils.bigquery import (
    iter_dict_from_bq_query
)
from data_hub_api.utils.cache import SingleObjectCache, DummySingleObjectCache
from data_hub_api.kotahi_docmaps.v1.sql import get_sql_path


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DocmapsProviderData:
    docmap_by_manuscript_id_map: Mapping[str, Docmap]
    evaluation_text_by_evaluation_id_map: Mapping[str, str]


class DocmapsProvider:
    def __init__(
        self,
        gcp_project_name: str = 'elife-data-pipeline',
        data_cache: Optional[SingleObjectCache[DocmapsProviderData]] = None,
    ) -> None:
        self.gcp_project_name = gcp_project_name
        self.docmaps_index_query = (
            Path(get_sql_path('docmaps_index.sql')).read_text(encoding='utf-8')
        )
        if data_cache is None:
            data_cache = DummySingleObjectCache[DocmapsProviderData]()
        self._data_cache = data_cache

    def _load_query_results_from_bq(self) -> Sequence[ApiInput]:
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
        return cast(Sequence[ApiInput], result)

    def _load_data(self) -> DocmapsProviderData:
        bq_result_list = self._load_query_results_from_bq()
        LOGGER.info('Preparing data from query results...')
        start_time = monotonic()
        data = DocmapsProviderData(
            docmap_by_manuscript_id_map=self.create_docmap_by_manuscript_id_map(
                bq_result_list
            ),
            evaluation_text_by_evaluation_id_map=self.create_evaluation_text_by_evaluation_id_map(
                bq_result_list
            )
        )
        end_time = monotonic()
        LOGGER.info(
            'Prepared data from query results, approx_size=%.3fMB, time=%.3f seconds',
            objsize.get_deep_size(data) / 1024 / 1024,
            (end_time - start_time)
        )
        return data

    def _get_data(self) -> DocmapsProviderData:
        return self._data_cache.get_or_load(load_fn=self._load_data)

    def create_docmap_by_manuscript_id_map(
        self,
        bq_results: Iterable[ApiInput]
    ) -> Mapping[str, Docmap]:
        return {
            bq_result['manuscript_id']: get_docmap_item_for_query_result_item(
                cast(ApiInput, bq_result)
            )
            for bq_result in bq_results
        }

    def create_evaluation_text_by_evaluation_id_map(
        self,
        bq_results: Iterable[ApiInput]
    ) -> Mapping[str, str]:
        evaluation_map = {}
        for bq_result in bq_results:
            manuscript_versions = bq_result['manuscript_versions']
            for manuscript_version in manuscript_versions:
                for evaluation_id, evaluation_text in iter_evaluation_id_and_text(
                    manuscript_version
                ):
                    evaluation_map[evaluation_id] = evaluation_text
        return evaluation_map

    def iter_docmaps_by_manuscript_id(
        self,
        manuscript_id: Optional[str] = None
    ) -> Iterable[Docmap]:
        docmap_by_manuscript_id_map = self._get_data().docmap_by_manuscript_id_map
        if manuscript_id:
            docmap = docmap_by_manuscript_id_map.get(manuscript_id)
            if not docmap:
                return []
            return [docmap]
        return docmap_by_manuscript_id_map.values()

    def get_docmaps_by_manuscript_id(self, manuscript_id: str) -> Sequence[Docmap]:
        return list(self.iter_docmaps_by_manuscript_id(manuscript_id))

    def get_docmaps_index(self) -> dict:
        article_docmaps_list = list(self.iter_docmaps_by_manuscript_id())
        return {'docmaps': article_docmaps_list}

    def get_evaluation_text_by_evaluation_id(self, evaluation_id: str) -> Optional[str]:
        assert evaluation_id
        return self._get_data().evaluation_text_by_evaluation_id_map.get(evaluation_id)

    def get_evaluation_html_by_evaluation_id(self, evaluation_id: str) -> Optional[str]:
        evaluation_text = self.get_evaluation_text_by_evaluation_id(evaluation_id)
        if evaluation_text is not None:
            return convert_plain_text_to_html(evaluation_text)
        return None
