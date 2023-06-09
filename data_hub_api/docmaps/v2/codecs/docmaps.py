import logging
import json
from typing import Dict, Iterable, Sequence, Union, cast
import urllib

from data_hub_api.docmaps.v2.codecs.elife_manuscript import (
    get_docmap_elife_manuscript_doi_assertion_item,
    get_docmap_elife_manuscript_output
)
from data_hub_api.docmaps.v2.codecs.evaluation import (
    iter_docmap_actions_for_evaluations,
    iter_docmap_evaluation_input,
)
from data_hub_api.docmaps.v2.codecs.preprint import (
    get_docmap_preprint_assertion_item,
    get_docmap_preprint_input,
    get_docmap_preprint_output
)
from data_hub_api.docmaps.v2.api_input_typing import ApiInput, ApiPreprintInput

from data_hub_api.docmaps.v2.docmap_typing import (
    DocmapAction,
    DocmapAssertion,
    DocmapEvaluationInput,
    DocmapPreprintInput,
    DocmapStep,
    DocmapSteps,
    Docmap
)

from data_hub_api.utils.json import remove_key_with_none_value_only


LOGGER = logging.getLogger(__name__)

DOCMAPS_JSONLD_SCHEMA_URL = 'https://w3id.org/docmaps/context.jsonld'

DOCMAP_ID_PREFIX = (
    'https://data-hub-api.elifesciences.org/enhanced-preprints/docmaps/v2/'
    +
    'by-publisher/elife/get-by-manuscript-id?'
)


def get_docmap_assertions_for_manuscript_published_step(
    preprint: ApiPreprintInput
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_preprint_assertion_item(preprint=preprint),
        'status': 'manuscript-published'
    }]


def get_docmap_actions_for_preprint_manuscript_published_step(
    preprint: ApiPreprintInput
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
    query_result_item: ApiInput,
    preprint: ApiPreprintInput
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_preprint_assertion_item(preprint=preprint),
        'status': 'under-review',
        'happened': (
            query_result_item['under_review_timestamp'].isoformat()
            if query_result_item['under_review_timestamp']
            else ""
        )
    }, {
        'item': get_docmap_elife_manuscript_doi_assertion_item(
            query_result_item=query_result_item,
            preprint=preprint
        ),
        'status': 'draft'
    }]


def get_docmap_actions_for_under_review_and_revised_step(
    query_result_item: ApiInput,
    preprint: ApiPreprintInput
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
    query_result_item: ApiInput,
    preprint: ApiPreprintInput
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
    preprint: ApiPreprintInput
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_preprint_assertion_item(preprint=preprint),
        'status': 'peer-reviewed'
    }]


def get_docmaps_step_for_peer_reviewed_status(
    query_result_item: ApiInput,
    preprint: ApiPreprintInput
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
    query_result_item: ApiInput,
    preprint: ApiPreprintInput,
    previous_preprint: ApiPreprintInput
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
    query_result_item: ApiInput,
    preprint: ApiPreprintInput
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_elife_manuscript_doi_assertion_item(
            query_result_item=query_result_item,
            preprint=preprint
        ),
        'status': 'revised'
    }]


def get_docmap_actions_for_revised_steps(
    query_result_item: ApiInput,
    preprint: ApiPreprintInput
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
    query_result_item: ApiInput,
    preprint: ApiPreprintInput,
    previous_preprint: ApiPreprintInput
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


def iter_docmap_steps_for_query_result_item(query_result_item: ApiInput) -> Iterable[DocmapStep]:
    preprint = query_result_item['preprints'][0]
    # yield get_docmaps_step_for_manuscript_published_status(preprint)
    yield get_docmaps_step_for_under_review_status(query_result_item, preprint)
    # if query_result_item['evaluations']:
    #     yield get_docmaps_step_for_peer_reviewed_status(query_result_item, preprint)
    # if len(query_result_item['preprints']) > 1:
    #     for index, preprint in enumerate(query_result_item['preprints']):
    #         if index > 0:
    #             previous_preprint = query_result_item['preprints'][index-1]
    #             yield get_docmaps_step_for_manuscript_published_status(preprint)
    #             yield get_docmaps_step_for_revised_status(
    #                 query_result_item,
    #                 preprint,
    #                 previous_preprint
    #             )


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


def get_docmap_item_for_query_result_item(query_result_item: ApiInput) -> Docmap:
    qc_complete_timestamp_str = query_result_item['qc_complete_timestamp'].isoformat()
    id_query_param = {'manuscript_id': query_result_item['manuscript_id']}
    publisher_json = query_result_item['publisher_json']
    LOGGER.debug('publisher_json: %r', publisher_json)
    publisher_json_str = json.dumps(publisher_json)
    publisher_data = json.loads(publisher_json_str)
    return {
        '@context': DOCMAPS_JSONLD_SCHEMA_URL,
        'type': 'docmap',
        'id': DOCMAP_ID_PREFIX + urllib.parse.urlencode(id_query_param),
        'created': qc_complete_timestamp_str,
        'updated': qc_complete_timestamp_str,
        'publisher': publisher_data,
        'first-step': '_:b0',
        'steps': generate_docmap_steps(iter_docmap_steps_for_query_result_item(query_result_item))
    }
