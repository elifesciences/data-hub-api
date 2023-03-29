WITH t_hypothesis_annotation_with_doi AS (
  SELECT
    * EXCEPT (id, created),
    REGEXP_EXTRACT(annotation.uri, r'(10\.\d{3,}[^v]*)v?') AS source_doi,
    REGEXP_EXTRACT(annotation.uri, r'10\.\d{3,}.*v([1-9])') AS source_doi_version,
    annotation.id AS hypothesis_id,
    annotation.created AS annotation_created_timestamp,
  FROM `elife-data-pipeline.de_proto.v_hypothesis_annotation` AS annotation
  WHERE annotation.group = 'q5X6RWJ6'
),

t_distinct_hypothesis_uri_doi_version AS(
  SELECT 
    DISTINCT
    uri,
    source_doi,
    source_doi_version
  FROM t_hypothesis_annotation_with_doi
),

t_distinct_hypothesis_uri_doi_version_with_elife_doi_version AS (
  SELECT
    *,
    ROW_NUMBER() OVER(
      PARTITION BY source_doi
      ORDER BY source_doi_version
    ) AS elife_doi_version
  FROM t_distinct_hypothesis_uri_doi_version
),

t_distinct_hypothesis_uri_id_and_timestamp AS(
  SELECT 
    uri,
    source_doi,
    source_doi_version,
    annotation_created_timestamp,
    hypothesis_id
  FROM t_hypothesis_annotation_with_doi
),

t_distinct_hypothesis_with_evaluation_suffix_number AS (
  SELECT
    *,
    ROW_NUMBER() OVER(
      PARTITION BY source_doi, source_doi_version
      ORDER BY annotation_created_timestamp, hypothesis_id
    ) AS evaluation_suffix_number
  FROM t_distinct_hypothesis_uri_id_and_timestamp
),

t_hypothesis_annotation_with_elife_doi_version AS (
  SELECT 
    CAST(elife_doi_version.elife_doi_version AS STRING) AS elife_doi_version_str,
    annotation.hypothesis_id,
    annotation.annotation_created_timestamp,
    annotation.uri,
    annotation.tags,
    annotation.normalized_tags,
    annotation.source_doi,
    annotation.source_doi_version,
    CONCAT('sa',CAST(t_evaluation_suffix.evaluation_suffix_number AS STRING)) AS evaluation_suffix
  FROM t_hypothesis_annotation_with_doi AS annotation
  INNER JOIN t_distinct_hypothesis_uri_doi_version_with_elife_doi_version AS elife_doi_version
    ON annotation.uri = elife_doi_version.uri
  INNER JOIN t_distinct_hypothesis_with_evaluation_suffix_number AS t_evaluation_suffix
    ON annotation.uri = t_evaluation_suffix.uri 
    AND annotation.hypothesis_id = t_evaluation_suffix.hypothesis_id
),

t_result_with_preprint_dois AS (
  SELECT 
    * EXCEPT(
      source_site_id,
      preprint_url_from_ejp,
      ejp_normalized_title,
      biorxiv_medrxiv_normalized_title)
  FROM `elife-data-pipeline.prod.v_manuscript_with_matching_preprint_server_doi`
  WHERE preprint_doi IS NOT NULL
),

t_result_with_evaluations AS (
  SELECT 
    *,
    ARRAY(
      SELECT AS STRUCT
        *
      FROM t_hypothesis_annotation_with_elife_doi_version AS annotation
      WHERE annotation.source_doi = t_result_with_preprint_dois.preprint_doi
    ) AS evaluations,
  FROM t_result_with_preprint_dois
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
    COALESCE(result.evaluations[SAFE_OFFSET(0)].elife_doi_version_str, '1') AS elife_doi_version_str,
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

    (ARRAY_LENGTH(result.evaluations) > 0) AS has_evaluations

  FROM t_result_with_sorted_evaluations AS result
  LEFT JOIN t_latest_biorxiv_medrxiv_api_response_version_by_doi AS latest_biorxiv_medrxiv_version
    ON latest_biorxiv_medrxiv_version.doi = result.preprint_doi
),

t_result_with_preprint_version AS (
  SELECT
    *,
    -- extract version from final preprint url to ensure url and version are consistent
    REGEXP_EXTRACT(preprint_url, r'10\.\d{3,}.*v([1-9])') AS preprint_version,
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

t_result_with_preprint_published_at_date_and_tdm_path AS (
  SELECT
    result.*,
    biorxiv_medrxiv_api_response.date AS preprint_published_at_date,
    tdm.tdm_path
  FROM t_result_with_preprint_version AS result
  LEFT JOIN `elife-data-pipeline.prod.mv_latest_biorxiv_medrxiv_api_response` AS biorxiv_medrxiv_api_response
    ON biorxiv_medrxiv_api_response.doi = result.preprint_doi
    AND CAST(biorxiv_medrxiv_api_response.version AS STRING) = result.preprint_version
  LEFT JOIN t_latest_tdm_path_by_doi_and_version AS tdm
    ON tdm.tdm_doi = result.preprint_doi
    AND CAST(tdm.tdm_ms_version AS STRING) = result.preprint_version
),

t_latest_manuscript_license AS (
  SELECT 
    * EXCEPT(rn)
  FROM (
    SELECT
      *, 
      ROW_NUMBER() OVER(
        PARTITION BY long_manuscript_identifier
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
  license.license_definition,
  license.license_timestamp,
FROM t_result_with_preprint_published_at_date_and_tdm_path AS result
LEFT JOIN t_latest_manuscript_license AS license
ON result.long_manuscript_identifier = license.long_manuscript_identifier
