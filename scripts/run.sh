#!/bin/bash

set -e

source config.sh

! [ $1 ] && echo "Missing argument" && exit 1
! [ -f $PROJECT_ROOT/.auth ] && echo "Credentials not available" && exit 1

CONTAINER=$1
TAG=$REPO/$APP:$CONTAINER

ES_USER=elastic
EXPR="(?<=PASSWORD\s$ES_USER\s=\s)\w+"
ES_PSW="$(grep -oP $EXPR $PROJECT_ROOT/.auth)"

OPTIONS="-d --rm --name $APP-$CONTAINER --pod $APP"
case $CONTAINER in
  es)
    DATA_DIR=$PROJECT_ROOT/data/elasticsearch
    [ -d $DATA_DIR ] || bash -c "mkdir $DATA_DIR && chmod 777 $DATA_DIR"
    OPTIONS="$OPTIONS -v $DATA_DIR:/usr/share/elasticsearch/data"
    ;;
  vis|api)
    OPTIONS="$OPTIONS -e 'ELASTICSEARCH_USERNAME=$ES_USER'"
    OPTIONS="$OPTIONS -e 'ELASTICSEARCH_PASSWORD=$ES_PSW'"
    ;;
  *) : ;;
esac

podman run $OPTIONS $TAG
echo "Container $APP-$CONTAINER is started"
