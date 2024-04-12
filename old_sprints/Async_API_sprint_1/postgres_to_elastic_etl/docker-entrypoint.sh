#!/bin/bash
wait-for-it -p -s "${POSTGRES_HOST}:${POSTGRES_PORT}" -s "${ELASTIC_HOST}:${ELASTIC_PORT}" -t 60 -- python main.py
