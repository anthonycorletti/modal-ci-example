#!/bin/sh -ex

mypy modalci tests
black modalci tests --check
ruff modalci tests scripts
