#!/bin/sh -ex

mypy hudson tests docs_src
black hudson tests docs_src --check
ruff hudson tests docs_src scripts
