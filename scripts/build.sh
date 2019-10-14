#!/bin/bash

set -e

! [ $1 ] && echo "Missing argument" && exit 1

source config.sh

CONTAINER=$1
TAG=$REPO/$APP:$CONTAINER
CONTEXT=$PROJECT_ROOT/$CONTAINER


case $CONTAINER in
  es)
    CONTEXT=$PROJECT_ROOT/elasticsearch ;;
  vis)
    CONTEXT=$PROJECT_ROOT/kibana ;;
  *) : ;;
esac

COMMAND="podman build -t $TAG $CONTEXT"
echo $COMMAND
bash -c "$COMMAND" && echo "Container $TAG is built!"
