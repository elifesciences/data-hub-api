from unittest.mock import patch, MagicMock
from typing import Iterable, cast

import pytest
from data_hub_api.docmaps.v2.codecs.evaluation import DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY
from data_hub_api.kotahi_docmaps.v1.api_input_typing import ApiInput
from data_hub_api.kotahi_docmaps.v1.codecs.evaluation import generate_evaluation_id

from data_hub_api.utils.cache import InMemorySingleObjectCache
from data_hub_api.kotahi_docmaps.v1 import provider as provider_module
from data_hub_api.kotahi_docmaps.v1.provider import (
    get_docmap_item_for_query_result_item,
    DocmapsProvider
)
from tests.unit_tests.kotahi_docmaps.v1.test_data import (
    DOCMAPS_QUERY_RESULT_ITEM_1,
    DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATION_EMAILS_1,
    ELIFE_ASSESSMENT_1,
    LONG_MANUSCRIPT_ID_1
)


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
            data_cache=InMemorySingleObjectCache(max_age_in_seconds=10)
        )
        docmaps_provider.get_docmaps_index()
        docmaps_index = docmaps_provider.get_docmaps_index()
        assert iter_dict_from_bq_query_mock.call_count == 1
        assert docmaps_index['docmaps'] == [
            get_docmap_item_for_query_result_item(cast(ApiInput, DOCMAPS_QUERY_RESULT_ITEM_1))
        ]

    def test_should_return_none_if_there_is_no_data_from_bq(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = iter([])
        result = DocmapsProvider().get_evaluation_text_by_evaluation_id('not_found_id_1')
        assert result is None

    def test_should_return_none_if_there_is_no_evaluation_email_in_bq_result(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = iter([DOCMAPS_QUERY_RESULT_ITEM_1])
        result = DocmapsProvider().get_evaluation_text_by_evaluation_id('not_found_id_1')
        assert result is None

    def test_should_return_evaluation_text_by_id(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = iter(
            [DOCMAPS_QUERY_RESULT_ITEM_WITH_EVALUATION_EMAILS_1]
        )
        evaluation_id = generate_evaluation_id(
            LONG_MANUSCRIPT_ID_1,
            DOCMAP_EVALUATION_TYPE_FOR_EVALUATION_SUMMARY,
            1
        )
        result = DocmapsProvider().get_evaluation_text_by_evaluation_id(evaluation_id)
        assert result == ELIFE_ASSESSMENT_1.strip()
