#!/bin/sh

. ./.env

if [ -z "$FLASK_RUN_PORT" ]; then
    FLASK_RUN_PORT=5000;
fi

python_path=$(which python)

echo "SHELL=/bin/bash
BASH_ENV=/api/.env
LC_ALL=C.UTF-8
LANG=C.UTF-8" > /tmp/scheduler.txt

for proxy in $(env | grep proxy); do
    echo $proxy >> /tmp/scheduler.txt
done

echo "@reboot sleep 60 && cd / && $python_path -m api.data_provider >> /var/log/cron.log 2>&1
0 6,12,18 * * * cd / && $python_path -m api.data_provider >> /var/log/cron.log 2>&1
# This extra line makes it a valid cron" >> /tmp/scheduler.txt

crontab /tmp/scheduler.txt  

printf "Start cron... " 
bash -c cron
printf "$(service cron status)\n"

echo "Starting API server"
gunicorn --chdir .. -w3 -k gevent --timeout 120 --bind=0.0.0.0:5000 api.wsgi
