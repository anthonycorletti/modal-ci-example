#!/bin/sh -ex

black hudson tests docs_src scripts
ruff hudson tests docs_src scripts --fix
