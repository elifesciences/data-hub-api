from unittest.mock import patch, MagicMock
from typing import Iterable, cast

import pytest
from data_hub_api.docmaps.codecs.docmaps import ADDITIONAL_MANUSCRIPT_IDS
from data_hub_api.docmaps.api_input_typing import ApiInput

from data_hub_api.utils.cache import InMemorySingleObjectCache
from data_hub_api.docmaps import provider as provider_module
from data_hub_api.docmaps.provider import (
    get_docmap_item_for_query_result_item,
    DocmapsProvider
)
from tests.unit_tests.docmaps.test_data import DOCMAPS_QUERY_RESULT_ITEM_1


@pytest.fixture(name='iter_dict_from_bq_query_mock', autouse=True)
def _iter_dict_from_bq_query_mock() -> Iterable[MagicMock]:
    with patch.object(provider_module, 'iter_dict_from_bq_query') as mock:
        yield mock


class TestEnhancedPreprintsDocmapsProvider:
    def test_should_create_index_with_non_empty_docmaps(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = iter([
            DOCMAPS_QUERY_RESULT_ITEM_1
        ])
        docmaps_index = DocmapsProvider().get_docmaps_index()
        assert docmaps_index['docmaps'] == [
            get_docmap_item_for_query_result_item(cast(ApiInput, DOCMAPS_QUERY_RESULT_ITEM_1))
        ]

    def test_should_cache_docmaps_query_results(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = [
            DOCMAPS_QUERY_RESULT_ITEM_1
        ]
        docmaps_provider = DocmapsProvider(
            query_results_cache=InMemorySingleObjectCache(max_age_in_seconds=10)
        )
        docmaps_provider.get_docmaps_index()
        docmaps_index = docmaps_provider.get_docmaps_index()
        assert iter_dict_from_bq_query_mock.call_count == 1
        assert docmaps_index['docmaps'] == [
            get_docmap_item_for_query_result_item(cast(ApiInput, DOCMAPS_QUERY_RESULT_ITEM_1))
        ]

    def test_should_add_is_reviewed_preprint_and_is_under_review_type_where_clause_to_query(
        self
    ):
        provider = DocmapsProvider(
            only_include_reviewed_preprint_type=True,
            only_include_evaluated_preprints=False,
            additionally_include_manuscript_ids=[]
        )
        assert provider.docmaps_index_query.rstrip().endswith(
            'WHERE is_reviewed_preprint_type AND is_or_was_under_review'
        )

    def test_should_add_additional_manuscript_ids_to_query_filter(
        self
    ):
        provider = DocmapsProvider(
            only_include_reviewed_preprint_type=True,
            only_include_evaluated_preprints=False,
            additionally_include_manuscript_ids=ADDITIONAL_MANUSCRIPT_IDS
        )
        assert provider.docmaps_index_query.rstrip().endswith(
            f'OR result.manuscript_id IN {ADDITIONAL_MANUSCRIPT_IDS}'
        )

    def test_should_add_has_evaluatons_where_clause_to_query(
        self
    ):
        provider = DocmapsProvider(
            only_include_reviewed_preprint_type=False,
            only_include_evaluated_preprints=True
        )
        assert provider.docmaps_index_query.rstrip().endswith('WHERE has_evaluations')

    def test_should_allow_both_reviewed_prerint_type_and_evaluated_preprints_filter(
        self
    ):
        with pytest.raises(AssertionError):
            DocmapsProvider(
                only_include_reviewed_preprint_type=True,
                only_include_evaluated_preprints=True
            )
