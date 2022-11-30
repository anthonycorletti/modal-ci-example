#!/bin/sh -ex

mypy hudson tests
black hudson tests --check
ruff hudson tests scripts
