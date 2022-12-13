from fastapi.testclient import TestClient

from data_hub_api.main import create_app


def test_read_main():
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

class TestGetScietyDocmapsIndex:
    def test_should_return_json_with_empty_articles_list(self):
        client = TestClient(create_app())
        response = client.get("/sciety/docmaps/v1/index")
        assert response.json() == {'articles':[]}
