#!/bin/bash

set -e

source config.sh

OPTIONS="--name $APP"

(( $(podman pod ps | grep $APP | wc -l) )) && echo "Pod $APP exists" && exit 1

for PORT in $EXTERNAL_PORTS; do
    OPTIONS="$OPTIONS -p $PORT"
done

podman pod create $OPTIONS
echo "Pod $APP created!"




