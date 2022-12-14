#!/bin/sh -e

POSTGRES_DB=${POSTGRES_DB:-hudson}

# run postgres in a docker container
echo "Starting postgres in a docker container."
docker run --rm -d --name hudson-postgres \
-p 5432:5432 \
-e POSTGRES_PASSWORD=hudson \
-e POSTGRES_USER=hudson \
-e POSTGRES_PASSWORD=hudson \
-e POSTGRES_DB=$POSTGRES_DB \
postgres:15.1

echo "Creating another database called hudson_test for testing."
sleep 1
if [ -t 1 ] ;
then
    docker exec -it hudson-postgres psql -h 0.0.0.0 -U hudson -c "CREATE DATABASE hudson_test;"
else
    echo "not a terminal";
fi
