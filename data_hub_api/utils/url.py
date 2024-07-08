import os

def get_basepath():
    return (
        os.getenv(
            'DOCMAP_BASEPATH',
            'https://data-hub-api.elifesciences.org/'
        )
    )
