from contextvars import ContextVar
import logging
import uuid


LOGGER = logging.getLogger(__name__)


request_id_context_var: ContextVar[str] = ContextVar('request_log_context')


class RequestLogFilter(logging.Filter):
    def filter(self, record):
        request_id = request_id_context_var.get('app')
        setattr(record, 'request_id', request_id)
        return True


def log_requests_middleware():
    async def log_requests(request, call_next):
        request_id = str(uuid.uuid4())
        user_agent = request.headers.get('user-agent', 'unknown')
        client_addr = (
            f"{request.client.host}:{request.client.port}"
            if request.client
            else 'unknown'
        )
        protocol = request.scope.get('http_version', 'unknown')
        method = request.method
        path = request.url.path

        request_id_context_var.set(request_id)

        LOGGER.info(
            '%s',
            f'Received request: {request_id} {client_addr} "{method} {path} HTTP/{protocol}"'
            f' "{user_agent}"'
        )

        response = await call_next(request)

        return response
    return log_requests
