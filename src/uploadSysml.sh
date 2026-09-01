#!/bin/bash
set -eu

cat "$@" | docker exec -i sysml-kernel-container conda run --no-capture-output -n sysml python /home/sysml/process_sysml.py