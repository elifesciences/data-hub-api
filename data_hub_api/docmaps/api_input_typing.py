from datetime import date, datetime
from typing import Optional, Sequence, TypedDict

ApiPreprintInput = TypedDict(
    'ApiPreprintInput',
    {
        'preprint_url': str,
        'elife_doi_version_str': str,
        'preprint_doi': str,
        'preprint_version': str,
        'preprint_published_at_date': date,
        'tdm_path': str
    },
    total=False
)

ApiEvaluationInput = TypedDict(
    'ApiEvaluationInput',
    {
        'hypothesis_id': str,
        'annotation_created_timestamp': datetime,
        'tags': list,
        'uri': str,
        'source_version': str,
        'evaluation_suffix': str
    },
    total=False
)

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
        'evaluations': Sequence[ApiEvaluationInput],
        'preprints': Sequence[ApiPreprintInput]
    },
    total=False
)
