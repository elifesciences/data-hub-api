import requests
import json

DOCMAP_BY_MANUSCRIPT_URL = (
    'http://localhost:8000/enhanced-preprints/docmaps/v2/by-publisher/elife/get-by-manuscript-id'
)


def test_should_match_example_response_for_86628():
    response = requests.get(url=DOCMAP_BY_MANUSCRIPT_URL, params={'manuscript_id': '86628'})
    response.raise_for_status()
    with open('data/docmaps/sample_docmap_for_86628.json', 'r') as file:
        example_response = json.load(file)
    assert response.json() == example_response
