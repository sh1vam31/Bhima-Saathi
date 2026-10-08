#!/bin/bash
# Start the mock services in the background on port 8100
uvicorn mock_services.main:app --host 0.0.0.0 --port 8100 &

# Start the main AI app on the port provided by Render (or default 10000)
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
