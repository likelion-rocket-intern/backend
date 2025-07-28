#!/bin/bash

set -e
set -x


echo "Prestart script started..."

# First check if DB and Redis are ready
python app/backend_pre_start.py
echo "DB/Redis check finished."

# Then run migrations
# alembic upgrade head

# Finally initialize embeddings
# python app/backend_pre_embed.py

# Create initial data in DB
# python app/initial_data.py

# Note: Dramatiq workers should be started separately using:
# ./scripts/worker-start.sh

echo "Prestart script finished successfully!"
# Execute the command passed to docker run
exec "$@"
