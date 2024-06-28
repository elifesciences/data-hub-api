from datetime import datetime
import logging
from typing import Dict, Iterable, Optional, Sequence, Union, cast
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

from data_hub_api.utils.json import (
    parse_json_if_string_or_return_value,
    remove_key_with_none_value_only
)


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


def get_docmap_assertions_for_vor_steps(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput,
    vor_version_number: int,
    vor_updated_date: Optional[datetime] = None
) -> Sequence[DocmapAssertion]:
    assertion = {
        'item': get_docmap_elife_manuscript_doi_assertion_item_for_vor(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
        ),
        'status': 'vor-published'
    }
    if vor_version_number > 1:
        return [{
            **assertion,
            'status': 'corrected',
            'happened': vor_updated_date.isoformat()
        }]
    return [assertion]


def get_docmap_actions_for_vor_published_step(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput
) -> Sequence[DocmapAction]:
    return [{
        'participants': [],
        'outputs': [get_docmap_elife_manuscript_output_for_vor(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version,
            vor_version_number=1
        )]
    }]


def get_docmaps_step_for_vor_published_status(
    query_result_item: ApiInput,
    manuscript_version: ApiManuscriptVersionInput,
) -> DocmapStep:
    return {
        'actions': get_docmap_actions_for_vor_published_step(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
        ),
        'assertions': get_docmap_assertions_for_vor_steps(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version,
            vor_version_number=1
        ),
        'inputs': [get_docmap_elife_manuscript_input(
            query_result_item=query_result_item,
            manuscript_version=manuscript_version
        )]
    }


def iter_docmap_steps_for_query_result_item(query_result_item: ApiInput) -> Iterable[DocmapStep]:
    manuscript_versions = [
        manuscript_version
        for manuscript_version in query_result_item['manuscript_versions']
        if '-VOR-' not in manuscript_version['long_manuscript_identifier']
    ]
    vor_versions = query_result_item['vor_versions']
    for index, manuscript_version in enumerate(manuscript_versions):
        yield get_docmaps_step_for_under_review_status(query_result_item, manuscript_version)
        if manuscript_version['evaluations']:
            if manuscript_version['position_in_overall_stage'] == 1:
                yield get_docmaps_step_for_peer_reviewed_status(
                    query_result_item=query_result_item,
                    manuscript_version=manuscript_version
                )
            else:
                yield get_docmaps_step_for_revised_status(query_result_item, manuscript_version)
            if manuscript_version['rp_publication_timestamp']:
                yield get_docmaps_step_for_manuscript_published_status(
                    query_result_item=query_result_item,
                    manuscript_version=manuscript_version
                )
        if vor_versions and index == len(manuscript_versions) - 1:
            yield get_docmaps_step_for_vor_published_status(
                query_result_item=query_result_item,
                manuscript_version=manuscript_version
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
    try:
        manuscript_first_version = query_result_item['manuscript_versions'][0]
        qc_complete_timestamp_str = manuscript_first_version['qc_complete_timestamp'].isoformat()
        id_query_param = {'manuscript_id': query_result_item['manuscript_id']}
        publisher_json: dict = parse_json_if_string_or_return_value(
            query_result_item['publisher_json']
        )
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
    except Exception as exc:
        LOGGER.warning(
            'Failed to generate DocMaps for query_result_item: %r due to %r',
            query_result_item,
            exc
        )
        raise
