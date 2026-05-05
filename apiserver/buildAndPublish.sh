docker build -t sysml.jupyter -f Dockerfile.jupyter .
docker tag sysml.jupyter $1/sysml.jupyter:latest
docker login
docker push $1/sysml.jupyter:latest