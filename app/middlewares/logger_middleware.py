# -*- coding: utf-8 -*-
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.logger import logger
from app.configs import settings


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[..., Response]):
        """Middleware to log the incoming requests to .log file"""
        # logging the request
        start_time = time.time()
        data = await request.body()
        try:
            data = request.query_params or data.decode("utf-8"),
        except UnicodeDecodeError:
            data = None

        logger.info(settings.req_logging_string.format(
            request.method,
            request.url.path,
        ))

        response = await call_next(request)

        # logging the response
        process_time = time.time() - start_time

        logger.info(settings.res_logging_string.format(
            response.status_code,
            process_time,
            request.url.path,
        ))
        return response
