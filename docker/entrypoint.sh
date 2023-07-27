#!/bin/bash
set -e

python3 -u /app/bin/import.py
python3 -u /app/bin/server.py