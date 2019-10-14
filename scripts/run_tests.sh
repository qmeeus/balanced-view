#!/bin/bash

set -e

echo "Run tests. This might take a while..."
COMMAND="podman exec -it balancedview-api bash -c 'cd / && python -m api.tests.run_tests'"
echo $COMMAND
bash -c "$COMMAND"

