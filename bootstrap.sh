#!/bin/bash

APP=balancedview
API_PORT=5000
UI_PORT=8080
IMAGE_REPO=docker.io/qmeeus

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

# if [ -z "$PODMAN_USERNS" ]; then
#     PODMAN_USERNS=keep-id; export PODMAN_USERNS
# fi

echo "Pull images from online repository"
podman pull $IMAGE_REPO/$APP:api
podman pull $IMAGE_REPO/$APP:ui

echo "Create pod with name $APP"
podman pod create --name $APP -p $API_PORT -p $UI_PORT || exit_on_error $APP

echo "Create api service on port $API_PORT with name $APP-api"

podman run -d \
    --name $APP-api \
    --pod $APP \
    -v $(pwd)/api:/api \
    -v $(pwd)/data:/var/lib/sqlite \
    $IMAGE_REPO/$APP:api || exit_on_error $APP

echo "Initialise the database"
podman exec $APP-api flask db init || exit 1
sleep 1

echo "Compute the migrations"
podman exec $APP-api flask db migrate || exit 1
sleep 1

echo "Apply the migrations"
podman exec $APP-api flask db upgrade || exit 1

echo "Create ui service on port $UI_PORT with name $APP-ui"
podman run -d --name $APP-ui --pod $APP $IMAGE_REPO/$APP:ui || exit_on_error $APP

podman ps
