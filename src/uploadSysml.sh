#!/bin/bash
SYSML_CONTENT=$(cat "$@")
docker exec \
  -e SYSML_CONTENT="$SYSML_CONTENT" \
  sysml-kernel-container \
  conda run --no-capture-output -n sysml python /home/sysml/process_sysml.py < /dev/null