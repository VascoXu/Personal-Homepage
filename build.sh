#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

npx tailwindcss -i ./static/styles/styles.css -o ./static/dist/css/tailwind.css
python build.py
