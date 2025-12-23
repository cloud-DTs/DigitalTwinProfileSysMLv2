if [ "$#" -lt 1 ]; then
  echo "Usage: $0 file1.sysml [file2.sysml ...]"
  exit 1
fi

SYSML_CONTENT="$(cat "$@")"

docker run --rm \
  --network thenetwork \
  -e SYSML_CONTENT="$SYSML_CONTENT" \
  sysml.jupyter
