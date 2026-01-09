#!/bin/bash
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 publish_guid project_id file1.sysml [file2.sysml ...]"
  exit 1
fi

PUBLISH_GUID="$1"
PROJECT_ID="$2"
shift 2

SYSML_CONTENT=$(cat "$@")

docker exec -it \
  -e SYSML_CONTENT="$SYSML_CONTENT" \
  -e PUBLISH_GUID="$PUBLISH_GUID" \
  -e PROJECT_ID="$PROJECT_ID" \
  sysml-kernel-container \
  conda run -n sysml python /home/sysml/process_sysml.py