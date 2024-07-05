import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from data_hub_api.kotahi_docmaps.v1.provider import DocmapsProvider


LOGGER = logging.getLogger(__name__)


def create_docmaps_router(
    docmaps_provider: DocmapsProvider
) -> APIRouter:
    router = APIRouter()

    @router.get("/v1/index")
    def get_kotahi_docmaps_index():
        return docmaps_provider.get_docmaps_index()

    @router.get("/v1/by-publisher/elife/get-by-manuscript-id")
    def get_kotahi_docmap_by_manuscript_id_by_publisher_elife(manuscript_id: str):
        docmaps = docmaps_provider.get_docmaps_by_manuscript_id(manuscript_id)
        if not docmaps:
            raise HTTPException(
                status_code=404,
                detail="No Docmaps available for requested manuscript from the publisher eLife"
            )
        assert len(docmaps) == 1
        return docmaps[0]

    @router.get("/v1/evaluation/get-by-evaluation-id", response_class=PlainTextResponse)
    def get_evaluation_text_by_evaluation_id(evaluation_id: str):
        evaluation_text = docmaps_provider.get_evaluation_html_by_evaluation_id(evaluation_id)
        if not evaluation_text:
            raise HTTPException(
                status_code=404,
                detail="No evaluation available for requested evaluation_id"
            )
        return evaluation_text

    return router
