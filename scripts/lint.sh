#!/bin/sh -ex

mypy modalci tests docs_src
black modalci tests docs_src --check
ruff modalci tests docs_src scripts
