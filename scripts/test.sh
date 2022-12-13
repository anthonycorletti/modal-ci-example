#!/bin/sh -ex

alembic upgrade head

pytest --cov=hudson --cov=tests --cov=docs_src --cov-report=term-missing --cov-report=xml -o console_output_style=progress --disable-warnings --cov-fail-under=100 ${@}
