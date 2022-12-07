#!/bin/sh -e

pip install --upgrade pip
pip install -e '.[dev,test,doc]'

pre-commit install
