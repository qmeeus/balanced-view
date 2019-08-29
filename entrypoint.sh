#!/bin/sh

if [ -z "$PORT" ]; then
    PORT=8080;
fi

echo "Starting API server"
# perl -pi -e "s#API_URL=.*#API_URL=http://127.0.0.1:5000#g" ui/.env
gunicorn -D -w 2 --bind=127.0.0.1:5000 api.wsgi

echo "Performing database operations"
cd api 
./init_db.sh
cd ..

echo "Starting web interface"
gunicorn -w 3 --bind=0.0.0.0:$PORT ui.wsgi
