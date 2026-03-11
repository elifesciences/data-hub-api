import os


def get_basepath() -> str:
    return (
        os.getenv(
            'DOCMAP_BASEPATH',
            'https://data-hub-api.elifesciences.org/'
        )
    )
