import logging
from time import monotonic
from typing import Any, Iterable, Optional, Sequence

from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator
from google.cloud.bigquery_storage import BigQueryReadClient

LOGGER = logging.getLogger(__name__)


def get_bq_client(project_name: str) -> bigquery.Client:
    return bigquery.Client(project=project_name)


def get_bq_result_from_bq_query(
    project_name: str,
    query: str,
    query_parameters: Optional[Sequence[Any]] = tuple()
) -> RowIterator:
    client = get_bq_client(project_name=project_name)
    job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
    t0 = monotonic()
    query_job = client.query(query, job_config=job_config)
    bq_result = query_job.result()  # Waits for query to finish
    LOGGER.info('BQ query execution finished in %.3f seconds', monotonic() - t0)
    LOGGER.debug('bq_result: %r', bq_result)
    return bq_result


def iter_dict_from_bq_query(
    project_name: str,
    query: str,
    query_parameters: Optional[Sequence[Any]] = tuple()
) -> Iterable[dict]:
    bq_result = get_bq_result_from_bq_query(
        project_name=project_name,
        query=query,
        query_parameters=query_parameters
    )
    t0 = monotonic()
    bqstorage_client = BigQueryReadClient()
    with bqstorage_client:
        for batch in bq_result.to_arrow_iterable(bqstorage_client=bqstorage_client):
            LOGGER.debug('batch: %r', batch)
            yield from batch.to_pylist()
    LOGGER.info('BQ data transfer finished in %.3f seconds', monotonic() - t0)
