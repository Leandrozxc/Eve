#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files with whitenoise
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Seed baseline relational data for workflow and SQL JOIN demo
python manage.py seed_join_demo

