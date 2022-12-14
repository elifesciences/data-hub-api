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
    REGEXP_EXTRACT(biorxiv_url, r'10\.\d{3,}.*v([1-9])') preprint_version,
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
    * EXCEPT(rn)
  FROM (
    SELECT
      t_preprint_doi_and_url_by_long_manuscript_identifier.*,
      Version.Manuscript_ID AS manuscript_id,
      ROW_NUMBER() OVER(
        PARTITION BY Version.Manuscript_ID
        ORDER BY t_preprint_doi_and_url_by_long_manuscript_identifier.imported_timestamp DESC
      ) AS rn
    FROM t_preprint_doi_and_url_by_long_manuscript_identifier
    JOIN `elife-data-pipeline.prod.mv_Editorial_Manuscript_Version` AS Version
      ON Version.Long_Manuscript_Identifier = t_preprint_doi_and_url_by_long_manuscript_identifier.long_manuscript_identifier
  )
  WHERE rn = 1
)

SELECT
  Version.Manuscript_ID AS manuscript_id,
  Version.Long_Manuscript_Identifier AS long_manuscript_identifier,
  Version.QC_Complete_Timestamp AS qc_complete_timestamp,
  preprint_doi_and_url.preprint_doi,
  preprint_doi_and_url.preprint_version,
  preprint_doi_and_url.preprint_url
FROM `elife-data-pipeline.prod.mv_Editorial_Manuscript_Version` AS Version
JOIN t_preprint_doi_and_url_by_manuscript_id AS preprint_doi_and_url
  ON preprint_doi_and_url.manuscript_id = Version.Manuscript_ID
WHERE
  Version.Long_Manuscript_Identifier LIKE '%-RP-%'
  AND Version.Overall_Stage = 'Full Submission'
  AND Version.Position_In_Overall_Stage = 1
