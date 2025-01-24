#!/bin/sh

# Run the default command (from the Dockerfile) first
echo "Container has started and will create an award application HTML file."
echo '<html><body><h1>Award Application</h1><p>This is the award application page.</p></body></html>' > /app/award_application.html

# Run the Python app
echo "Starting the Python application..."
python app.py
exec "$@"