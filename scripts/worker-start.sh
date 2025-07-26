#! /usr/bin/env bash

set -e
set -x

# Start Dramatiq workers
dramatiq app.worker --processes 1 --threads 2