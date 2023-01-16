#!/bin/sh -ex

black modalci tests scripts
ruff modalci tests scripts --fix
