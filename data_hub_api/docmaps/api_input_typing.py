from datetime import datetime
from typing import Optional, Sequence, TypedDict


ApiEditorDetailInput = TypedDict(
    'ApiEditorDetailInput',
    {
        'name': str,
        'institution': str,
        'country': Optional[str],
    },
    total=False
)

ApiInput = TypedDict(
    'ApiInput',
    {
        'manuscript_id': str,
        'qc_complete_timestamp': datetime,
        'under_review_timestamp': datetime,
        'publisher_json': dict,
        'elife_doi': str,
        'license': str,
        'editor_details': Sequence[ApiEditorDetailInput],
        'senior_editor_details': Sequence[ApiEditorDetailInput],
        'evaluations': list,
        'preprints': list
    },
    total=False
)
