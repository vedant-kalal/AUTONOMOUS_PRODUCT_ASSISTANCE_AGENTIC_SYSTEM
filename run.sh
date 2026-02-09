#!/bin/bash
echo "Starting Postgres..."
docker-compose up -d

echo "Waiting for DB..."
sleep 5

echo "Starting Streamlit App..."
streamlit run app/main.py
