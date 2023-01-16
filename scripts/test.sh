#!/bin/sh -e

pytest --cov=modalci --cov=tests --cov-report=term-missing --cov-report=xml --disable-warnings --cov-fail-under=100 --asyncio-mode=auto ${@}
