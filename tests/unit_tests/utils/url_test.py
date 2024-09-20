from data_hub_api.utils.url import get_basepath


class TestGetBasePath:
    def test_get_default_basepath(self):
        assert get_basepath() == 'https://data-hub-api.elifesciences.org/'

    def test_get_overridden_basepath(self, monkeypatch):
        monkeypatch.setenv('DOCMAP_BASEPATH', 'http://new-basepath/')
        assert get_basepath() == 'http://new-basepath/'
