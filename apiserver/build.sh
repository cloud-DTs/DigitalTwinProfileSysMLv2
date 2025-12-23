docker build -t sysml.jupyter -f Dockerfile.jupyter .
docker build -t sysml.api     -f Dockerfile.api     .
docker network create thenetwork
docker volume create postgresdbserver
docker-compose up -d postgresdbserver sysmlapiserver

