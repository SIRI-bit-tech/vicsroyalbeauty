#!/usr/bin/env bash
# Render build script: install dependencies and collect static files

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput 