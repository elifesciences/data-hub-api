import logging

from fastapi import FastAPI

from data_hub_api.enhanced_preprints.docmaps.provider import ScietyDocmapsProvider


LOGGER = logging.getLogger(__name__)


def create_app():
    app = FastAPI()
    sciety_docmaps_provider = ScietyDocmapsProvider()

    @app.get("/")
    def get_root():
        return {"Hello": "World"}

    @app.get("/enhanced-preprints/docmaps/v1/index")
    def get_sciety_docmaps_index():
        return sciety_docmaps_provider.get_docmaps_index()

    return app
