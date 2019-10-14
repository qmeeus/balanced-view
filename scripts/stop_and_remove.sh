#!/bin/bash

set -e

! [ $1 ] && echo "Missing argument" && exit 1
source config.sh

CONTAINER=$1

if (( $(is_running $APP-$1) )); then
  echo "Stop container $APP-$1"
  COMMAND="podman stop $APP-$1"
  echo $COMMAND
  bash -c "$COMMAND"
fi

if (( $(podman ps -a | grep $APP-$1 | wc -l) )); then
  echo "Remove container $APP-$1"
  COMMAND="podman rm $APP-$1"
  echo $COMMAND
  bash -c "$COMMAND"
fi

