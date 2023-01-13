WITH t_preprint_server_dois AS (
  SELECT
    biorxiv_url,
    ejp_elife_tracking_number, 
    final_decision_date,
    imported_timestamp,
    PARSE_DATE("%B %d, %Y", TRIM(date_generated_info, '"Generated on ')) AS date_generated
  FROM `elife-data-pipeline.prod.preprint_server_dois`
  WHERE
    imported_timestamp = (  -- Note: this assumes that the last imported file is the most recent data
      SELECT MAX(imported_timestamp)
      FROM `elife-data-pipeline.prod.preprint_server_dois`
    )
    AND biorxiv_url LIKE "%http%10.1101%"
),

t_preprint_doi_and_url_by_long_manuscript_identifier AS (
  SELECT 
    COALESCE(
      REGEXP_EXTRACT(biorxiv_url, r'(10\.\d{3,}[^v]*)v?'),
      CONCAT('10.1101/', REGEXP_EXTRACT(biorxiv_url, r'https://www.biorxiv.org/content/early/\d{4}/\d{2}/\d{2}/(\d{6,})'))
    ) AS preprint_doi,
    biorxiv_url AS preprint_url,
    ejp_elife_tracking_number AS long_manuscript_identifier,
    imported_timestamp
  FROM (
    SELECT 
      biorxiv_url, 
      ejp_elife_tracking_number,
      imported_timestamp,
      ROW_NUMBER() OVER(
        PARTITION BY ejp_elife_tracking_number
        ORDER BY preprint_doi.imported_timestamp DESC
      ) AS rn
    FROM t_preprint_server_dois AS preprint_doi 
  )
  WHERE rn = 1
),

t_preprint_doi_and_url_by_manuscript_id AS (
  SELECT
    Version.Manuscript_ID AS manuscript_id,
    preprint_doi_url.*
  FROM t_preprint_doi_and_url_by_long_manuscript_identifier AS preprint_doi_url
  JOIN `elife-data-pipeline.prod.mv_Editorial_Last_Manuscript_Version` AS Version
    ON Version.Long_Manuscript_Identifier = preprint_doi_url.long_manuscript_identifier
),

t_latest_biorxiv_medrxiv_api_response AS (
  -- move to view
  SELECT
    * EXCEPT(rn)
  FROM (
    SELECT
      response.* EXCEPT(title),
      response.title AS title_with_markup,
      REGEXP_REPLACE(response.title, r"<[^>]*>", "") AS title_without_markup,

      CONCAT(
        'https://www.',
        response.server,
        '.org/content/',
        response.doi,
        'v',
        response.version
      ) AS preprint_url,

      ROW_NUMBER() OVER(
        PARTITION BY response.doi, response.version
        ORDER BY response.imported_timestamp DESC
      ) AS rn
    FROM `elife-data-pipeline.prod.biorxiv_medrxiv_api_response` AS response
  )
  WHERE rn = 1
),

t_latest_biorxiv_medrxiv_api_response_version_by_doi AS (
  SELECT
    * EXCEPT(rn)
  FROM (
    SELECT
      response.*,
      ROW_NUMBER() OVER(
        PARTITION BY response.doi
        ORDER BY response.version DESC, response.imported_timestamp DESC
      ) AS rn
    FROM t_latest_biorxiv_medrxiv_api_response AS response
  )
  WHERE rn = 1
),

t_biorxiv_medrxiv_response_by_normalized_title AS (
  SELECT
    * EXCEPT(rn)
  FROM (
    SELECT
      REGEXP_REPLACE(LOWER(response.title_without_markup), r'[^a-z]', '') AS normalized_title,
      response.*,
      ROW_NUMBER() OVER(
        PARTITION BY REGEXP_REPLACE(LOWER(response.title_without_markup), r'[^a-z]', '')
        ORDER BY response.imported_timestamp ASC
      ) AS rn
    FROM t_latest_biorxiv_medrxiv_api_response AS response
  )
  WHERE rn = 1
),

t_hypothesis_annotation_with_doi AS (
  SELECT
    *,
    REGEXP_EXTRACT(annotation.uri, r'(10\.\d{3,}[^v]*)v?') AS source_doi,
    REGEXP_EXTRACT(annotation.uri, r'10\.\d{3,}.*v([1-9])') AS source_version
  FROM `elife-data-pipeline.de_proto.v_hypothesis_annotation` AS annotation
  WHERE annotation.group = 'q5X6RWJ6'
),

t_result AS (
  SELECT
    Version.Manuscript_ID AS manuscript_id,
    Version.Long_Manuscript_Identifier AS long_manuscript_identifier,
    Version.QC_Complete_Timestamp AS qc_complete_timestamp,
  
    COALESCE(preprint_doi_and_url.preprint_doi, biorxiv_medrxiv_response.doi) AS preprint_doi,

    CASE
      WHEN preprint_doi_and_url.preprint_doi IS NOT NULL THEN 'ejp_preprint_doi'
      WHEN biorxiv_medrxiv_response.doi IS NOT NULL THEN 'biorxiv_medrxiv_title_match'
    END AS preprint_doi_source,

    IF(preprint_doi_and_url.preprint_url LIKE '%doi.org/%', NULL, preprint_doi_and_url.preprint_url) AS ejp_validated_preprint_url,
    Version.Manuscript_Title AS manuscript_title,
    Version.DOI AS elife_doi,
    (Version.Long_Manuscript_Identifier LIKE '%-RP-%') AS is_reviewed_preprint_type,

    ARRAY(
      SELECT AS STRUCT
        annotation.id AS hypothesis_id,
        annotation.created AS annotation_created_timestamp,
        annotation.uri,
        annotation.tags,
        annotation.normalized_tags,
        annotation.source_doi,
        annotation.source_version
      FROM t_hypothesis_annotation_with_doi AS annotation
      WHERE annotation.source_doi = COALESCE(preprint_doi_and_url.preprint_doi, biorxiv_medrxiv_response.doi)
    ) AS evaluations,

    ARRAY(SELECT Name FROM UNNEST(Version.Reviewing_Editors)) AS editor_names,
    ARRAY(SELECT Name FROM UNNEST(Version.Senior_Editors)) AS senior_editor_names,

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
    )) AS publisher_json

  FROM `elife-data-pipeline.prod.mv_Editorial_Manuscript_Version` AS Version
  LEFT JOIN t_preprint_doi_and_url_by_manuscript_id AS preprint_doi_and_url
    ON preprint_doi_and_url.manuscript_id = Version.Manuscript_ID
  LEFT JOIN t_biorxiv_medrxiv_response_by_normalized_title AS biorxiv_medrxiv_response
    ON biorxiv_medrxiv_response.normalized_title = REGEXP_REPLACE(LOWER(Version.Manuscript_Title), r'[^a-z]', '')
  WHERE
    Version.Overall_Stage = 'Full Submission'
    AND Version.Position_In_Overall_Stage = 1
    AND COALESCE(preprint_doi_and_url.preprint_doi, biorxiv_medrxiv_response.doi) IS NOT NULL
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

    (ARRAY_LENGTH(result.evaluations) > 0) AS has_evaluations

  FROM t_result AS result
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

t_result_with_tdm_path AS (
  SELECT
    result.*,
    tdm.tdm_path
  FROM t_result_with_preprint_version AS result
  LEFT JOIN t_latest_tdm_path_by_doi_and_version AS tdm
    ON tdm.tdm_doi = result.preprint_doi
    AND CAST(tdm.tdm_ms_version AS STRING) = result.preprint_version
)


SELECT
  *
FROM t_result_with_tdm_path
