import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse

from data_hub_api.docmaps.v2.provider import DocmapsProvider


LOGGER = logging.getLogger(__name__)


def create_docmaps_router(
    docmaps_provider: DocmapsProvider
) -> APIRouter:
    router = APIRouter()

    @router.get("/v2/index", response_class=StreamingResponse)
    def stream_docmaps_index() -> StreamingResponse:
        return StreamingResponse(
            docmaps_provider.iter_docmaps_index_json_stream(),
            media_type="application/json"
        )

    @router.get("/v2/by-publisher/elife/get-by-manuscript-id")
    def get_enhanced_preprints_docmaps_by_manuscript_id_by_publisher_elife(manuscript_id: str):
        docmaps = docmaps_provider.get_docmaps_by_manuscript_id(manuscript_id)
        if not docmaps:
            raise HTTPException(
                status_code=404,
                detail="No Docmaps available for requested manuscript from the publisher eLife"
            )
        assert len(docmaps) == 1
        return docmaps[0]

    @router.get("/v2/evaluation/get-by-evaluation-id", response_class=HTMLResponse)
    def get_evaluation_text_by_evaluation_id(evaluation_id: str):
        evaluation_text = 'dummy evaluation text for evaluation_id: ' + evaluation_id
        return evaluation_text

    return router
