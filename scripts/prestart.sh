#!/bin/bash

set -e
set -x

# First check if DB and Redis are ready
python app/backend_pre_start.py

# Then run migrations
alembic upgrade head

# Finally initialize embeddings
python app/backend_pre_embed.py

# Create initial data in DB
# python app/initial_data.py

# Note: Dramatiq workers should be started separately using:
# ./scripts/worker-start.sh

# Execute the command passed to docker run
exec "$@"
