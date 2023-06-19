import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from data_hub_api.config import ADDITIONAL_MANUSCRIPT_IDS
from data_hub_api.docmaps.v1.api_router import create_docmaps_router as create_docmaps_router_v1
from data_hub_api.docmaps.v2.api_router import create_docmaps_router

from data_hub_api.utils.cache import InMemorySingleObjectCache
from data_hub_api.docmaps.v1.provider import DocmapsProviderV1
from data_hub_api.docmaps.v2.provider import DocmapsProvider


LOGGER = logging.getLogger(__name__)


def create_app():
    app = FastAPI()

    max_age_in_seconds = 60 * 60  # 1 hour

    enhanced_preprints_docmaps_provider_v1 = DocmapsProviderV1(
        only_include_reviewed_preprint_type=True,
        only_include_evaluated_preprints=False,
        additionally_include_manuscript_ids=ADDITIONAL_MANUSCRIPT_IDS,
        query_results_cache=InMemorySingleObjectCache(max_age_in_seconds=max_age_in_seconds)
    )

    enhanced_preprints_docmaps_provider = DocmapsProvider(
        only_include_reviewed_preprint_type=True,
        additionally_include_manuscript_ids=ADDITIONAL_MANUSCRIPT_IDS,
        query_results_cache=InMemorySingleObjectCache(max_age_in_seconds=max_age_in_seconds)
    )

    public_reviews_docmaps_provider = DocmapsProviderV1(
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
        create_docmaps_router_v1(
            enhanced_preprints_docmaps_provider_v1
        ),
        prefix='/enhanced-preprints/docmaps'
    )

    app.include_router(
        create_docmaps_router(
            enhanced_preprints_docmaps_provider
        ),
        prefix='/enhanced-preprints/docmaps'
    )

    app.include_router(
        create_docmaps_router_v1(
            public_reviews_docmaps_provider
        ),
        prefix='/public-reviews/docmaps'
    )

    return app
