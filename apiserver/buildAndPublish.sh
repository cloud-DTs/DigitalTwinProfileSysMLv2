docker build -t sysml.jupyter -f Dockerfile.jupyter .
docker build -t sysml.api     -f Dockerfile.api .

docker tag sysml.jupyter $1/sysml.jupyter:latest
docker tag sysml.api     $1/sysml.api:latest
docker login
docker push $1/sysml.jupyter:latest
docker push $1/sysml.api:latest