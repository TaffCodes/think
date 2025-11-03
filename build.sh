#!/usr/bin/env bash
# build.sh

# Exit on error
set -o errexit

# 1. Install dependencies
pip install -r requirements.txt

# 2. Collect all static files (for Whitenoise)
python manage.py collectstatic --no-input

# 3. Run database migrations
python manage.py migrate