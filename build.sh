#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set FLASK_APP so that `flask db upgrade` can find the app factory
export FLASK_APP=run.py

# Apply database migrations
flask db upgrade