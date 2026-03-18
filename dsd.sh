# Login zu GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u DEIN_GITHUB_USERNAME --password-stdin

# Images bauen
cd apiserver
docker build -t ghcr.io/cloud-dts/sysml-jupyter:latest -f Dockerfile.jupyter .
docker build -t ghcr.io/cloud-dts/sysml-api:latest     -f Dockerfile.api     .

# Pushen
docker push ghcr.io/cloud-dts/sysml-jupyter:latest
docker push ghcr.io/cloud-dts/sysml-api:latest