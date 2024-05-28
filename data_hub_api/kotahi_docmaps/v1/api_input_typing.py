from datetime import date, datetime
from typing import Optional, Sequence, TypedDict, Union


ApiEditorDetailInput = TypedDict(
    'ApiEditorDetailInput',
    {
        'name': str,
        'institution': Optional[str],
        'country': Optional[str],
        'title': Optional[str],
        'first_name': str,
        'middle_name': Optional[str],
        'last_name': str,
        'city': Optional[str]
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
        'email_body': Optional[str],
        'email_timestamp': Optional[datetime]
    }
)

ApiInput = TypedDict(
    'ApiInput',
    {
        'publisher_json': Union[str, dict],
        'manuscript_id': str,
        'elife_doi': str,
        'license': str,
        'is_reviewed_preprint_type': bool,
        'manuscript_versions': Sequence[ApiManuscriptVersionInput]
    }
)
