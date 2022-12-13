import json
from pathlib import Path
from fastapi.testclient import TestClient

from data_hub_api.main import create_app


def test_read_main():
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


class TestGetScietyDocmapsIndex:
    def test_should_return_json_with_articles_list(self):
        client = TestClient(create_app())
        response = client.get("/sciety/docmaps/v1/index")
        docmaps_1 = Path('data/docmaps/minimal_docmaps_example.json')
        docmaps_2 = Path('data/docmaps/minimal_docmaps_example_2.json')
        assert response.json() == {
            'articles': [json.loads(docmaps_1.read_bytes()), json.loads(docmaps_2.read_bytes())]
        }
