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
    }
)

ApiEditorDetailInput = TypedDict(
    'ApiEditorDetailInput',
    {
        'name': str,
        'institution': str,
        'country': Optional[str],
    }
)

ApiManuscriptVersionInput = TypedDict(
    'ApiManuscriptVersionInput',
    {
        'long_manuscript_identifier': str,
        'position_in_overall_stage': int,
        'qc_complete_timestamp': datetime,
        'under_review_timestamp': Optional[datetime],
        'editor_details': Sequence[ApiEditorDetailInput],
        'senior_editor_details': Sequence[ApiEditorDetailInput],
        'preprint_url': str,
        'elife_doi_version_str': str,
        'preprint_doi': str,
        'preprint_version': Optional[str],
        'preprint_published_at_date': Optional[date],
        'meca_path': Optional[str],
        'evaluations': Sequence[ApiEvaluationInput],
        'rp_publication_timestamp': Optional[datetime],
        'vor_publication_date': Optional[date]
    }
)


ApiInput = TypedDict(
    'ApiInput',
    {
        'publisher_json': str,
        'manuscript_id': str,
        'elife_doi': str,
        'license': str,
        'is_reviewed_preprint_type': bool,
        'manuscript_versions': Sequence[ApiManuscriptVersionInput]
    }
)
