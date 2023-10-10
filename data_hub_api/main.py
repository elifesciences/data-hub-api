import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from data_hub_api.config import ADDITIONAL_MANUSCRIPT_IDS
from data_hub_api.docmaps.v1.api_router import create_docmaps_router as create_docmaps_router_v1
from data_hub_api.docmaps.v2.api_router import create_docmaps_router
from data_hub_api.docmaps.v2.kotahi_api_router import (
    create_docmaps_router as kotahi_create_docmaps_router
)
from data_hub_api.utils.cache import InMemorySingleObjectCache
from data_hub_api.docmaps.v1.provider import DocmapsProviderV1
from data_hub_api.docmaps.v2.provider import DocmapsProvider
from data_hub_api.docmaps.v2.kotahi_provider import DocmapsProvider as KotahiDocmapsProvider


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
        sql_query_name='docmaps_index.sql',
        query_results_cache=InMemorySingleObjectCache(max_age_in_seconds=max_age_in_seconds)
    )

    kotahi_docmaps_provider = KotahiDocmapsProvider(
        sql_query_name='kotahi_docmaps_index.sql',
        query_results_cache=InMemorySingleObjectCache(max_age_in_seconds=max_age_in_seconds)
    )

    public_reviews_docmaps_provider = DocmapsProviderV1(
        only_include_reviewed_preprint_type=False,
        only_include_evaluated_preprints=True,
        query_results_cache=InMemorySingleObjectCache(max_age_in_seconds=max_age_in_seconds)
    )

# http://localhost:8000/enhanced-preprints/docmaps/v2/index
# https://data-hub-api.elifesciences.org/enhanced-preprints/docmaps/v2/by-publisher/elife/get-by-manuscript-id?manuscript_id=86628
# https://data-hub-api.elifesciences.org/kotahi/docmaps/v1/by-publisher/elife/get-by-manuscript-id?manuscript_id=86628
# http://localhost:8000/kotahi/docmaps/v1/index
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
        kotahi_create_docmaps_router(
            kotahi_docmaps_provider
        ),
        prefix='/kotahi/docmaps'
    )

    app.include_router(
        create_docmaps_router_v1(
            public_reviews_docmaps_provider
        ),
        prefix='/public-reviews/docmaps'
    )

    return app
