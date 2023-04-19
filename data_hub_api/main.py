import logging

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from data_hub_api.utils.cache import InMemorySingleObjectCache
from data_hub_api.docmaps.provider import ADDITIONAL_PREPRINT_DOIS, DocmapsProvider


LOGGER = logging.getLogger(__name__)


def create_docmaps_router(
    docmaps_provider: DocmapsProvider
) -> APIRouter:
    router = APIRouter()

    @router.get("/v1/index")
    def get_enhanced_preprints_docmaps_index():
        return docmaps_provider.get_docmaps_index()

    @router.get("/v1/by-publisher/elife/get-by-manuscript-id")
    def get_enhanced_preprints_docmaps_by_manuscript_id_by_publisher_elife(manuscript_id: str):
        docmaps = docmaps_provider.get_docmaps_by_manuscript_id(manuscript_id)
        if not docmaps:
            raise HTTPException(
                status_code=404,
                detail="No Docmaps available for requested manuscript from the publisher eLife"
            )
        assert len(docmaps) == 1
        return docmaps[0]

    return router


def create_app():
    app = FastAPI()

    max_age_in_seconds = 60 * 60  # 1 hour

    enhanced_preprints_docmaps_provider = DocmapsProvider(
        only_include_reviewed_preprint_type=True,
        only_include_evaluated_preprints=False,
        additionally_include_preprint_dois=ADDITIONAL_PREPRINT_DOIS,
        query_results_cache=InMemorySingleObjectCache(max_age_in_seconds=max_age_in_seconds)
    )

    public_reviews_docmaps_provider = DocmapsProvider(
        only_include_reviewed_preprint_type=False,
        only_include_evaluated_preprints=True,
        query_results_cache=InMemorySingleObjectCache(max_age_in_seconds=max_age_in_seconds)
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
