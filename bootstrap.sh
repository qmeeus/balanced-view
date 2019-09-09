#!/bin/bash

APP=balancedview
API_PORT=5000
UI_PORT=9999
NGINX_PORT=8080
IMAGE_REPO=docker.io/qmeeus
DEFAULT_IMAGE=$IMAGE_REPO/$APP
IMAGES="nginx api ui"

function clean_exit {
    echo "An error occured, clean and exit..."
    podman ps -a | grep $APP | cut -d" " -f1 | xargs -I "{}" bash -c 'podman stop {} && podman rm {}'
    podman pod rm $APP
    exit 1
}

while (( "$#" )); do
  case "$1" in
    -u|--update)
      UPDATE=true
      shift 1
      ;;
    -r|--restart)
      RESTART=true
      #if ! [ "$2" == "all" ]; then
      #  IMAGES=$2
      #fi
      shift 1  #2
      ;;
    -m|--migrate)
      MIGRATE=true
      shift 1
      ;;
    --) # end argument parsing
      shift
      break
      ;;
    *) # unsupported flags
      echo "Error: Unsupported flag $1" >&2
      exit 1
      ;;
  esac
done

if ! [ $RESTART ] && [ "$(podman pod ps | grep $APP | wc -l)" != "0" ] ; then
    echo "Pod $APP is already running. Re-create it? y/N"
    read input
    case $input in
        y|Y) echo "Deleting pod $APP" && podman pod rm -f $APP ;;
        *) echo "Leaving build process" && exit 0 ;;
    esac
fi

if [ $UPDATE ]; then
    echo "Updating the local containers. Options:"
    printf "\t(1) Build locally\n"
    printf "\t(2) Download from $IMAGE_REPO\n"
    printf "\t(q) Quit\n"
    printf "Choice (Default 1) >>> " && read input
    case $input in
	2)
	    echo "Pull images from online repository"
	    for image in $IMAGES; do
            podman pull $DEFAULT_IMAGE:$image || exit 1;
	    done
        ;;
    q)
        echo "Exiting..." && exit 0;;
	*)
	    for image in $IMAGES; do
            echo "podman build -t $DEFAULT_IMAGE:$image ./$image || exit 1"
        done
        ;;
    esac
fi

if ! [ $RESTART ]; then
  echo "Create pod with name $APP"
  podman pod create --name $APP -p $NGINX_PORT || clean_exit $APP
else
  for image in $IMAGES; do
    podman stop $APP-$image
    podman rm $APP-$image
  done
fi

if [ "$(podman ps | grep $APP-api | wc -l)" == "0" ]; then
  echo "Create nginx server listening on port $NGINX_PORT"
  podman run -d --name $APP-nginx --pod $APP $DEFAULT_IMAGE:nginx || clean_exit $APP
fi

if [ "$(podman ps | grep $APP-api | wc -l)" == "0" ]; then
  echo "Create api service on port $API_PORT with name $APP-api"
  podman run -d \
      --name $APP-api \
      --pod $APP \
      -v $(pwd)/api:/api \
      -v $(pwd)/data:/var/lib/sqlite \
      $DEFAULT_IMAGE:api || clean_exit $APP
fi

if [ $MIGRATE ]; then
    podman exec -it $APP-api bash init_db.sh
fi


if [ "$(podman ps | grep $APP-ui | wc -l)" == "0" ]; then
  echo "Create ui service on port $UI_PORT with name $APP-ui"
  podman run -d --name $APP-ui --pod $APP $DEFAULT_IMAGE:ui || clean_exit $APP
fi

podman ps
