from datetime import date, datetime
from typing import Optional, Sequence, TypedDict


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

ApiManuscriptVersionInput = TypedDict(
    'ApiManuscriptVersionInput',
    {
        'long_manuscript_identifier': str,
        'position_in_overall_stage': int,
        'qc_complete_timestamp': datetime,
        'under_review_timestamp': datetime,
        'editor_details': Sequence[ApiEditorDetailInput],
        'senior_editor_details': Sequence[ApiEditorDetailInput],
        'preprint_url': str,
        'elife_doi_version_str': str,
        'preprint_doi': str,
        'preprint_version': str,
        'preprint_published_at_date': date,
        'meca_path': str,
        'evaluations': Sequence[ApiEvaluationInput],
        'rp_publication_timestamp': Optional[datetime]
    },
    total=False
)


ApiInput = TypedDict(
    'ApiInput',
    {
        'publisher_json': dict,
        'manuscript_id': str,
        'elife_doi': str,
        'license': str,
        'is_reviewed_preprint_type': bool,
        'manuscript_versions': Sequence[ApiManuscriptVersionInput]
    },
    total=False
)
