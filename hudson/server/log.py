import structlog


def _define_structlog() -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
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
        wrapper_class=structlog.stdlib.AsyncBoundLogger,
        cache_logger_on_first_use=True,
    )


def _set_log_level(logger: structlog.stdlib.AsyncBoundLogger) -> None:
    """Set the parent logger level.

    Args:
        logger (structlog.stdlib.AsyncBoundLogger): The logger.
    """
    import logging

    from hudson._env import env

    level_name = logging.getLevelName(env.LOG_LEVEL.upper())

    logging.basicConfig(level=level_name, format="%(message)s")

    logger.setLevel(level_name)
    logger.parent.setLevel(level_name)
    assert logger.level == logger.parent.level


_define_structlog()
# _set_parent_log_level(logger=structlog.get_logger())
# log = structlog.wrap_logger(
#     logger=structlog.get_logger(), wrapper_class=structlog.stdlib.AsyncBoundLogger
# )
log = structlog.get_logger()
