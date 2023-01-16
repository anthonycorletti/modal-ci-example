#!/bin/sh -e

pip install --upgrade pip
pip install -e '.[dev,test]'

pre-commit install
