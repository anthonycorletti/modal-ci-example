#!/bin/sh -ex

black hudson tests scripts
ruff hudson tests scripts --fix
