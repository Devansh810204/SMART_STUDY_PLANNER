#!/bin/bash
source venv/bin/activate
uvicorn app:app --reload --host $HOST --port $PORT
