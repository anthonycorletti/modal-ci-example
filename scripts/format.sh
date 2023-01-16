#!/bin/sh -ex

black modalci tests docs_src scripts
ruff modalci tests docs_src scripts --fix
