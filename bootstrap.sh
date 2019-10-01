#!/bin/bash

set -e

function get_env {
  echo "$(cat $1/.env | grep $2 | cut -d'=' -f2)"
}

function get_nginx_port {
  echo "$(cat nginx/services/$1.conf | grep listen | cut -d':' -f2 | tr -d ';')"
}

APP=balancedview
API_PORT=$(get_env api FLASK_RUN_PORT)
UI_PORT=$(get_env ui FLASK_RUN_PORT)
ES_PORT=$(get_env api ES_PORT)
NGINX_PORT1=$(get_nginx_port ui)
NGINX_PORT2=$(get_nginx_port api)
IMAGE_REPO=docker.io/qmeeus
DEFAULT_IMAGE=$IMAGE_REPO/$APP
IMAGES="nginx api ui"
CONTAINERS="es nginx api ui"

function is_running {
  if ! [ $1 ]; then
    if [ "$(podman pod ps | grep $APP | wc -l)" != "0" ]; then
      echo 1
    fi
  else
    if [ "$(podman ps | grep $APP-$1 | wc -l)" != "0" ]; then
      echo 1
    fi
  fi
}

function wait_for_processes {
  while (( "$#" )); do
    pid=$1
    shift 1
    if (kill -s 0 $pid 2>/dev/null); then
      echo "Wait for process $pid to finish" && wait $pid
    fi
  done
}

# 0) Parse the script arguments
while (( "$#" )); do
  case "$1" in
    -u|--update)
      UPDATE=true && shift 1;;
    -r|--restart)
      RESTART=true && shift 1;;
    --) # end argument parsing
      shift && break;;
    *) # unsupported flags
      echo "Error: Unsupported flag $1" >&2 && exit 1;;
  esac
done

# 1) Stop and remove the containers / pod
if ! [ $RESTART ] && [ $(is_running) ] ; then
  printf "Pod $APP is already running. Re-create it? y/N >>> " && read input
  case $input in
    y|Y)
      echo "Deleting pod $APP"
      podman ps -a | grep $APP | cut -d" " -f1 \
        | xargs -I "{}" bash -c 'podman stop {} || podman rm {}' \
        && podman pod rm $APP
      ;;
    *) : ;; # echo "Exiting..." && exit 0
  esac
fi

# 2) Update the images if necessary
if [ $UPDATE ]; then
  echo "Updating the local containers. Options:"
  printf "\t(1) Build locally\n"
  printf "\t(2) Download from $IMAGE_REPO\n"
  printf "\t(q) Quit\n"
  printf "Choice (Default 1) >>> " && read input

  BACK_PID=""

  case $input in
    2)
      echo "Pull images from online repository"
      for image in $IMAGES; do
        podman pull -q $DEFAULT_IMAGE:$image || exit 1 &
        BACK_PID="$BACK_PID $!"
      done
      ;;
    q)
      echo "Exiting..." && exit 0;;
    *)
      echo "Build images locally"
      for image in $IMAGES; do
        podman build -t $DEFAULT_IMAGE:$image -q ./$image || exit 1 &
        BACK_PID="$BACK_PID $!"
      done
      ;;
  esac

  wait_for_processes $BACK_PID

fi

# 3) Start the different services
BACK_PID=""

# 3a) Create the pod and stop the running containers if necessary
if ! [ $(is_running) ]; then
  echo "Create pod with name $APP"
  podman pod create --name $APP -p $NGINX_PORT1 -p $NGINX_PORT2
else
  for container in $CONTAINERS; do
    printf "Restart $container? y/N >>> " && read input
    case $input in
      y|Y)
        podman stop $APP-$container 2>/dev/null || podman rm $APP-$container 2>/dev/null || true &
        BACK_PID="$BACK_PID $!"
        ;;
      *) : ;;
    esac
  done

  wait_for_processes $BACK_PID

fi

BACK_PID=""

# 3b) Start ElasticSearch
if ! [ $(is_running es) ]; then
  echo "Start elasticsearch"
  DATA_DIR=$(pwd)/data/elasticsearch
  [ -d $DATA_DIR ] || bash -c "mkdir $DATA_DIR && chmod 777 $DATA_DIR"
  podman run -d \
    --name $APP-es \
    --pod $APP \
    --rm \
    -v $DATA_DIR:/usr/share/elasticsearch/data \
    -e "discovery.type=single-node" \
    docker.elastic.co/elasticsearch/elasticsearch:7.3.2 &
    BACK_PID="$BACK_PID $!"
fi

# 3c) Start the web server
if ! [ $(is_running nginx) ]; then
  echo "Run nginx server listening on ports $NGINX_PORT1 and $NGINX_PORT2"
  podman run -d \
    --name $APP-nginx \
    --pod $APP \
    --rm \
    $DEFAULT_IMAGE:nginx &
    BACK_PID="$BACK_PID $!"
fi

# 3d) Start the API
if ! [ $(is_running api) ]; then
  echo "Run api service on port $API_PORT with name $APP-api"
  podman run -d \
    --name $APP-api \
    --pod $APP \
    --rm \
    $DEFAULT_IMAGE:api &
    BACK_PID="$BACK_PID $!"
fi

# 3e) Start the UI
if ! [ $(is_running ui) ]; then
  echo "Run ui service on port $UI_PORT with name $APP-ui"
  podman run -d \
    --name $APP-ui \
    --pod $APP \
    --rm \
    $DEFAULT_IMAGE:ui &
    BACK_PID="$BACK_PID $!"
fi

# 4) Wait for the last processes to finish
wait_for_processes $BACK_PID

podman ps
