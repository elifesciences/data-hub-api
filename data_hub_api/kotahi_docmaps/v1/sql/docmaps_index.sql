WITH t_reviewed_preprints AS (
  SELECT 
    * EXCEPT(
      source_site_id,
      preprint_url_from_ejp,
      ejp_normalized_title,
      biorxiv_medrxiv_normalized_title)
  FROM `elife-data-pipeline.prod.v_manuscript_with_matching_preprint_server_doi`
  WHERE is_reviewed_preprint_type
    AND under_review_timestamp IS NOT NULL
    AND preprint_doi IS NOT NULL
    AND long_manuscript_identifier NOT LIKE '%-VOR-%'
    AND qc_complete_timestamp >= '2023-10-01'
),

t_latest_evaluation_emails AS(
  SELECT
    * EXCEPT(rn)
  FROM (
    SELECT 
      *,
      ROW_NUMBER() OVER (
        PARTITION BY email.email_id
        ORDER BY email.imported_timestamp DESC
      ) AS rn,
    FROM `elife-data-pipeline.prod.rp_reviews_and_elife_assessment_emails` AS email
    WHERE (
      converted_subject LIKE "Update from eLife:%"
      OR
      converted_subject LIKE "Reviews for your submission to eLife:%"
    )
  )
  WHERE rn=1
),

t_manuscript_version_with_rp_site_data AS (
  SELECT
    Version.long_manuscript_identifier
  FROM `elife-data-pipeline.prod.mv_Editorial_All_Manuscript_Version` AS Version
  WHERE Version.Is_Research_Content
    -- only include manuscripts that went through QC
    AND Version.QC_Complete_Timestamp IS NOT NULL
    AND COALESCE(Version.Decision, '') != 'Decline to Review'
    AND Is_Reviewed_Preprint_Type
),

t_latest_evaluation_emails_by_long_manuscript_identifier AS (
  SELECT 
    * 
  FROM (
    SELECT
      *,
      ROW_NUMBER() OVER (
        PARTITION BY email.long_manuscript_identifier
        ORDER BY email.create_dt DESC
      ) AS rn,
    FROM t_latest_evaluation_emails AS email
  )
  WHERE rn=1
),

t_emails_for_not_declined_to_review_manuscripts AS (
  SELECT
    email.*
  FROM t_latest_evaluation_emails_by_long_manuscript_identifier AS email
  INNER JOIN t_manuscript_version_with_rp_site_data AS version
    ON email.long_manuscript_identifier = version.long_manuscript_identifier
),

t_result_with_evaluation_emails AS (
  SELECT 
    reviewed_preprints.*,
    evaluation_emails.converted_body AS email_body,
    evaluation_emails.create_dt AS email_timestamp
  FROM t_reviewed_preprints AS reviewed_preprints
  LEFT JOIN t_emails_for_not_declined_to_review_manuscripts AS evaluation_emails
  ON evaluation_emails.long_manuscript_identifier = reviewed_preprints.long_manuscript_identifier
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

t_result_with_preprint_url_and_evaluation_emails AS (
  SELECT
    result.*,
    CONCAT('https://doi.org/', result.preprint_doi) AS preprint_doi_url,

    COALESCE(
      result.ejp_validated_preprint_url,
      latest_biorxiv_medrxiv_version.preprint_url
    ) AS preprint_url,

    CASE
      WHEN result.ejp_validated_preprint_url IS NOT NULL THEN 'ejp_preprint_url'
      WHEN latest_biorxiv_medrxiv_version.preprint_url IS NOT NULL THEN 'latest_biorxiv_medrxiv_version'
    END AS preprint_url_source,


  FROM t_result_with_evaluation_emails AS result
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

    CAST(result.position_in_overall_stage AS STRING) AS elife_doi_version_str,

    CASE
      WHEN manual_preprint_version IS NOT NULL
        THEN manual_preprint_version
      WHEN preprint_url LIKE '%10.1101/%v%'
        THEN REGEXP_EXTRACT(preprint_url, r'10\.\d{3,}.*v([1-9])')
      WHEN preprint_url LIKE '%researchsquare.com/article/rs-%v%' OR preprint_url LIKE '%arxiv.org/abs/%v%'
        THEN REGEXP_EXTRACT(preprint_url, r'v(\d+)$')
      WHEN REGEXP_CONTAINS(preprint_doi_url, r'(.*v\d+)$')
        THEN REGEXP_EXTRACT(preprint_doi_url, r'v(\d+)$')
      ELSE NULL
    END AS preprint_version,
    CASE 
      WHEN preprint_doi LIKE '%/rs%rs-%'
        THEN REGEXP_EXTRACT(preprint_doi, r'(.+)\/\w+') 
      ELSE preprint_doi
    END AS preprint_doi_without_version,
  FROM t_result_with_preprint_url_and_evaluation_emails AS result
),

t_manual_preprint_match_for_published_date AS (
  SELECT
    * EXCEPT(rn),
  FROM
  (
    SELECT 
      *,
      ROW_NUMBER() OVER(PARTITION BY long_manuscript_identifier ORDER BY imported_timestamp DESC) AS rn
    FROM `elife-data-pipeline.prod.unmatched_manuscripts`
    WHERE preprint_published_at_date IS NOT NULL 
      AND preprint_published_at_date != ''
  )
  WHERE rn = 1
),

t_europepmc_preprint_publication_date AS (
  SELECT
    response.doi,
    response.firstPublicationDate,
    REGEXP_EXTRACT(doi, r'v(\d+)$') AS doi_version,
  FROM `elife-data-pipeline.prod.v_latest_europepmc_preprint_servers_response`  AS response
  WHERE REGEXP_EXTRACT(doi, r'v(\d+)$') IS NOT NULL
),

t_preprint_published_at_date AS (
  SELECT 
    result.manuscript_id,
    result.long_manuscript_identifier,
    COALESCE(
      biorxiv_medrxiv_api_response.date,
      CAST(manual_preprint_published_date.preprint_published_at_date AS DATE),
      europepmc_pub_date.firstPublicationDate
    ) AS preprint_published_at_date,
  FROM t_result_with_preprint_version AS result
  LEFT JOIN `elife-data-pipeline.prod.mv_latest_biorxiv_medrxiv_api_response` AS biorxiv_medrxiv_api_response
    ON biorxiv_medrxiv_api_response.doi = result.preprint_doi
    AND CAST(biorxiv_medrxiv_api_response.version AS STRING) = result.preprint_version
  LEFT JOIN t_manual_preprint_match_for_published_date AS manual_preprint_published_date
    ON result.long_manuscript_identifier = manual_preprint_published_date.long_manuscript_identifier
  LEFT JOIN t_europepmc_preprint_publication_date AS europepmc_pub_date
    ON result.preprint_doi = europepmc_pub_date.doi
    AND result.preprint_version = europepmc_pub_date.doi_version
),

t_vor_publication_date AS (
  SELECT 
    article_id,
    vor_publication_date
  FROM `elife-data-pipeline.prod.v_elife_article_xml_data`
  WHERE is_latest_xml_version
  AND vor_publication_date IS NOT NULL
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
        TIMESTAMP(DATETIME(result.qc_complete_timestamp), 'US/Eastern') AS qc_complete_timestamp,
        TIMESTAMP(DATETIME(result.under_review_timestamp), 'US/Eastern') AS under_review_timestamp,
        result.manuscript_title,
        result.preprint_url,
        result.elife_doi_version_str,
        result.preprint_url_source,
        result.preprint_doi,
        result.preprint_version,
        result.preprint_doi_source,
        result.preprint_doi_url,
        preprint.preprint_published_at_date,
        result.editor_details,
        result.senior_editor_details,
        result.author_names_csv,
        result.email_body,
        result.email_timestamp
      )
    ORDER BY result.position_in_overall_stage
    ) AS manuscript_versions 
  FROM t_result_with_preprint_version AS result
  LEFT JOIN t_preprint_published_at_date AS preprint
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
