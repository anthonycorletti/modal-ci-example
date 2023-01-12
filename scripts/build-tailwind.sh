#!/bin/sh -e

npx tailwindcss -i ./static/input.css -o ./static/output.css ${@} # --watch
