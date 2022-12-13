from pathlib import Path
import logging
from fastapi import FastAPI

LOGGER = logging.getLogger(__name__)


def create_app():
    app = FastAPI()

    @app.get("/")
    def get_root():
        return {"Hello": "World"}

    @app.get("/sciety/docmaps/v1/index")
    def get_sciety_docmaps_index():
        return {'articles': [Path('data/docmaps/minimal_docmaps_example.json').read_text()]}

    return app
