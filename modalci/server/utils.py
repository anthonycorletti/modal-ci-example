import json
from typing import Callable, Union
from uuid import uuid4

from fastapi import Request, Response
from fastapi.routing import APIRoute

from modalci._types import (
    JsonResponseLoggerMessage,
    RequestLoggerMessage,
    ResponseLoggerMessage,
)
from modalci.server.log import log


class _APIRoute(APIRoute):
    """_APIRoute.

    _APIRoute is a custom APIRoute class that adds a background task to the
    response to log request and response data.
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def _log(
            req: RequestLoggerMessage,
            res: Union[JsonResponseLoggerMessage, ResponseLoggerMessage],
        ) -> None:
            id = {"id": str(uuid4()).replace("-", "")}
            log.info({**json.loads(req.json()), **id})
            log.info({**json.loads(res.json()), **id})

        async def custom_route_handler(request: Request) -> Response:
            req = RequestLoggerMessage(**request.__dict__)
            response = await original_route_handler(request)
            # if the response headers contain a content-type of application/json
            # then log the response body
            res: Union[JsonResponseLoggerMessage, ResponseLoggerMessage]
            if response.headers.get("content-type") == "application/json":
                res = JsonResponseLoggerMessage(**response.__dict__)
            else:
                res = ResponseLoggerMessage(**response.__dict__)
            await _log(req=req, res=res)
            return response

        return custom_route_handler
