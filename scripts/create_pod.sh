#!/bin/bash

set -e

source config.sh

OPTIONS="--name $APP"

(( $(podman pod ps | grep $APP | wc -l) )) && echo "Pod $APP exists" && exit 0

for PORT in $EXTERNAL_PORTS; do
    OPTIONS="$OPTIONS -p $PORT"
done

COMMAND="podman pod create $OPTIONS"
echo $COMMAND
bash -c "$COMMAND" && echo "Pod $APP created!"




