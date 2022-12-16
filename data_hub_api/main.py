import logging

from fastapi import FastAPI

from data_hub_api.enhanced_preprints.docmaps.provider import EnhancedPreprintsDocmapsProvider


LOGGER = logging.getLogger(__name__)


def create_app():
    app = FastAPI()
    enhanced_preprints_docmaps_provider = EnhancedPreprintsDocmapsProvider()

    @app.get("/")
    def get_root():
        return {"Hello": "World"}

    @app.get("/enhanced-preprints/docmaps/v1/index")
    def get_enhanced_preprints_docmaps_index():
        return enhanced_preprints_docmaps_provider.get_docmaps_index()

    return app
