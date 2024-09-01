# -*- coding: utf-8 -*-
from starlette.middleware import Middleware

from .logger_middleware import LoggingMiddleware


middlewares = [
    Middleware(LoggingMiddleware)
]
