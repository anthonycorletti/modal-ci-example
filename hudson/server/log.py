import logging

import structlog

from hudson._env import env

logging.basicConfig(level=env.LOG_LEVEL.upper(), format="%(message)s")

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.MODULE,
                structlog.processors.CallsiteParameter.PATHNAME,
                structlog.processors.CallsiteParameter.PROCESS_NAME,
                structlog.processors.CallsiteParameter.PROCESS,
                structlog.processors.CallsiteParameter.THREAD,
                structlog.processors.CallsiteParameter.THREAD_NAME,
            ],
        ),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(sort_keys=True),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()
