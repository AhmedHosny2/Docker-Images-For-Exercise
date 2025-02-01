#!/bin/sh

  # Run the Python app
  echo "Starting the Python application..."
  python app.py
  exec "$@"