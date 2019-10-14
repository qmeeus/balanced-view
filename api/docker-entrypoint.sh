#!/bin/sh

#. ./.env

if [ -z "$FLASK_RUN_PORT" ]; then
    echo "FLASK_RUN_PORT undefined."
    exit 1
fi

python_path=$(which python)

cat <<EOF > /tmp/scheduler.txt
$(env | sed 's:HOME=.*:HOME=/api:')
SHELL=/bin/bash
@reboot sleep 60 && $python_path -m api.data_provider >> /var/log/cron.log 2>&1
0 6,12,18 * * * $python_path -m api.data_provider >> /var/log/cron.log 2>&1
# This extra line makes it a valid cron"
EOF

crontab /tmp/scheduler.txt

printf "Start cron... "
bash -c cron
printf "$(service cron status)\n"

echo "Starting API server"
gunicorn -w3 -k gevent --timeout 120 --bind=0.0.0.0:5000 api.wsgi
