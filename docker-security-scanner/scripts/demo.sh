#!/bin/bash

IMAGE_NAME="secdevops-sample:latest"
CONFIG_FILE="demo.yaml"

echo "==== Building/Pulling Sample Image ===="
cat <<EOF > Dockerfile
FROM alpine:3.18.0
RUN apk add --no-cache bash curl
EOF

docker build -t $IMAGE_NAME .

echo "==== Running Automated Vulnerability Scan ===="
trivy --config $CONFIG_FILE $IMAGE_NAME
SCAN_EXIT_CODE=$?

echo "==== Scanning Process Completed ===="
if [ $SCAN_EXIT_CODE -ne 0 ]; then
    echo "BUILD FAILED: High or Critical vulnerabilities detected!"
    exit $SCAN_EXIT_CODE
else
    echo "BUILD PASSED: No blocking vulnerabilities found."
    exit 0
fi