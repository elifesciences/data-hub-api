import logging

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from data_hub_api.docmaps.provider import DocmapsProvider


LOGGER = logging.getLogger(__name__)


def create_docmaps_router(
    docmaps_provider: DocmapsProvider
) -> APIRouter:
    router = APIRouter()

    @router.get("/v1/index")
    def get_enhanced_preprints_docmaps_index():
        return docmaps_provider.get_docmaps_index()

    @router.get("/v1/get-by-doi")
    def get_enhanced_preprints_docmaps_by_preprint_doi(preprint_doi: str):
        docmaps = docmaps_provider.get_docmaps_by_doi(preprint_doi)
        if not docmaps:
            raise HTTPException(
                status_code=404,
                detail="No Docmaps available for requested DOI"
            )
        return docmaps

    return router


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

    app.include_router(
        create_docmaps_router(
            enhanced_preprints_docmaps_provider
        ),
        prefix='/enhanced-preprints/docmaps'
    )

    app.include_router(
        create_docmaps_router(
            public_reviews_docmaps_provider
        ),
        prefix='/public-reviews/docmaps'
    )

    return app
