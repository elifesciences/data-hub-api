from datetime import datetime
from typing import Optional, Sequence, TypedDict


DocmapEditorDetailInput = TypedDict(
    'DocmapEditorDetailInput',
    {
        'name': str,
        'institution': str,
        'country': Optional[str],
    },
    total=False
)

DocmapInput = TypedDict(
    'DocmapInput',
    {
        'manuscript_id': str,
        'qc_complete_timestamp': datetime,
        'under_review_timestamp': datetime,
        'publisher_json': dict,
        'elife_doi': str,
        'license': str,
        'editor_details': Sequence[DocmapEditorDetailInput],
        'senior_editor_details': Sequence[DocmapEditorDetailInput],
        'evaluations': list,
        'preprints': list
    },
    total=False
)
