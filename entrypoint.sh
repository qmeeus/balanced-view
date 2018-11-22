#!/bin/sh

if [ -z "$PORT" ]; then
    PORT=5000;
fi

flask run --host=0.0.0.0 --port $PORT;
