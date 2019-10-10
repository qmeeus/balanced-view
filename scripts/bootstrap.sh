#!/bin/bash

set -e

function usage {
    cat <<EOF
USAGE: ./bootstrap.sh [OPTIONS]
Bootstrap script to setup the different services composing balancedview
The script is interactive and will ask what services should be restarted
or updated.

OPTIONS
    -h --help       Display this help and exit
    -u --update     Pull one or more containers from $REPO
    -b --build      Build one or more containers locally
    -r --restart    Restart one or more containers
    -t --run-tests  Run the tests before exiting

EOF
}

declare -a BACKPID

function wait_for_processes {
  if (( ${#BACKPID[@]} )); then
    echo "Wait for ${#BACKPID[@]} processes to finish..."
    while (( "${#BACKPID[@]}" )); do
      PID=${BACKPID[${#BACKPID[@]}-1]}
      if (kill -s 0 $PID 2>/dev/null); then
        wait $PID && echo "*$PID ended*"
      fi
      unset BACKPID[${#BACKPID[@]}-1]
    done
  fi
}

function cleanup {
  if (( ${#BACKPID[@]} )); then
    echo "Trying to kill ${#BACKPID[@]} processes"
    for PID in "${BACKPID[@]}"; do
      if (kill -s 0 $PID 2> /dev/null); then
        kill -9 $PID
      fi
    done
  fi
}

trap cleanup EXIT

source config.sh

# Parse command line arguments
while (( "$#" )); do
  case "$1" in
    -u|--update) UPDATE=true && shift 1;;
    -b|--build) BUILD=true && shift 1;;
    -r|--restart) RESTART=true && shift 1;;
    -a|--all) ALL=true && shift 1;;
    -t|--run-tests) RUN_TESTS=true && shift 1;;
    -h|--help) usage && exit 0;;
    --) shift && break;; # End of arguments
    *) echo "Error: Unsupported flag $1" >&2 && exit 1;;
  esac
done

if { [ $UPDATE ] && [ $BUILD ] ;} || { [ $UPDATE ] && [ $RESTART ] ;} || { [ $RESTART ] && [ $BUILD ] ;}; then
  echo "Choose either to update or build the containers"
  exit 1
fi

SERVICES="es vis api ui nginx"
for SERVICE in $SERVICES; do
  if [ $UPDATE ]; then

    if [[ $(user_input "Update $SERVICE") = 1 ]]; then
      ./update.sh $SERVICE & BACKPID=( "${BACKPID[@]}" "$!" )
      RESTART_SERVICE=true
    fi
  elif [ $BUILD ]; then
    if [[ $(user_input "Build $SERVICE") = 1 ]]; then
      ./build.sh $SERVICE & BACKPID=( "${BACKPID[@]}" "$!" )
      RESTART_SERVICE=true
    fi
  elif [ $RESTART ]; then
    if [[ $(user_input "Restart $SERVICE") = 1 ]]; then
      RESTART_SERVICE=true
    fi
  fi
  if [ $RESTART_SERVICE ]; then
    ./stop_and_remove.sh $SERVICE & BACKPID=( "${BACKPID[@]}" "$!" )
  fi
done

if (( $(podman pod ps  | grep $APP | wc -l) )); then
  if [[ $(user_input "Pod $APP already exists. Re-create it") = 1 ]]; then
    for SERVICE in $SERVICES; do
      ./stop_and_remove.sh $SERVICE & BACKPID=( "${BACKPID[@]}" "$!" )
    done
    wait_for_processes
    podman pod rm $APP
  fi
fi

./create_pod.sh
wait_for_processes

for SERVICE in $SERVICES; do
  if ! (( $(is_running $SERVICE) )); then
    ./run.sh $SERVICE & BACKPID=( "${BACKPID[@]}" "$!" )
  fi
  if [ "$SERVICE" = "es" ]; then
    wait_for_processes
    ./generate_auth.sh & BACKPID=( "${BACKPID[@]}" "$!" )
  fi
done

wait_for_processes

if [ $RUN_TESTS ]; then
  ./run_tests.sh
fi

podman ps
