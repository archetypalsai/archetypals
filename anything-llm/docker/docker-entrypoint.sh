#!/bin/bash

# Check if STORAGE_DIR is set
if [ -z "$STORAGE_DIR" ]; then
    echo "================================================================"
    echo "⚠️  STORAGE_DIR environment variable is not set! Exiting... ⚠️"
    echo "================================================================"
    exit 1
fi

echo "================================================================"
echo "✅ STORAGE_DIR is set to: $STORAGE_DIR"
echo "Starting AnythingLLM server and collector processes..."
echo "================================================================"

# Start server process
{
  echo "Starting server..."
  cd /app/server/ || exit 1
  node index.js
} &

# Start collector process
{
  echo "Starting collector..."
  cd /app/collector/ || exit 1
  node index.js
} &

wait -n
exit $?
