#!/bin/bash

set -e

! [ $1 ] && echo "Missing argument" && exit 1

source config.sh
LOGDIR=$LOGDIR/build
CONTAINER=$1
LOGFILE=$LOGDIR/$CONTAINER.log
TAG=$REPO/$APP:$CONTAINER
CONTEXT="$(get_context $CONTAINER)"

mkdir -p $LOGDIR

case $CONTAINER in
  es)
    CONTEXT=$PROJECT_ROOT/elasticsearch ;;
  vis)
    CONTEXT=$PROJECT_ROOT/kibana ;;
  *) : ;;
esac

COMMAND="podman build -t $TAG $CONTEXT"
echo $COMMAND
bash -c "$COMMAND" > $LOGFILE 2>&1 && echo "Container $TAG is built!"
