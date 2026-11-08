#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files with whitenoise
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Seed baseline relational data for workflow demo
python manage.py seed_demo_data

