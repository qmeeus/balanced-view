#!/bin/sh

if [ -z "$PORT" ]; then
    PORT=8080;
fi

echo "Launch api on localhost"
FLASK_APP=api/api.py; export FLASK_APP
flask run --host=127.0.0.1 --port 5000 &

perl -pi -e "s#API_URL=.*#API_URL=http://127.0.0.1:5000#g" ui/.env

echo "Launch ui as main interface"
FLASK_APP=ui; export FLASK_APP
flask run --host=0.0.0.0 --port $PORT
