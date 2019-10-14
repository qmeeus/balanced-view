#!/bin/bash

set -e

source config.sh
LOGFILE=$LOGDIR/tests.log

echo "Run tests. This might take a while..."
COMMAND="podman exec -it balancedview-api python -m api.tests.run_tests"
echo $COMMAND
bash -c "$COMMAND" > $LOGFILE 2>&1

