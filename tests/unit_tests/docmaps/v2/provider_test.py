import json
from unittest.mock import patch, MagicMock
from typing import Iterable, cast

import pytest
from data_hub_api.docmaps.v2.api_input_typing import ApiInput

from data_hub_api.utils.cache import InMemorySingleObjectCache
from data_hub_api.docmaps.v2 import provider as provider_module
from data_hub_api.docmaps.v2.provider import (
    get_docmap_item_for_query_result_item,
    DocmapsProvider,
    get_html_formatted_evaluation_content
)
from tests.unit_tests.docmaps.v2.test_data import (
    DOCMAPS_QUERY_RESULT_EVALUATION_1,
    DOCMAPS_QUERY_RESULT_ITEM_1,
    MANUSCRIPT_VERSION_1
)


@pytest.fixture(name='iter_dict_from_bq_query_mock', autouse=True)
def _iter_dict_from_bq_query_mock() -> Iterable[MagicMock]:
    with patch.object(provider_module, 'iter_dict_from_bq_query') as mock:
        yield mock


def _get_docmaps_index_dict(provider: DocmapsProvider) -> dict:
    return json.loads(
        ''.join(provider.iter_docmaps_index_json_stream())
    )


class TestGetHtmlFormattedEvaluationContent:
    def test_should_return_same_evaluation_content_if_no_markdown(self):
        content = 'evaluation content for evaluation_id_1'
        assert get_html_formatted_evaluation_content(content) == f'<p>{content}</p>'

    def test_should_return_html_formatted_content_for_bold_markdown(self):
        assert get_html_formatted_evaluation_content('**bold**') == '<p><strong>bold</strong></p>'

    def test_should_return_html_formatted_content_for_italic_markdown(self):
        assert get_html_formatted_evaluation_content('*italic*') == '<p><em>italic</em></p>'

    def test_should_return_html_formatted_content_for_both_bold_and_italic(self):
        bold_italic = '***bold/italics** italics*'
        bold_italic_html = '<p><em><strong>bold/italics</strong> italics</em></p>'
        assert get_html_formatted_evaluation_content(bold_italic) == bold_italic_html


class TestDocmapsProvider:
    def test_should_create_index_with_non_empty_docmaps(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = iter([
            DOCMAPS_QUERY_RESULT_ITEM_1
        ])
        docmaps_index = _get_docmaps_index_dict(DocmapsProvider())
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
        docmaps_index = _get_docmaps_index_dict(docmaps_provider)
        docmaps_index = _get_docmaps_index_dict(docmaps_provider)
        assert iter_dict_from_bq_query_mock.call_count == 1
        assert docmaps_index['docmaps'] == [
            get_docmap_item_for_query_result_item(cast(ApiInput, DOCMAPS_QUERY_RESULT_ITEM_1))
        ]

    def test_should_return_none_for_invalid_evaluation_id(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = []
        docmaps_provider = DocmapsProvider()
        assert docmaps_provider.get_evaluation_content_by_id('not_found_id_1') is None

    def test_should_return_evaluation_content_for_valid_evaluation_id(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = [{
            **DOCMAPS_QUERY_RESULT_ITEM_1,
            'manuscript_versions': [{
                **MANUSCRIPT_VERSION_1,  # type: ignore
                'evaluations': [DOCMAPS_QUERY_RESULT_EVALUATION_1]
            }]
        }]
        docmaps_provider = DocmapsProvider()
        assert docmaps_provider.get_evaluation_content_by_id(
            DOCMAPS_QUERY_RESULT_EVALUATION_1['hypothesis_id']
        ) == get_html_formatted_evaluation_content(
            DOCMAPS_QUERY_RESULT_EVALUATION_1['annotation_content']
        )
