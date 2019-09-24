#!/bin/sh

echo "$(pwd)"

. ./.env

if [ -z "$FLASK_RUN_PORT" ]; then
    FLASK_RUN_PORT=5000;
fi

echo "Start cron"
bash -c cron
echo "$(service cron status)"

echo "Starting API server"
gunicorn --chdir .. -w3 -k gevent --bind=0.0.0.0:5000 api.wsgi
