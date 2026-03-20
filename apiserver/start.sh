#!/bin/bash
set -e


conda run -n sysml jupyter nbconvert \
    --to notebook \
    --execute ${HOME}/SysML-v2-Release-2025-02/publish_notebook.ipynb \
    --output ${HOME}/SysML-v2-Release-2025-02/publish_notebook_output.ipynb


conda run -n sysml jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root \
    --ServerApp.token=''
