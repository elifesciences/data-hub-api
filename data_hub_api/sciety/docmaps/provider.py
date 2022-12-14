import json
from pathlib import Path
from typing import Iterable


class ScietyDocmapsProvider:
    def iter_docmaps(self) -> Iterable[dict]:
        docmaps_path = Path('./data/docmaps/')
        for docmaps_file_path in docmaps_path.iterdir():
            yield json.loads(docmaps_file_path.read_bytes())

    def get_docmaps_index(self) -> dict:
        article_docmaps_list = list(self.iter_docmaps())
        return {'articles': article_docmaps_list}
