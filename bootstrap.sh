#!/bin/bash

APP=balancedview
API_PORT=5000
UI_PORT=8080
IMAGE_REPO=docker.io/qmeeus
API_TAG=$IMAGE_REPO/$APP:api
UI_TAG=$IMAGE_REPO/$APP:ui

function exit_on_error {
    echo "Error with pod" $1 ". Trying to delete..."
    podman pod rm -f $1
    exit 1
}

if [ "$(podman pod ps | grep $APP | wc -l)" != "0" ] ; then
    echo "Pod $APP is already running. Re-create it? y/N"
    read input
    case $input in
        y|Y) echo "Deleting pod $APP" && podman pod rm -f $APP ;;
        *) echo "Leaving build process" && exit 0 ;;
    esac
fi

if [[ $(podman images | grep $APP | wc -l) < 2 ]]; then
    printf "No local image found. Options: (default 1)"
    printf "\t(1) Build locally"
    printf "\t(2) Download from $IMAGE_REPO"
    read input
    case $input in
	2)
	    echo "Pull images from online repository"
	    podman pull $API_TAG || exit 1
	    podman pull $UI_TAG || exit 1
	    ;;
	*)
	    echo "Build $API_TAG" && cd api && podman build -t $API_TAG . || exit 1
	    echo "Build $UI_TAG" && cd ../ui && podman build -t $UI_TAG . || exit 1
	    ;;
    esac
fi

echo "Create pod with name $APP"
podman pod create --name $APP -p $API_PORT -p $UI_PORT || exit_on_error $APP

echo "Create api service on port $API_PORT with name $APP-api"

podman run -d \
    --name $APP-api \
    --pod $APP \
    -v $(pwd)/api:/api \
    -v $(pwd)/data:/var/lib/sqlite \
    $API_TAG || exit_on_error $APP

podman exec -it $APP-api bash init_db.sh

echo "Create ui service on port $UI_PORT with name $APP-ui"
podman run -d --name $APP-ui --pod $APP $UI_TAG || exit_on_error $APP

podman ps
