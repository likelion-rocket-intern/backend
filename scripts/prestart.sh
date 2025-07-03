#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
# python app/initial_data.py

# Note: Dramatiq workers should be started separately using:
# ./scripts/worker-start.sh

# Execute the command passed to docker run
exec "$@"
