#!/bin/bash

function get_env {
  echo "$(cat $1/.env | grep $2 | cut -d'=' -f2)"
}

APP=balancedview
API_PORT=$(get_env api FLASK_RUN_PORT)
UI_PORT=$(get_env ui FLASK_RUN_PORT)
NGINX_PORT=$(cat nginx/server.conf | grep listen | cut -d':' -f2 | tr -d ';')
IMAGE_REPO=docker.io/qmeeus
DEFAULT_IMAGE=$IMAGE_REPO/$APP
IMAGES="nginx api ui"
CONTAINERS="db nginx api ui"

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

while (( "$#" )); do
  case "$1" in
    -u|--update)
      UPDATE=true && shift 1;;
    -r|--restart)
      RESTART=true && shift 1;;
    -m|--migrate)
      MIGRATE=true && shift 1;;
    -c|--create_db)
      CREATE_DB=true && shift 1;;
    --) # end argument parsing
      shift && break;;
    *) # unsupported flags
      echo "Error: Unsupported flag $1" >&2 && exit 1;;
  esac
done

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
        podman build -t $DEFAULT_IMAGE:$image ./$image || exit 1
      done
      ;;
  esac
fi

if ! [ $(is_running) ]; then
  echo "Create pod with name $APP"
  podman pod create --name $APP -p $NGINX_PORT
else
  for container in $CONTAINERS; do
    printf "Restart $container? y/N >>> " && read input
    case $input in
      y|Y)
        podman stop $APP-$container || podman rm $APP-$container;;
      *)
        : ;;
    esac
  done
fi

if ! [ $(is_running db) ]; then
  echo "Run database container"
  DB_LOCATION=$(pwd)/data/postgres
  mkdir -p $DB_LOCATION
  DB_PWD="$(get_env api POSTGRES_PASSWORD)"
  podman run -d \
    --name $APP-db \
    --pod $APP \
    --rm \
    -v $(pwd)/data/postgres:/var/lib/postgresql/data \
    postgres
     # -e POSTGRES_PASSWORD=$DB_PWD \
  sleep 3
fi

if [ $CREATE_DB ]; then
  DB_USER=$(get_env api SQLALCHEMY_DATABASE_USER)
  DB_NAME=$(get_env api SQLALCHEMY_DATABASE_NAME)
  echo ">>> Waiting for PostgreSQL to start"
  until podman exec $APP-db psql -U postgres -c '\list'; do
    echo ">>>>>> PostgreSQL is not ready yet" && sleep 1
  done
  podman exec -u postgres $APP-db sh -c "createuser -wdrs $DB_USER && createdb $DB_NAME"
fi

if ! [ $(is_running nginx) ]; then
  echo "Run nginx server listening on port $NGINX_PORT"
  podman run -d \
    --name $APP-nginx \
    --pod $APP \
    --rm \
    $DEFAULT_IMAGE:nginx &
fi

if ! [ $(is_running api) ]; then
  echo "Run api service on port $API_PORT with name $APP-api"
  podman run -d \
    --name $APP-api \
    --pod $APP \
    --rm \
    -v $(pwd)/api:/api \
    $DEFAULT_IMAGE:api
        # -v $(pwd)/data:/var/lib/sqlite \
fi

if [ $MIGRATE ]; then
  podman exec -it $APP-api bash init_db.sh
fi

if ! [ $(is_running ui) ]; then
  echo "Run ui service on port $UI_PORT with name $APP-ui"
  podman run -d \
    --name $APP-ui \
    --pod $APP \
    --rm \
    $DEFAULT_IMAGE:ui
fi

podman ps
