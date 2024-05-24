from datetime import date, datetime
from typing import Optional, Sequence, TypedDict, Union


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
        'institution': Optional[str],
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
        'meca_path': Optional[str],
        'evaluations': Sequence[ApiEvaluationInput],
        'rp_publication_timestamp': Optional[datetime],
        'vor_publication_date': Optional[date],
        'subject_areas': Sequence[ApiSubjectAreaInput]
    }
)

ApiRelatedContentInput = TypedDict(
    'ApiRelatedContentInput',
    {
        'manuscript_id': Optional[str],
        'manuscript_type': Optional[str],
        'manuscript_title': Optional[str],
        'manuscript_authors_csv': Optional[str],
        'collection_id': Optional[str],
        'collection_title': Optional[str],
        'collection_curator_name': Optional[str],
        'is_collection_curator_et_al': Optional[bool],
        'collection_thumbnail_url': Optional[str],
        'podcast_id': Optional[int],
        'podcast_chapter_title': Optional[str],
        'podcast_chapter_time': Optional[int]
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
        'manuscript_versions': Sequence[ApiManuscriptVersionInput],
        'related_content': Sequence[ApiRelatedContentInput]
    }
)
