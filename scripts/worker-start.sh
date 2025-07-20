#! /usr/bin/env bash

set -e
set -x

# Start Dramatiq workers
dramatiq app.worker.resume_analysis app.worker.__init__ --processes 1 --threads 4 