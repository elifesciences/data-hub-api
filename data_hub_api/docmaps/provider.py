import logging
import json
from pathlib import Path
from time import monotonic
from typing import Iterable, Optional, Sequence, Tuple
import urllib

import objsize

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
    'by-publisher/elife/get-by-doi?'
)

DOI_ROOT_URL = 'https://doi.org/'
ELIFE_REVIEWED_PREPRINTS_URL = 'https://elifesciences.org/reviewed-preprints/'
HYPOTHESIS_URL = 'https://hypothes.is/a/'
SCIETY_ARTICLES_ACTIVITY_URL = 'https://sciety.org/articles/activity/'
SCIETY_ARTICLES_EVALUATIONS_URL = 'https://sciety.org/evaluations/hypothesis:'

DOCMAP_OUTPUT_TYPE_FOR_EVALUATION_SUMMARY = 'evaluation-summary'
DOCMAP_OUTPUT_TYPE_FOR_REPLY = 'reply'
DOCMAP_OUTPUT_TYPE_FOR_REVIEW_ARTICLE = 'review-article'

ADDITIONAL_PREPRINT_DOIS = (
  '10.1101/2022.06.24.497502',
  '10.1101/2022.07.26.501569',
  '10.1101/2022.06.30.498369',
  '10.1101/2022.05.30.22275761',
  '10.1101/2022.07.21.500925',
  '10.1101/2021.11.12.468444'
)


def get_docmap_assertions_value_for_preprint_manuscript_published_step(
    query_result_item: dict
) -> Sequence[dict]:
    return [{
        'item': {
            'type': 'preprint',
            'doi': query_result_item['preprint_doi'],
            'versionIdentifier': query_result_item['preprint_version']
        },
        'status': 'manuscript-published'
    }]


def get_docmap_actions_value_for_preprint_manuscript_published_step(
    query_result_item: dict
) -> Sequence[dict]:
    preprint_doi = query_result_item['preprint_doi']
    preprint_published_at_date = query_result_item['preprint_published_at_date']
    return [{
        'participants': [],
        'outputs': [{
            'type': 'preprint',
            'doi': preprint_doi,
            'url': query_result_item['preprint_url'],
            'published': (
                preprint_published_at_date.isoformat()
                if preprint_published_at_date
                else None
            ),
            'versionIdentifier': query_result_item['preprint_version'],
            '_tdmPath': query_result_item['tdm_path']
        }]
    }]


def get_docmaps_step_for_manuscript_published_status(
    query_result_item
) -> dict:
    return {
        'actions': get_docmap_actions_value_for_preprint_manuscript_published_step(
            query_result_item=query_result_item
        ),
        'assertions': get_docmap_assertions_value_for_preprint_manuscript_published_step(
            query_result_item=query_result_item
        ),
        'inputs': []
    }


def get_docmap_assertions_value_for_preprint_under_review_step(
    query_result_item: dict
) -> Sequence[dict]:
    return [{
        'item': {
            'type': 'preprint',
            'doi': query_result_item['preprint_doi'],
            'versionIdentifier': query_result_item['preprint_version']
        },
        'status': 'under-review',
        'happened': query_result_item['qc_complete_timestamp']
    }, {
        'item': {
            'type': 'preprint',
            'doi': query_result_item['elife_doi'] + '.' + query_result_item['elife_doi_version'],
            'versionIdentifier': query_result_item['elife_doi_version']
        },
        'status': 'draft'
    }]


def get_docmap_actions_value_for_preprint_under_review_step(
    query_result_item: dict
) -> Sequence[dict]:
    return [{
        'participants': [],
        'outputs': [{
            'identifier': query_result_item['manuscript_id'],
            'versionIdentifier': query_result_item['preprint_version'],
            'type': 'preprint',
            'doi': query_result_item['elife_doi'] + '.' + query_result_item['elife_doi_version']
        }]
    }]


def get_docmap_inputs_value_for_review_steps(
    query_result_item: dict
) -> Sequence[dict]:
    return [{
        'type': 'preprint',
        'doi': query_result_item['preprint_doi'],
        'url': query_result_item['preprint_url'],
        'versionIdentifier': query_result_item['preprint_version']
    }]


def get_docmaps_step_for_under_review_status(
    query_result_item
):
    return {
        'actions': get_docmap_actions_value_for_preprint_under_review_step(
            query_result_item=query_result_item
        ),
        'assertions': get_docmap_assertions_value_for_preprint_under_review_step(
            query_result_item=query_result_item
        ),
        'inputs': get_docmap_inputs_value_for_review_steps(
            query_result_item=query_result_item
        )
    }


def get_docmap_assertions_value_for_preprint_peer_reviewed_step(
    query_result_item: dict
) -> Sequence[dict]:
    return [{
        'item': {
            'type': 'preprint',
            'doi': query_result_item['preprint_doi'],
            'versionIdentifier': query_result_item['preprint_version']
        },
        'status': 'peer-reviewed'
    }]


def has_tag_containing(tags: list, text: str) -> bool:
    return any(
        text in tag
        for tag in tags
    )


def get_outputs_type_form_tags(
    tags: list
) -> Optional[str]:
    has_author_response_tag = has_tag_containing(tags, 'AuthorResponse')
    has_summary_tag = has_tag_containing(tags, 'Summary')
    has_review_tag = has_tag_containing(tags, 'Review')
    assert not (has_author_response_tag and has_summary_tag)
    if has_author_response_tag:
        return DOCMAP_OUTPUT_TYPE_FOR_REPLY
    if has_summary_tag:
        return DOCMAP_OUTPUT_TYPE_FOR_EVALUATION_SUMMARY
    if has_review_tag:
        return DOCMAP_OUTPUT_TYPE_FOR_REVIEW_ARTICLE
    return None


def get_participants_for_peer_reviewed_review_article_type() -> list:
    return [
        {
            'actor': {
                'name': 'anonymous',
                'type': 'person'
            },
            'role': 'peer-reviewer'
        }
    ]


def get_related_organization_detail(
    editor_detail: dict
) -> str:
    if editor_detail['country']:
        return editor_detail['institution'] + ', ' + editor_detail['country']
    return editor_detail['institution']


def get_participants_for_peer_reviewed_evalution_summary_type(
    editor_details_list,
    senior_editor_details_list
) -> Sequence[dict]:
    participants = []
    for editor_detail in editor_details_list:
        single_editor_dict = {
            'actor': {
                'name': editor_detail['name'],
                'type': 'person',
                '_relatesToOrganization': get_related_organization_detail(editor_detail)
            },
            'role': 'editor'
        }
        participants.append(single_editor_dict)
    for senior_editor_detail in senior_editor_details_list:
        single_senior_editor_dict = {
            'actor': {
                'name': senior_editor_detail['name'],
                'type': 'person',
                '_relatesToOrganization': get_related_organization_detail(senior_editor_detail)
            },
            'role': 'senior-editor'
        }
        participants.append(single_senior_editor_dict)
    return participants


def get_participants_for_preprint_peer_reviewed_step(
    query_result_item: dict,
    outputs_type: str
) -> Sequence[dict]:
    editor_details_list = query_result_item['editor_details']
    senior_editor_details_list = query_result_item['senior_editor_details']
    if outputs_type == DOCMAP_OUTPUT_TYPE_FOR_REVIEW_ARTICLE:
        return get_participants_for_peer_reviewed_review_article_type()
    if outputs_type == DOCMAP_OUTPUT_TYPE_FOR_EVALUATION_SUMMARY:
        return get_participants_for_peer_reviewed_evalution_summary_type(
            editor_details_list=editor_details_list,
            senior_editor_details_list=senior_editor_details_list
        )
    return []


def get_single_actions_value_for_preprint_peer_reviewed_step(
    query_result_item: dict,
    hypothesis_id: str,
    annotation_created_timestamp: str,
    outputs_type: str
) -> dict:
    preprint_doi = query_result_item['preprint_doi']
    return {
        'participants': get_participants_for_preprint_peer_reviewed_step(
            query_result_item=query_result_item,
            outputs_type=outputs_type
        ),
        'outputs': [
            {
                'type': outputs_type,
                'published': annotation_created_timestamp,
                'content': [
                    {
                        'type': 'web-page',
                        'url': f'{HYPOTHESIS_URL}{hypothesis_id}'
                    },
                    {
                        'type': 'web-page',
                        'url': (
                            f'{SCIETY_ARTICLES_ACTIVITY_URL}'
                            f'{preprint_doi}#hypothesis:{hypothesis_id}'
                        )
                    },
                    {
                        'type': 'web-page',
                        'url': (
                            f'{SCIETY_ARTICLES_EVALUATIONS_URL}'
                            f'{hypothesis_id}/content'
                        )
                    }
                ]
            }
        ]
    }


def iter_single_actions_value_from_query_result_for_peer_reviewed_step(
    query_result_item: dict
) -> Iterable[dict]:
    evaluations = query_result_item['evaluations']
    preprint_url = query_result_item['preprint_url']
    for evaluation in evaluations:
        hypothesis_id = evaluation['hypothesis_id']
        annotation_created_timestamp = evaluation['annotation_created_timestamp']
        outputs_type = get_outputs_type_form_tags(evaluation['tags'])
        evaluation_preprint_url = evaluation['uri']
        if evaluation_preprint_url != preprint_url:
            LOGGER.debug(
                'ignoring evaluation on another version: %r != %r',
                evaluation_preprint_url, preprint_url
            )
            continue
        if outputs_type in (
            DOCMAP_OUTPUT_TYPE_FOR_EVALUATION_SUMMARY,
            DOCMAP_OUTPUT_TYPE_FOR_REVIEW_ARTICLE,
            DOCMAP_OUTPUT_TYPE_FOR_REPLY
        ):
            yield get_single_actions_value_for_preprint_peer_reviewed_step(
                query_result_item=query_result_item,
                hypothesis_id=hypothesis_id,
                annotation_created_timestamp=annotation_created_timestamp,
                outputs_type=outputs_type
            )


def get_docmaps_step_for_peer_reviewed_status(
    query_result_item
):
    return {
        'actions': list(iter_single_actions_value_from_query_result_for_peer_reviewed_step(
            query_result_item=query_result_item
            )
        ),
        'assertions': get_docmap_assertions_value_for_preprint_peer_reviewed_step(
            query_result_item=query_result_item
        ),
        'inputs': get_docmap_inputs_value_for_review_steps(
            query_result_item=query_result_item
        )
    }


def iter_docmap_steps_for_query_result_item(query_result_item: dict) -> Iterable[dict]:
    yield get_docmaps_step_for_manuscript_published_status(query_result_item)
    yield get_docmaps_step_for_under_review_status(query_result_item)
    if query_result_item['evaluations']:
        yield get_docmaps_step_for_peer_reviewed_status(query_result_item)


def generate_docmap_steps(step_itearble: Iterable[dict]) -> dict:
    steps_dict = {}
    step_list = list(step_itearble)
    for step_index, step in enumerate(step_list):
        LOGGER.debug('step_index: %r', step_index)
        step_ranking_dict = {
            'next-step': ('_:b' + str(step_index + 1) if step_index + 1 < len(step_list) else None),
            'previous-step': '_:b' + str(step_index - 1) if step_index > 0 else None
        }
        steps_dict['_:b'+str(step_index)] = dict(step, **step_ranking_dict)
    return remove_key_with_none_value_only(steps_dict)


def get_docmap_item_for_query_result_item(query_result_item: dict) -> dict:
    qc_complete_timestamp_str = query_result_item['qc_complete_timestamp'].isoformat()
    publisher_json = query_result_item['publisher_json']
    LOGGER.debug('publisher_json: %r', publisher_json)
    id_query_param = {'preprint_doi': query_result_item['preprint_doi']}
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
    def __init__(  # pylint: disable=too-many-arguments
        self,
        gcp_project_name: str = 'elife-data-pipeline',
        query_results_cache: Optional[SingleObjectCache[Sequence[dict]]] = None,
        only_include_reviewed_preprint_type: bool = True,
        only_include_evaluated_preprints: bool = False,
        additionally_include_preprint_dois: Optional[Tuple[str]] = None
    ) -> None:
        self.gcp_project_name = gcp_project_name
        self.docmaps_index_query = (
            Path(get_sql_path('docmaps_index.sql')).read_text(encoding='utf-8')
        )
        assert not (only_include_reviewed_preprint_type and only_include_evaluated_preprints)
        assert not (additionally_include_preprint_dois and not only_include_reviewed_preprint_type)
        if only_include_reviewed_preprint_type:
            self.docmaps_index_query += (
                '\nWHERE is_reviewed_preprint_type AND is_or_was_under_review'
            )
        if only_include_reviewed_preprint_type and additionally_include_preprint_dois:
            self.docmaps_index_query += f'\nOR preprint_doi IN {additionally_include_preprint_dois}'
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

    def iter_docmaps(self, preprint_doi: Optional[str] = None) -> Iterable[dict]:
        bq_result_list = self._query_results_cache.get_or_load(
            load_fn=self._load_query_results_from_bq
        )
        if preprint_doi:
            bq_result_list = [
                bq_result
                for bq_result in bq_result_list
                if bq_result['preprint_doi'] == preprint_doi
            ]
        for bq_result in bq_result_list:
            yield get_docmap_item_for_query_result_item(bq_result)

    def get_docmaps_by_doi(self, preprint_doi: str) -> Sequence[dict]:
        return list(self.iter_docmaps(preprint_doi))

    def get_docmaps_index(self) -> dict:
        article_docmaps_list = list(self.iter_docmaps())
        return {'docmaps': article_docmaps_list}
