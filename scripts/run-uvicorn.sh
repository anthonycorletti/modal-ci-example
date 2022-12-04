#!/bin/sh -e

uvicorn hudson.server.main:app ${@}
