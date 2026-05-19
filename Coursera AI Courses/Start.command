#!/bin/bash
cd "$(dirname "$0")/App"
echo "Starting Coursera AI Affiliate Toolkit..."
sleep 2 && open http://localhost:5050 &
python3 app.py
