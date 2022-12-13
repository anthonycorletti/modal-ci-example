#!/bin/sh -e

# TODO: automatically invoke this when the api starts
alembic upgrade head
