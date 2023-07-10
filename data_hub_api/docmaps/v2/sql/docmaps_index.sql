WITH t_hypothesis_annotation_with_doi AS (
  SELECT
    * EXCEPT (id, created),
    CASE 
      WHEN annotation.uri LIKE '%10.1101/%'
        THEN REGEXP_EXTRACT(annotation.uri, r'(10\.\d{3,}[^v]*)v?')
      WHEN annotation.uri LIKE '%researchsquare.com/article/rs-%'
        -- 'https://www.researchsquare.com/article/rs-2848731/v1' --> 'rs-2848731/v1'
        THEN CONCAT('10.21203/rs.3.', REGEXP_EXTRACT(annotation.uri, r'\/(\w+-\d+\/\w+)'))
      WHEN annotation.uri LIKE '%arxiv.org/abs/%'
        -- 'https://arxiv.org/abs/2305.01403v1' -->  '2305.01403'
        THEN CONCAT('10.48550/arXiv.', REGEXP_EXTRACT(annotation.uri, r'\/(\d+\.\d+)'))
      ELSE NULL
    END AS source_doi,
    CASE 
      WHEN annotation.uri LIKE '%10.1101/%'
        THEN REGEXP_EXTRACT(annotation.uri, r'(10\.\d{3,}[^v]*)v?')
      WHEN annotation.uri LIKE '%researchsquare.com/article/rs-%'
        -- 'https://www.researchsquare.com/article/rs-2848731/v1' --> 'rs-2848731/v1'
        THEN CONCAT('10.21203/rs.3.', REGEXP_EXTRACT(annotation.uri, r'\/(\w+-\d+)\/\w+'))
      WHEN annotation.uri LIKE '%arxiv.org/abs/%'
        -- 'https://arxiv.org/abs/2305.01403v1' -->  '2305.01403'
        THEN CONCAT('10.48550/arXiv.', REGEXP_EXTRACT(annotation.uri, r'\/(\d+\.\d+)'))
      ELSE NULL
    END AS source_doi_without_version,
    CASE 
      WHEN annotation.uri LIKE '%10.1101/%'
        THEN REGEXP_EXTRACT(annotation.uri, r'10\.\d{3,}.*v([1-9])')
      WHEN annotation.uri LIKE '%researchsquare.com/article/rs-%' OR annotation.uri LIKE '%arxiv.org/abs/%'
        THEN REGEXP_EXTRACT(annotation.uri, r'v(\d+)$') 
      ELSE NULL
    END AS source_doi_version,
    annotation.id AS hypothesis_id,
    annotation.created AS annotation_created_timestamp,
  FROM `elife-data-pipeline.de_proto.v_hypothesis_annotation` AS annotation
  WHERE annotation.group = 'q5X6RWJ6'
    AND created >= '2022-09-01' -- to ignore any public reviews posted before Sep 2022
),

t_manual_osf_preprint_match AS (
  SELECT
    * EXCEPT(rn)
  FROM
  (
    SELECT 
      *,
      ROW_NUMBER() OVER(PARTITION BY manuscript_id ORDER BY imported_timestamp DESC) AS rn
    FROM `elife-data-pipeline.prod.unmatched_manuscripts`
    WHERE osf_preprint_url IS NOT NULL
  )
  WHERE rn=1
),

t_hypothesis_with_temp_filtered_osf_annotations AS (
  SELECT
    *
  FROM t_hypothesis_annotation_with_doi
  WHERE (
    (uri LIKE 'https://psyarxiv.com/%' AND annotation_created_timestamp < '2023-07-01') -- filter for revisions
    OR
    uri NOT LIKE 'https://psyarxiv.com/%'
  )
),

t_hypothesis_annotation_with_osf_doi AS (
  SELECT 
    hypothesis.* EXCEPT(source_doi, source_doi_without_version, source_doi_version),
    IFNULL(source_doi, osf.preprint_doi) AS source_doi,
    IFNULL(source_doi_without_version, osf.preprint_doi) AS source_doi_without_version,
    IFNULL(source_doi_version, osf.preprint_doi_version) AS source_doi_version,
  FROM t_hypothesis_with_temp_filtered_osf_annotations AS hypothesis
  LEFT JOIN t_manual_osf_preprint_match AS osf
    ON hypothesis.uri = osf.osf_preprint_url
),

t_distinct_hypothesis_uri_doi_version AS (
  SELECT 
    DISTINCT
    uri,
    source_doi_without_version,
    source_doi_version
  FROM t_hypothesis_annotation_with_osf_doi
),

t_hypothesis_with_source_doi_rank AS (
  SELECT
    *,
    ROW_NUMBER() OVER(
      PARTITION BY source_doi_without_version
      ORDER BY source_doi_version
    ) AS source_doi_rank
  FROM t_distinct_hypothesis_uri_doi_version
),

t_hypothesis_uri_id_and_timestamp AS (
  SELECT
    uri,
    source_doi,
    source_doi_version,
    annotation_created_timestamp,
    hypothesis_id
  FROM t_hypothesis_annotation_with_osf_doi
),

t_distinct_hypothesis_with_evaluation_suffix_number AS (
  SELECT
    *,
    ROW_NUMBER() OVER(
      PARTITION BY source_doi, source_doi_version
      ORDER BY annotation_created_timestamp, hypothesis_id
    ) AS evaluation_suffix_number
  FROM t_hypothesis_uri_id_and_timestamp
),

t_hypothesis_annotation_with_evaluation_suffix AS (
  SELECT 
    annotation.hypothesis_id,
    annotation.annotation_created_timestamp,
    annotation.uri,
    annotation.tags,
    annotation.normalized_tags,
    annotation.source_doi,
    annotation.source_doi_version,
    doi_rank.source_doi_without_version,
    doi_rank.source_doi_rank,
    CONCAT('sa',CAST(t_evaluation_suffix.evaluation_suffix_number AS STRING)) AS evaluation_suffix
  FROM t_hypothesis_annotation_with_osf_doi AS annotation
  INNER JOIN t_hypothesis_with_source_doi_rank AS doi_rank
    ON annotation.uri = doi_rank.uri
  INNER JOIN t_distinct_hypothesis_with_evaluation_suffix_number AS t_evaluation_suffix
    ON annotation.uri = t_evaluation_suffix.uri 
    AND annotation.hypothesis_id = t_evaluation_suffix.hypothesis_id
),

t_reviewed_preprints AS (
  SELECT 
    * EXCEPT(
      source_site_id,
      preprint_url_from_ejp,
      ejp_normalized_title,
      biorxiv_medrxiv_normalized_title),
    (
      under_review_timestamp IS NOT NULL
      OR 
      (
        is_reviewed_preprint_type
        AND long_manuscript_identifier LIKE '%-VOR-%'
      )
    ) AS should_provide_docmaps_for,
  FROM `elife-data-pipeline.prod.v_manuscript_with_matching_preprint_server_doi`
  WHERE preprint_doi IS NOT NULL
),

t_reviewed_preprints_for_docmaps AS (
  SELECT * 
  FROM t_reviewed_preprints
  WHERE should_provide_docmaps_for
),

t_result_with_evaluations AS (
  SELECT 
    *,
    ARRAY(
      SELECT AS STRUCT
        *
      FROM t_hypothesis_annotation_with_evaluation_suffix AS annotation
      WHERE annotation.source_doi = t_reviewed_preprints_for_docmaps.preprint_doi
        AND annotation.source_doi_rank = t_reviewed_preprints_for_docmaps.position_in_overall_stage
    ) AS evaluations,
  FROM t_reviewed_preprints_for_docmaps
),

t_result_with_sorted_evaluations AS (
  SELECT
    result.* EXCEPT(evaluations),

    ARRAY(
      SELECT AS STRUCT evaluation.*
      FROM result.evaluations AS evaluation
      ORDER BY evaluation.annotation_created_timestamp
    ) AS evaluations

  FROM t_result_with_evaluations AS result
),

t_latest_biorxiv_medrxiv_api_response_version_by_doi AS (
  SELECT
    doi,
    preprint_url
  FROM (
    SELECT
      response.*,
      ROW_NUMBER() OVER(
        PARTITION BY response.doi
        ORDER BY response.version DESC, response.imported_timestamp DESC
      ) AS rn
    FROM `elife-data-pipeline.prod.mv_latest_biorxiv_medrxiv_api_response` AS response
  )
  WHERE rn = 1
),

t_result_with_preprint_url_and_has_evaluations AS (
  SELECT
    result.*,
    CONCAT('https://doi.org/', result.preprint_doi) AS preprint_doi_url,

    COALESCE(
      result.evaluations[SAFE_OFFSET(0)].uri,
      result.ejp_validated_preprint_url,
      latest_biorxiv_medrxiv_version.preprint_url
    ) AS preprint_url,

    CASE
      WHEN result.evaluations[SAFE_OFFSET(0)].uri IS NOT NULL THEN 'evaluations'
      WHEN result.ejp_validated_preprint_url IS NOT NULL THEN 'ejp_preprint_url'
      WHEN latest_biorxiv_medrxiv_version.preprint_url IS NOT NULL THEN 'latest_biorxiv_medrxiv_version'
    END AS preprint_url_source,

    (ARRAY_LENGTH(result.evaluations) > 0) AS has_evaluations,

  FROM t_result_with_sorted_evaluations AS result
  LEFT JOIN t_latest_biorxiv_medrxiv_api_response_version_by_doi AS latest_biorxiv_medrxiv_version
    ON latest_biorxiv_medrxiv_version.doi = result.preprint_doi
),

t_result_with_preprint_version AS (
  SELECT
    * EXCEPT(elife_doi),

    CASE 
      WHEN elife_doi IS NULL
        THEN CONCAT('10.7554/eLife.',manuscript_id)
      ELSE 
        elife_doi
    END AS elife_doi,
     
    CASE 
      WHEN preprint_url LIKE '%10.1101/%'
        THEN REGEXP_EXTRACT(preprint_url, r'10\.\d{3,}.*v([1-9])')
      WHEN preprint_url LIKE '%researchsquare.com/article/rs-%' OR preprint_url LIKE '%arxiv.org/abs/%'
        THEN REGEXP_EXTRACT(preprint_url, r'v(\d+)$')
      WHEN REGEXP_CONTAINS(preprint_doi_url, r'(.*v\d+)$')
        THEN REGEXP_EXTRACT(preprint_doi_url, r'v(\d+)$')
      WHEN REGEXP_CONTAINS(preprint_doi_url, r'osf')
        THEN result.evaluations[SAFE_OFFSET(0)].source_doi_version
      ELSE NULL
    END AS preprint_version,
    CASE 
      WHEN preprint_doi LIKE '%/rs%rs-%'
        THEN REGEXP_EXTRACT(preprint_doi, r'(.+)\/\w+') 
      ELSE preprint_doi
    END AS preprint_doi_without_version,
  FROM t_result_with_preprint_url_and_has_evaluations AS result
),

t_latest_tdm_path_by_doi_and_version AS (
  SELECT 
    * EXCEPT(rn) 
  FROM (
    SELECT
      ROW_NUMBER() OVER (
        PARTITION BY t_results.tdm_doi, t_results.ms_version
        ORDER BY imported_timestamp DESC
      ) AS rn,
      t_results.tdm_doi,
      t_results.tdm_path,
      t_results.ms_version AS tdm_ms_version,
    FROM `elife-data-pipeline.prod.biorxiv_medrxiv_meca_path_metadata`
    LEFT JOIN UNNEST(results) AS t_results
  )
  WHERE rn=1
),

t_preprint_published_at_date_and_tdm_path AS (
  SELECT 
    result.manuscript_id,
    result.long_manuscript_identifier,
    biorxiv_medrxiv_api_response.date AS preprint_published_at_date,
    CASE 
      WHEN result.preprint_doi LIKE '10.1101/%'
        THEN tdm.tdm_path 
      WHEN result.preprint_doi LIKE '10.21203/rs%' OR result.preprint_doi LIKE '%arXiv%'
        THEN CONCAT(
          's3://prod-elife-epp-meca/',
          result.preprint_doi_without_version,
          '-v',
          result.preprint_version,
          '-meca.zip'
        )
      ELSE NULL
    END AS tdm_path
  FROM t_result_with_preprint_version AS result
  LEFT JOIN `elife-data-pipeline.prod.mv_latest_biorxiv_medrxiv_api_response` AS biorxiv_medrxiv_api_response
    ON biorxiv_medrxiv_api_response.doi = result.preprint_doi
    AND CAST(biorxiv_medrxiv_api_response.version AS STRING) = result.preprint_version
  LEFT JOIN t_latest_tdm_path_by_doi_and_version AS tdm
    ON tdm.tdm_doi = result.preprint_doi
    AND CAST(tdm.tdm_ms_version AS STRING) = result.preprint_version
),

t_result_with_sorted_manuscript_versions_array AS (
  SELECT
    result.manuscript_id,
    result.is_reviewed_preprint_type,
    result.elife_doi,
    ARRAY_AGG(
      STRUCT(
        result.long_manuscript_identifier,
        result.position_in_overall_stage,
        result.is_or_was_under_review,
        result.qc_complete_timestamp,
        result.under_review_timestamp,
        result.has_evaluations,
        result.manuscript_title,
        result.preprint_url,
        CAST(result.position_in_overall_stage AS STRING) AS elife_doi_version_str,
        result.preprint_url_source,
        result.preprint_doi,
        result.preprint_version,
        result.preprint_doi_source,
        result.preprint_doi_url,
        preprint.preprint_published_at_date,
        preprint.tdm_path,
        result.editor_details,
        result.senior_editor_details,
        result.author_names_csv,
        result.evaluations
      )
    ORDER BY result.position_in_overall_stage
    ) AS manuscript_versions 
  FROM t_result_with_preprint_version AS result
  LEFT JOIN t_preprint_published_at_date_and_tdm_path AS preprint
    ON result.long_manuscript_identifier = preprint.long_manuscript_identifier
  GROUP BY result.manuscript_id, result.is_reviewed_preprint_type, result.elife_doi
),

t_latest_manuscript_license AS (
  SELECT 
    * EXCEPT(rn),
    CASE
      WHEN license_id = 1 THEN 'http://creativecommons.org/licenses/by/4.0/'
      WHEN license_id = 2 THEN 'https://creativecommons.org/publicdomain/zero/1.0/'
      ELSE NULL 
    END AS license_url
  FROM (
    SELECT
      *, 
      ROW_NUMBER() OVER(
        PARTITION BY manuscript_id
        ORDER BY imported_timestamp DESC
      ) AS rn
    FROM `elife-data-pipeline.prod.manuscript_license`
  )
  WHERE rn = 1
)

SELECT
  result.*,
  PARSE_JSON(ARRAY_TO_STRING(
    [
      '{',
      '  "id": "https://elifesciences.org/",',
      '  "name": "eLife",',
      '  "logo": "https://sciety.org/static/groups/elife--b560187e-f2fb-4ff9-a861-a204f3fc0fb0.png",',
      '  "homepage": "https://elifesciences.org/",',
      '  "account": {',
      '    "id": "https://sciety.org/groups/elife",',
      '    "service": "https://sciety.org"',
      '  }',
      '}'
    ],
    '\n'
  )) AS publisher_json,
  license.license_url AS license,
  license.license_timestamp,
FROM t_result_with_sorted_manuscript_versions_array AS result
LEFT JOIN t_latest_manuscript_license AS license
  ON result.manuscript_id = license.manuscript_id
