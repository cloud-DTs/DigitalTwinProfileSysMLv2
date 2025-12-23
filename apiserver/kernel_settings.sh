#!/bin/bash
set -e

echo "Patching kernel.json..."

sed -i 's|http://sysml2.intercax.com:9000|http://sysmlapiserver:9000|g' \
  /home/sysml/conda/share/jupyter/kernels/sysml/kernel.json

echo "Starting Jupyter..."
exec start-notebook.sh
