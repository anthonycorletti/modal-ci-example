import json
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute

from hudson._types import RequestLoggerMessage, ResponseLoggerMessage
from hudson.server.log import log


class _APIRoute(APIRoute):
    """_APIRoute.

    _APIRoute is a custom APIRoute class that adds a background task to the
    response to log request and response data.
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def _log(req: RequestLoggerMessage, res: ResponseLoggerMessage) -> None:
            log.debug({"req": json.loads(req.json())})
            log.debug({"res": json.loads(res.json())})

        async def custom_route_handler(request: Request) -> Response:
            req = RequestLoggerMessage(**request.__dict__)
            response = await original_route_handler(request)
            res = ResponseLoggerMessage(**response.__dict__)
            await _log(req=req, res=res)
            return response

        return custom_route_handler
