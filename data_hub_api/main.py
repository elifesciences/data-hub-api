from fastapi import FastAPI


def create_app():
    app = FastAPI()

    @app.get("/")
    def get_root():
        return {"Hello": "World"}

    @app.get("/sciety/docmaps/v1/index")
    def get_sciety_docmaps_index():
        return {'articles': []}

    return app
