import logging
import uuid

LOGGER = logging.getLogger(__name__)


def log_requests_middleware():
    async def log_requests(request, call_next):
        request_id = str(uuid.uuid4())
        user_agent = request.headers.get("user-agent", "unknown")
        client_addr = (
            f"{request.client.host}:{request.client.port}"
            if request.client
            else "unknown"
        )
        protocol = request.scope.get("http_version", "unknown")
        method = request.method
        path = request.url.path

        request.state.request_id = request_id

        LOGGER.info(
            '%s',
            f'{request_id} START {client_addr} - - "{method} {path} HTTP/{protocol}" "{user_agent}"'
        )

        response = await call_next(request)

        LOGGER.info(
            '%s',
            f'{request_id} END {client_addr} - - "{method} {path} HTTP/{protocol}"'
            f' {response.status_code} "{user_agent}"'
        )

        return response
    return log_requests
