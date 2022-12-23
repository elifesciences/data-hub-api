import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from data_hub_api.docmaps.provider import DocmapsProvider


LOGGER = logging.getLogger(__name__)


def create_app():
    app = FastAPI()

    enhanced_preprints_docmaps_provider = DocmapsProvider(
        only_include_reviewed_preprint_type=True,
        only_include_evaluated_preprints=False
    )

    public_reviews_docmaps_provider = DocmapsProvider(
        only_include_reviewed_preprint_type=False,
        only_include_evaluated_preprints=True
    )

    @app.get("/")
    def get_root():
        with open("data_hub_api/index.html", "r", encoding='utf-8') as file:
            html_content = file.read()
        return HTMLResponse(content=html_content, status_code=200)

    @app.get("/enhanced-preprints/docmaps/v1/index")
    def get_enhanced_preprints_docmaps_index():
        return enhanced_preprints_docmaps_provider.get_docmaps_index()

    @app.get("/public-reviews/docmaps/v1/index")
    def get_public_reviews_docmaps_index():
        return public_reviews_docmaps_provider.get_docmaps_index()

    return app
