import logging
import json
from pathlib import Path
from time import monotonic
from typing import Dict, Iterable, Optional, Sequence, Tuple, Union, cast
import urllib

import objsize

from data_hub_api.docmaps.codecs.elife_manuscript import (
    get_docmap_elife_manuscript_doi_assertion_item,
    get_docmap_elife_manuscript_output
)
from data_hub_api.docmaps.codecs.evaluation import (
    iter_docmap_actions_for_evaluations,
    iter_docmap_evaluation_input,
)
from data_hub_api.docmaps.codecs.preprint import (
    get_docmap_preprint_assertion_item,
    get_docmap_preprint_input,
    get_docmap_preprint_output
)

from data_hub_api.docmaps.docmap_typing import (
    DocmapAction,
    DocmapAssertion,
    DocmapEvaluationInput,
    DocmapPreprintInput,
    DocmapStep,
    DocmapSteps,
    Docmap
)

from data_hub_api.utils.bigquery import (
    iter_dict_from_bq_query
)
from data_hub_api.utils.cache import SingleObjectCache, DummySingleObjectCache
from data_hub_api.docmaps.sql import get_sql_path
from data_hub_api.utils.json import remove_key_with_none_value_only


LOGGER = logging.getLogger(__name__)

DOCMAPS_JSONLD_SCHEMA_URL = 'https://w3id.org/docmaps/context.jsonld'

DOCMAP_ID_PREFIX = (
    'https://data-hub-api.elifesciences.org/enhanced-preprints/docmaps/v1/'
    +
    'by-publisher/elife/get-by-manuscript-id?'
)

ADDITIONAL_MANUSCRIPT_IDS = (
    '80494',
    '80984',
    '81727',
    '81926',
    '81535',
    '80729'
)


def get_docmap_assertions_for_manuscript_published_step(
    preprint: dict
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_preprint_assertion_item(preprint=preprint),
        'status': 'manuscript-published'
    }]


def get_docmap_actions_for_preprint_manuscript_published_step(
    preprint: dict
) -> Sequence[DocmapAction]:
    return [{
        'participants': [],
        'outputs': [get_docmap_preprint_output(preprint=preprint)]
    }]


def get_docmaps_step_for_manuscript_published_status(
    preprint
) -> DocmapStep:
    return {
        'actions': get_docmap_actions_for_preprint_manuscript_published_step(
            preprint=preprint
        ),
        'assertions': get_docmap_assertions_for_manuscript_published_step(
            preprint=preprint
        ),
        'inputs': []
    }


def get_docmap_assertions_for_under_review_step(
    query_result_item: dict,
    preprint: dict
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_preprint_assertion_item(preprint=preprint),
        'status': 'under-review',
        'happened': query_result_item['under_review_timestamp']
    }, {
        'item': get_docmap_elife_manuscript_doi_assertion_item(
            query_result_item=query_result_item,
            preprint=preprint
        ),
        'status': 'draft'
    }]


def get_docmap_actions_for_under_review_and_revised_step(
    query_result_item: dict,
    preprint: dict
) -> Sequence[DocmapAction]:
    return [{
        'participants': [],
        'outputs': [
            get_docmap_elife_manuscript_output(
                query_result_item=query_result_item,
                preprint=preprint
            )
        ]
    }]


def get_docmaps_step_for_under_review_status(
    query_result_item: dict,
    preprint: dict
):
    return {
        'actions': get_docmap_actions_for_under_review_and_revised_step(
            query_result_item=query_result_item,
            preprint=preprint
        ),
        'assertions': get_docmap_assertions_for_under_review_step(
            query_result_item=query_result_item,
            preprint=preprint
        ),
        'inputs': [get_docmap_preprint_input(preprint=preprint)]
    }


def get_docmap_assertions_for_peer_reviewed_step(
    preprint: dict
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_preprint_assertion_item(preprint=preprint),
        'status': 'peer-reviewed'
    }]


def get_docmaps_step_for_peer_reviewed_status(
    query_result_item: dict,
    preprint: dict
):
    return {
        'actions': list(iter_docmap_actions_for_evaluations(
            query_result_item=query_result_item,
            preprint=preprint
            )
        ),
        'assertions': get_docmap_assertions_for_peer_reviewed_step(
            preprint=preprint
        ),
        'inputs': [get_docmap_preprint_input(preprint=preprint)]
    }


def get_docmap_inputs_for_revised_steps(
    query_result_item: dict,
    preprint: dict,
    previous_preprint: dict
) -> Sequence[Union[DocmapPreprintInput, DocmapEvaluationInput]]:
    return (
        list([get_docmap_preprint_input(preprint=preprint)])
        +
        list(iter_docmap_evaluation_input(
            query_result_item=query_result_item,
            preprint=previous_preprint
        ))
    )


def get_docmap_assertions_for_revised_steps(
    query_result_item: dict,
    preprint: dict
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_elife_manuscript_doi_assertion_item(
            query_result_item=query_result_item,
            preprint=preprint
        ),
        'status': 'revised'
    }]


def get_docmap_actions_for_revised_steps(
    query_result_item: dict,
    preprint: dict
) -> Sequence[DocmapAction]:
    return (
        list(get_docmap_actions_for_under_review_and_revised_step(
            query_result_item=query_result_item,
            preprint=preprint
        ))
        +
        list(iter_docmap_actions_for_evaluations(
            query_result_item=query_result_item,
            preprint=preprint
        ))
    )


def get_docmaps_step_for_revised_status(
    query_result_item: dict,
    preprint: dict,
    previous_preprint: dict
):
    return {
        'actions': get_docmap_actions_for_revised_steps(
            query_result_item=query_result_item,
            preprint=preprint
        ),
        'assertions': get_docmap_assertions_for_revised_steps(
            query_result_item=query_result_item,
            preprint=preprint
        ),
        'inputs': get_docmap_inputs_for_revised_steps(
            query_result_item=query_result_item,
            preprint=preprint,
            previous_preprint=previous_preprint
        )
    }


def iter_docmap_steps_for_query_result_item(query_result_item: dict) -> Iterable[DocmapStep]:
    preprint = query_result_item['preprints'][0]
    yield get_docmaps_step_for_manuscript_published_status(preprint)
    yield get_docmaps_step_for_under_review_status(query_result_item, preprint)
    if query_result_item['evaluations']:
        yield get_docmaps_step_for_peer_reviewed_status(query_result_item, preprint)
    if len(query_result_item['preprints']) > 1:
        for index, preprint in enumerate(query_result_item['preprints']):
            if index > 0:
                previous_preprint = query_result_item['preprints'][index-1]
                yield get_docmaps_step_for_manuscript_published_status(preprint)
                yield get_docmaps_step_for_revised_status(
                    query_result_item,
                    preprint,
                    previous_preprint
                )


def generate_docmap_steps(step_iterable: Iterable[DocmapStep]) -> DocmapSteps:
    steps_dict: Dict[str, DocmapStep] = {}
    step_list = list(step_iterable)
    for step_index, step in enumerate(step_list):
        LOGGER.debug('step_index: %r', step_index)
        step_ranking_dict = {
            'next-step': ('_:b' + str(step_index + 1) if step_index + 1 < len(step_list) else None),
            'previous-step': '_:b' + str(step_index - 1) if step_index > 0 else None
        }
        steps_dict['_:b'+str(step_index)] = cast(DocmapStep, dict(step, **step_ranking_dict))
    return remove_key_with_none_value_only(steps_dict)


def get_docmap_item_for_query_result_item(query_result_item: dict) -> Docmap:
    qc_complete_timestamp_str = query_result_item['qc_complete_timestamp'].isoformat()
    publisher_json = query_result_item['publisher_json']
    LOGGER.debug('publisher_json: %r', publisher_json)
    id_query_param = {'manuscript_id': query_result_item['manuscript_id']}
    return {
        '@context': DOCMAPS_JSONLD_SCHEMA_URL,
        'type': 'docmap',
        'id': DOCMAP_ID_PREFIX + urllib.parse.urlencode(id_query_param),
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
        query_results_cache: Optional[SingleObjectCache[Sequence[dict]]] = None,
        only_include_reviewed_preprint_type: bool = True,
        only_include_evaluated_preprints: bool = False,
        additionally_include_manuscript_ids: Optional[Tuple[str]] = None
    ) -> None:
        self.gcp_project_name = gcp_project_name
        self.docmaps_index_query = (
            Path(get_sql_path('docmaps_index.sql')).read_text(encoding='utf-8')
        )
        assert not (only_include_reviewed_preprint_type and only_include_evaluated_preprints)
        assert not (additionally_include_manuscript_ids and not only_include_reviewed_preprint_type)
        if only_include_reviewed_preprint_type:
            self.docmaps_index_query += (
                '\nWHERE is_reviewed_preprint_type AND is_or_was_under_review'
            )
        if only_include_reviewed_preprint_type and additionally_include_manuscript_ids:
            self.docmaps_index_query += (
                f'\nOR result.manuscript_id IN {additionally_include_manuscript_ids}'
            )
        if only_include_evaluated_preprints:
            self.docmaps_index_query += '\nWHERE has_evaluations'
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
            yield get_docmap_item_for_query_result_item(bq_result)

    def get_docmaps_by_manuscript_id(self, manuscript_id: str) -> Sequence[Docmap]:
        return list(self.iter_docmaps_by_manuscript_id(manuscript_id))

    def get_docmaps_index(self) -> dict:
        article_docmaps_list = list(self.iter_docmaps_by_manuscript_id())
        return {'docmaps': article_docmaps_list}
