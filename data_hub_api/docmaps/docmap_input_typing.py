from datetime import datetime
from typing import TypedDict


DocmapInput = TypedDict(
    'DocmapInput',
    {
        'manuscript_id': str,
        'qc_complete_timestamp': datetime,
        'under_review_timestamp': datetime,
        'publisher_json': dict,
        'elife_doi': str,
        'license': str,
        'editor_details': list,
        'senior_editor_details': list,
        'evaluations': list,
        'preprints': list
    },
    total=False
)
