import asyncio
import datetime
import json
import logging
import socket
from logging.handlers import QueueHandler
from queue import SimpleQueue
from typing import Any, List
from uuid import UUID

from hudson._env import env


class LogEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, bytes):
            return obj.decode("utf-8")
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, (set, frozenset)):
            return tuple(obj)
        elif isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        return super().default(obj)


class StructuredMessage:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    def __str__(self) -> str:
        return LogEncoder().encode(self.kwargs)


class OnelineFormatter(logging.Formatter):
    def formatException(self, exc_info: Any) -> str:
        result = super().formatException(exc_info)
        return repr(result)

    def format(self, record: logging.LogRecord) -> str:
        result = super().format(record)
        if record.exc_text:
            result = result.replace("\n", "")
        result_dict = record.__dict__
        result_dict["host"] = socket.gethostname()
        return str(StructuredMessage(**result_dict))


class StructuredLogger:
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def create_logger() -> logging.Logger:
        logger = logging.getLogger(__name__)
        log_handler = logging.StreamHandler()
        formatter = OnelineFormatter(datefmt=StructuredLogger.DATE_FORMAT)
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
        logger.setLevel(env.LOG_LEVEL.upper())
        return logger


class LocalQueueHandler(QueueHandler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        try:
            self.enqueue(record)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.handleError(record)


def setup_logging_queue() -> None:
    """Move log handlers to a separate thread.

    Replace handlers on the root logger with a LocalQueueHandler,
    and start a logging.QueueListener holding the original
    handlers.

    https://www.zopatista.com/python/2019/05/11/asyncio-logging/
    """
    root = logging.getLogger()
    queue: SimpleQueue = SimpleQueue()
    handlers: List[logging.Handler] = []
    handler = LocalQueueHandler(queue)

    root.addHandler(handler)
    for h in root.handlers[:]:
        if h is not handler:  # pragma: no cover
            root.removeHandler(h)
            handlers.append(h)

    listener = logging.handlers.QueueListener(
        queue, *handlers, respect_handler_level=True
    )
    listener.start()


log = StructuredLogger.create_logger()
setup_logging_queue()
