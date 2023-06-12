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
    get_docmap_preprint_input
)
from data_hub_api.docmaps.v2.api_input_typing import ApiInput, ApiManuscriptDetailInput

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


def get_docmap_assertions_for_under_review_step(
    query_result_item: ApiInput,
    manuscript_detail: ApiManuscriptDetailInput
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_preprint_assertion_item(manuscript_detail=manuscript_detail),
        'status': 'under-review',
        'happened': (
            manuscript_detail['under_review_timestamp'].isoformat()
            if manuscript_detail['under_review_timestamp']
            else ""
        )
    }, {
        'item': get_docmap_elife_manuscript_doi_assertion_item(
            query_result_item=query_result_item,
            manuscript_detail=manuscript_detail
        ),
        'status': 'draft'
    }]


def get_docmap_actions_for_under_review_step(
    query_result_item: ApiInput,
    manuscript_detail: ApiManuscriptDetailInput
) -> Sequence[DocmapAction]:
    return [{
        'participants': [],
        'outputs': [
            get_docmap_elife_manuscript_output(
                query_result_item=query_result_item,
                manuscript_detail=manuscript_detail
            )
        ]
    }]


def get_docmaps_step_for_under_review_status(
    query_result_item: ApiInput,
    manuscript_detail: ApiManuscriptDetailInput
):
    return {
        'actions': get_docmap_actions_for_under_review_step(
            query_result_item=query_result_item,
            manuscript_detail=manuscript_detail
        ),
        'assertions': get_docmap_assertions_for_under_review_step(
            query_result_item=query_result_item,
            manuscript_detail=manuscript_detail
        ),
        'inputs': [get_docmap_preprint_input(manuscript_detail=manuscript_detail, detailed=True)]
    }


def get_docmap_assertions_for_peer_reviewed_step(
    manuscript_detail: ApiManuscriptDetailInput
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_preprint_assertion_item(manuscript_detail=manuscript_detail),
        'status': 'peer-reviewed'
    }]


def get_docmaps_step_for_peer_reviewed_status(
    query_result_item: ApiInput,
    manuscript_detail: ApiManuscriptDetailInput
):
    return {
        'actions': list(iter_docmap_actions_for_evaluations(
            query_result_item=query_result_item,
            manuscript_detail=manuscript_detail
            )
        ),
        'assertions': get_docmap_assertions_for_peer_reviewed_step(
            manuscript_detail=manuscript_detail
        ),
        'inputs': [get_docmap_preprint_input(manuscript_detail=manuscript_detail, detailed=False)]
    }


def get_docmap_assertions_for_manuscript_published_step(
    query_result_item: ApiInput,
    manuscript_detail: ApiManuscriptDetailInput
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_elife_manuscript_doi_assertion_item(
            query_result_item=query_result_item,
            manuscript_detail=manuscript_detail
        ),
        'status': 'manuscript-published'
    }]


def get_docmap_actions_for_manuscript_published_step(
    query_result_item: ApiInput,
    manuscript_detail: ApiManuscriptDetailInput
) -> Sequence[DocmapAction]:
    return [{
        'participants': [],
        'outputs': [get_docmap_elife_manuscript_output(
            query_result_item=query_result_item,
            manuscript_detail=manuscript_detail
        )]
    }]


def get_docmap_inputs_for_manuscript_published_step(
    query_result_item: ApiInput,
    manuscript_detail: ApiManuscriptDetailInput,
) -> Sequence[Union[DocmapPreprintInput, DocmapEvaluationInput]]:
    return (
        list([get_docmap_preprint_input(
            manuscript_detail=manuscript_detail,
            detailed=False
        )])
        +
        list(iter_docmap_evaluation_input(
            query_result_item=query_result_item,
            manuscript_detail=manuscript_detail
        ))
    )


def get_docmaps_step_for_manuscript_published_status(
    query_result_item: ApiInput,
    manuscript_detail: ApiManuscriptDetailInput
) -> DocmapStep:
    return {
        'actions': get_docmap_actions_for_manuscript_published_step(
            query_result_item=query_result_item,
            manuscript_detail=manuscript_detail
        ),
        'assertions': get_docmap_assertions_for_manuscript_published_step(
            query_result_item=query_result_item,
            manuscript_detail=manuscript_detail
        ),
        'inputs': get_docmap_inputs_for_manuscript_published_step(
            query_result_item=query_result_item,
            manuscript_detail=manuscript_detail
        )
    }


def iter_docmap_steps_for_query_result_item(query_result_item: ApiInput) -> Iterable[DocmapStep]:
    manuscript_details = query_result_item['manuscript_detail']
    for manuscript_detail in manuscript_details:
        yield get_docmaps_step_for_under_review_status(query_result_item, manuscript_detail)
        if manuscript_detail['evaluations']:
            yield get_docmaps_step_for_peer_reviewed_status(query_result_item, manuscript_detail)
            yield get_docmaps_step_for_manuscript_published_status(
                query_result_item,
                manuscript_detail
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


def get_docmap_item_for_query_result_item(query_result_item: ApiInput) -> Docmap:
    manuscript_first_version = query_result_item['manuscript_detail'][0]
    qc_complete_timestamp_str = manuscript_first_version['qc_complete_timestamp'].isoformat()
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
