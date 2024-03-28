#!/bin/bash

# Run Alembic upgrades
alembic upgrade head

# Initialize the database (if needed)
cd app/sql_app
python initial_data.py

# Add any other necessary initialization steps