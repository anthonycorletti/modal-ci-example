#!/bin/sh -e

POSTGRES_DB=${POSTGRES_DB:-modalci}

# run postgres in a docker container
echo "Starting postgres in a docker container."
docker run --rm -d --name modalci-postgres \
-p 5432:5432 \
-e POSTGRES_PASSWORD=modalci \
-e POSTGRES_USER=modalci \
-e POSTGRES_PASSWORD=modalci \
-e POSTGRES_DB=$POSTGRES_DB \
postgres:15.1

echo "Creating another database called modalci_test for testing."
sleep 1
if [ -t 1 ] ;
then
    docker exec -it modalci-postgres psql -h 0.0.0.0 -U modalci -c "CREATE DATABASE modalci_test;"
else
    echo "not a terminal";
fi
