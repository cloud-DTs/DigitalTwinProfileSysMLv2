#!/bin/bash
# 'awk 1' == cat, but guarantees every file ends with a newline. Plain cat glues the
# last line of a file without a trailing newline onto the first line of the next one,
# which corrupts the model and shifts all following line numbers.
SYSML_CONTENT=$(awk 1 "$@")
docker exec \
  -e SYSML_CONTENT="$SYSML_CONTENT" \
  sysml-kernel-container \
  conda run --no-capture-output -n sysml python /home/sysml/process_sysml.py < /dev/null