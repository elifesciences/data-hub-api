import logging
from typing import Iterable

from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator

LOGGER = logging.getLogger(__name__)


def get_bq_client(project_name: str) -> bigquery.Client:
    return bigquery.Client(project=project_name)


def get_bq_result_from_bq_query(
    project_name: str,
    query: str
) -> RowIterator:
    client = get_bq_client(project_name=project_name)
    query_job = client.query(query)  # Make an API request.
    bq_result = query_job.result()  # Waits for query to finish
    LOGGER.debug('bq_result: %r', bq_result)
    return bq_result


def iter_dict_from_bq_query(
    project_name: str,
    query: str
) -> Iterable[dict]:
    bq_result = get_bq_result_from_bq_query(project_name=project_name, query=query)
    for row in bq_result:
        LOGGER.debug('row: %r', row)
        yield dict(row.items())
