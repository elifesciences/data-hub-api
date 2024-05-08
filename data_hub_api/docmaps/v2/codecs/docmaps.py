import logging
import ast
from typing import Dict, Iterable, Sequence, Union, cast
import urllib

from data_hub_api.docmaps.v2.codecs.elife_manuscript import (
    get_docmap_elife_manuscript_doi_assertion_item,
    get_docmap_elife_manuscript_doi_assertion_item_for_vor,
    get_docmap_elife_manuscript_input,
    get_docmap_elife_manuscript_output,
    get_docmap_elife_manuscript_output_for_published_step,
    get_docmap_elife_manuscript_output_for_vor
)
from data_hub_api.docmaps.v2.codecs.evaluation import (
    iter_docmap_actions_for_evaluations,
    iter_docmap_evaluation_input,
)
from data_hub_api.docmaps.v2.codecs.preprint import (
    get_docmap_preprint_assertion_item,
    get_docmap_preprint_input,
    get_docmap_preprint_input_with_published_and_meca_path
)
from data_hub_api.docmaps.v2.api_input_typing import ApiInput, ApiManuscriptVersionInput

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
    manuscript_version: ApiManuscriptVersionInput
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_preprint_assertion_item(manuscript_version=manuscript_version),
        'status': 'under-review',
        'happened': (
            manuscript_version['under_review_timestamp'].isoformat()
            if manuscript_version['under_review_timestamp']
            else ""
        )
    }, {
        'item': get_docmap_elife_manuscript_doi_assertion_item(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
        ),
        'status': 'draft'
    }]


def get_docmap_actions_for_under_review_step(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
) -> Sequence[DocmapAction]:
    return [{
        'participants': [],
        'outputs': [
            get_docmap_elife_manuscript_output(
                query_result_item=query_result_item,
                manuscript_version=manuscript_version
            )
        ]
    }]


def get_docmaps_step_for_under_review_status(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
):
    return {
        'actions': get_docmap_actions_for_under_review_step(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
        ),
        'assertions': get_docmap_assertions_for_under_review_step(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
        ),
        'inputs': [get_docmap_preprint_input_with_published_and_meca_path(
            manuscript_version=manuscript_version
        )]
    }


def get_docmap_assertions_for_peer_reviewed_step(
    manuscript_version: ApiManuscriptVersionInput
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_preprint_assertion_item(manuscript_version=manuscript_version),
        'status': 'peer-reviewed'
    }]


def get_docmaps_step_for_peer_reviewed_status(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
):
    return {
        'actions': list(iter_docmap_actions_for_evaluations(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
            )
        ),
        'assertions': get_docmap_assertions_for_peer_reviewed_step(
            manuscript_version=manuscript_version
        ),
        'inputs': [get_docmap_preprint_input(manuscript_version=manuscript_version)]
    }


def get_docmap_assertions_for_revised_step(
    manuscript_version: ApiManuscriptVersionInput
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_preprint_assertion_item(manuscript_version=manuscript_version),
        'status': 'revised'
    }]


def get_docmaps_step_for_revised_status(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
):
    return {
        'actions': list(iter_docmap_actions_for_evaluations(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
            )
        ),
        'assertions': get_docmap_assertions_for_revised_step(
            manuscript_version=manuscript_version
        ),
        'inputs': [get_docmap_preprint_input(manuscript_version=manuscript_version)]
    }


def get_docmap_assertions_for_manuscript_published_step(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_elife_manuscript_doi_assertion_item(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
        ),
        'status': 'manuscript-published'
    }]


def get_docmap_actions_for_manuscript_published_step(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
) -> Sequence[DocmapAction]:
    return [{
        'participants': [],
        'outputs': [get_docmap_elife_manuscript_output_for_published_step(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
        )]
    }]


def get_docmap_inputs_for_manuscript_published_step(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput,
) -> Sequence[Union[DocmapPreprintInput, DocmapEvaluationInput]]:
    return (
        list([get_docmap_preprint_input(
            manuscript_version=manuscript_version
        )])
        +
        list(iter_docmap_evaluation_input(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
        ))
    )


def get_docmaps_step_for_manuscript_published_status(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
) -> DocmapStep:
    return {
        'actions': get_docmap_actions_for_manuscript_published_step(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
        ),
        'assertions': get_docmap_assertions_for_manuscript_published_step(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
        ),
        'inputs': get_docmap_inputs_for_manuscript_published_step(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
        )
    }


def get_docmap_assertions_for_vor_published_step(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput,
    is_vor_for_opt_ins: bool = False
) -> Sequence[DocmapAssertion]:
    return [{
        'item': get_docmap_elife_manuscript_doi_assertion_item_for_vor(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version,
            is_vor_for_opt_ins=is_vor_for_opt_ins
        ),
        'status': 'vor-published'
    }]


def get_docmap_actions_for_vor_published_step(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput,
    is_vor_for_opt_ins: bool = False
) -> Sequence[DocmapAction]:
    return [{
        'participants': [],
        'outputs': [get_docmap_elife_manuscript_output_for_vor(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version,
            is_vor_for_opt_ins=is_vor_for_opt_ins
        )]
    }]


def get_docmaps_step_for_vor_published_status(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput,
    previous_manuscript_version: ApiManuscriptVersionInput,
    is_vor_for_opt_ins: bool = False
) -> DocmapStep:
    return {
        'actions': get_docmap_actions_for_vor_published_step(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version,
            is_vor_for_opt_ins=is_vor_for_opt_ins
        ),
        'assertions': get_docmap_assertions_for_vor_published_step(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version,
            is_vor_for_opt_ins=is_vor_for_opt_ins
        ),
        'inputs': [get_docmap_elife_manuscript_input(
            query_result_item=query_result_item,
            manuscript_version=previous_manuscript_version
        )]
    }


def is_manuscript_vor_from_new_site(long_manuscript_identifier: str) -> bool:
    return ('-VOR-' in long_manuscript_identifier)


def iter_docmap_steps_for_query_result_item(query_result_item: ApiInput) -> Iterable[DocmapStep]:
    manuscript_versions = query_result_item['manuscript_versions']
    for index, manuscript_version in enumerate(manuscript_versions):
        if not is_manuscript_vor_from_new_site(manuscript_version['long_manuscript_identifier']):
            yield get_docmaps_step_for_under_review_status(query_result_item, manuscript_version)
            if manuscript_version['evaluations']:
                if manuscript_version['position_in_overall_stage'] == 1:
                    yield get_docmaps_step_for_peer_reviewed_status(
                        query_result_item,
                        manuscript_version
                    )
                else:
                    yield get_docmaps_step_for_revised_status(query_result_item, manuscript_version)
                if manuscript_version['rp_publication_timestamp']:
                    yield get_docmaps_step_for_manuscript_published_status(
                        query_result_item,
                        manuscript_version
                    )
        if manuscript_version['vor_publication_date'] and index == len(manuscript_versions) - 1:
            is_vor_for_opt_ins = False
            previous_manuscript_version = manuscript_versions[index - 1]
            if not is_manuscript_vor_from_new_site(
                manuscript_version['long_manuscript_identifier']
            ):
                is_vor_for_opt_ins = True
                previous_manuscript_version = manuscript_version
            yield get_docmaps_step_for_vor_published_status(
                query_result_item,
                manuscript_version,
                previous_manuscript_version,
                is_vor_for_opt_ins
            )


def generate_docmap_steps_and_remove_none_value_keys(
    step_iterable: Iterable[DocmapStep]
) -> DocmapSteps:
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
        'steps': generate_docmap_steps_and_remove_none_value_keys(
            iter_docmap_steps_for_query_result_item(query_result_item)
        )
    }
