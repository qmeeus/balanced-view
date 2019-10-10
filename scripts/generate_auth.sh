#!/bin/bash

set -e

source config.sh

CONTAINER=$APP-es
AUTH_FILE=$PROJECT_ROOT/.auth

echo "Generate passwords for elasticsearch"
! [[ "$(is_running $CONTAINER )" -gt 0 ]] && echo "$CONTAINER not running" && exit 1
[ -f $AUTH_FILE ] && echo "Authentication file exists" && exit 0

podman exec $CONTAINER bin/elasticsearch-setup-passwords auto --batch > $AUTH_FILE
echo "Authentication file is created!"

