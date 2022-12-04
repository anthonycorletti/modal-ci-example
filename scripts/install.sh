#!/bin/sh -e

pip install --upgrade pip
pip install --no-cache-dir '.[dev,test,doc]'
pre-commit install
