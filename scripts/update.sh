#!/bin/bash

set -e

source config.sh

! [ $1 ] && echo "Missing argument" && exit 1

CONTAINER=$1
TAG=$REPO/$APP:$CONTAINER

if ! [ "$(podman login --get-login $REGISTRY ])" = "$REGISTRY_USER" ]; then
    podman login -u $REGISTRY_USER $REGISTRY
fi

podman pull $TAG
echo "Image $TAG was downloaded!"
