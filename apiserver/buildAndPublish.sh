docker build -t sysml.jupyter -f Dockerfile.jupyter .
docker tag sysml.jupyter csba184/sysml.jupyter:latest
docker login
docker push csba184/sysml.jupyter:latest