from datetime import date, datetime
from typing import Optional, Sequence, TypedDict


ApiEvaluationEmailInput = TypedDict(
    'ApiEvaluationEmailInput',
    {
        'long_manuscript_identifier': str,
        'email_subject': list,
        'converted_body': str,
        'email_timestamp': datetime,
    }
)

ApiEditorDetailInput = TypedDict(
    'ApiEditorDetailInput',
    {
        'name': str,
        'institution': str,
        'country': Optional[str],
        'title': Optional[str],
        'first_name': str,
        'middle_name': Optional[str],
        'last_name': str,
        'city': Optional[str]
    }
)

ApiSubjectAreaInput = TypedDict(
    'ApiSubjectAreaInput',
    {
        'subject_area_name': str
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
        'evaluation_emails': Sequence[ApiEvaluationEmailInput],
        'rp_publication_timestamp': Optional[datetime],
        'vor_publication_date': Optional[date],
        'subject_areas': Sequence[ApiSubjectAreaInput]
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
