#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Run database initialization
python init_neon_db.py
