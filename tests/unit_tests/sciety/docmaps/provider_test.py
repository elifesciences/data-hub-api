from data_hub_api.sciety.docmaps.provider import ScietyDocmapsProvider


class TestScietyDocmapsProvider:
    def test_should_create_index_with_non_empty_articles(self):
        docmaps_index = ScietyDocmapsProvider().get_docmaps_index()
        assert docmaps_index['articles']
