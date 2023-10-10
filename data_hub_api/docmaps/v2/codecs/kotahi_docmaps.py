import logging
import ast
from typing import Iterable
import urllib
from data_hub_api.docmaps.v2.codecs.docmaps_steps import (
    generate_docmap_steps,
    get_docmaps_step_for_manuscript_published_status,
    get_docmaps_step_for_peer_reviewed_status,
    get_docmaps_step_for_revised_status,
    get_docmaps_step_for_under_review_status,
    get_kotahi_docmaps_step_for_under_review_status,
    get_docmaps_step_for_vor_published_status
)

from data_hub_api.docmaps.v2.api_input_typing import ApiInput

from data_hub_api.docmaps.v2.docmap_typing import (
    DocmapStep,
    Docmap
)

LOGGER = logging.getLogger(__name__)

DOCMAPS_JSONLD_SCHEMA_URL = 'https://w3id.org/docmaps/context.jsonld'

DOCMAP_ID_PREFIX = (
    'https://data-hub-api.elifesciences.org/kotahi/docmaps/v1/'
    +
    'by-publisher/elife/get-by-manuscript-id?'
)


def is_manuscript_vor(long_manuscript_identifier: str) -> bool:
    return ('-VOR-' in long_manuscript_identifier)


def iter_docmap_steps_for_query_result_item(query_result_item: ApiInput) -> Iterable[DocmapStep]:
    manuscript_versions = query_result_item['manuscript_versions']
    for index, manuscript_version in enumerate(manuscript_versions):
        if not is_manuscript_vor(manuscript_version['long_manuscript_identifier']):
            yield get_kotahi_docmaps_step_for_under_review_status(query_result_item, manuscript_version)
            if manuscript_version['evaluations']:
                if manuscript_version['position_in_overall_stage'] == 1:
                    yield get_docmaps_step_for_peer_reviewed_status(
                        query_result_item,
                        manuscript_version
                    )
                else:
                    yield get_docmaps_step_for_revised_status(query_result_item, manuscript_version)
        else:
            previous_manuscript_version = query_result_item['manuscript_versions'][index - 1]
            assert manuscript_version['position_in_overall_stage'] > 1
            yield get_docmaps_step_for_vor_published_status(
                query_result_item,
                manuscript_version,
                previous_manuscript_version
            )


def get_kotahi_docmap_item_for_query_result_item(query_result_item: ApiInput) -> Docmap:
    manuscript_first_version = query_result_item['manuscript_versions'][0]
    qc_complete_timestamp_str = manuscript_first_version['qc_complete_timestamp'].isoformat()
    id_query_param = {'manuscript_id': query_result_item['manuscript_id']}
    publisher_json = ast.literal_eval(query_result_item['publisher_json'])
    LOGGER.debug('publisher_json: %r', publisher_json)
    return {
        '@context': DOCMAPS_JSONLD_SCHEMA_URL,
        'type': 'docmap',
        'id': DOCMAP_ID_PREFIX + urllib.parse.urlencode(id_query_param),
        'created': qc_complete_timestamp_str,
        'updated': qc_complete_timestamp_str,
        'publisher': publisher_json,
        'first-step': '_:b0',
        'steps': generate_docmap_steps(iter_docmap_steps_for_query_result_item(query_result_item))
    }
