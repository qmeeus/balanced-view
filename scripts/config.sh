#!/bin/bash

set -e

PROJECT_ROOT="$(dirname "$(dirname "$(readlink -fm "$0")")")"
REGISTRY=docker.io
REGISTRY_USER=qmeeus
REPO=$REGISTRY/$REGISTRY_USER
APP=balancedview
UI_PORT_EXT="$(grep listen $PROJECT_ROOT/nginx/services/ui.conf | cut -d':' -f2 | tr -d ';')"
API_PORT_EXT="$(grep listen $PROJECT_ROOT/nginx/services/api.conf | cut -d':' -f2 | tr -d ';')"
EXTERNAL_PORTS="$UI_PORT_EXT $API_PORT_EXT 5601"
LOGDIR=$PROJECT_ROOT/logs

function is_running {
  # Usage: is_running CONTAINER
  echo $(podman ps | grep $1 | wc -l)
}

function user_input {
  # Usage: user_input "Do something"
  printf "$1? y/N >>> " >&2
  read yesno
  case $yesno in
    y|Y) echo 1;;
    *) echo 0;;
  esac
}

function get_context {
  # Usage: get_context api
  CONTEXT=$PROJECT_ROOT/$1
  case $1 in
    es)
      CONTEXT=$PROJECT_ROOT/elasticsearch ;;
    vis)
      CONTEXT=$PROJECT_ROOT/kibana ;;
    *) : ;;
  esac
  echo $CONTEXT
}
