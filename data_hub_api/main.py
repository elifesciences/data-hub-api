import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from data_hub_api.docmaps.v2.api_router import create_docmaps_router
from data_hub_api.kotahi_docmaps.v1.api_router import (
    create_docmaps_router as create_docmaps_router_for_kotahi
)

from data_hub_api.utils.cache import InMemorySingleObjectCache
from data_hub_api.docmaps.v2.provider import DocmapsProvider
from data_hub_api.kotahi_docmaps.v1.provider import DocmapsProvider as KotahiDocmapsProvider


LOGGER = logging.getLogger(__name__)


def create_app():
    app = FastAPI()

    @app.middleware("http")
    async def log_requests(request, call_next):
        user_agent = request.headers.get("user-agent", "unknown")
        LOGGER.info(
            f"Received request: {request.method} {request.url.path} | User-Agent: {user_agent}"
        )
        response = await call_next(request)
        return response

    docmaps_v2_max_age_in_seconds = 10 * 60  # 10 minutes
    kotahi_docmaps_max_age_in_seconds = 60 * 60  # 1 hour

    enhanced_preprints_docmaps_provider = DocmapsProvider(
        query_results_cache=InMemorySingleObjectCache(
            max_age_in_seconds=docmaps_v2_max_age_in_seconds
        )
    )

    kotahi_docmaps_provider = KotahiDocmapsProvider(
        data_cache=InMemorySingleObjectCache(
            max_age_in_seconds=kotahi_docmaps_max_age_in_seconds
        )
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
        create_docmaps_router_for_kotahi(
            kotahi_docmaps_provider
        ),
        prefix='/kotahi/docmaps'
    )

    return app
