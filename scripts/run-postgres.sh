#!/bin/sh -e

# run postgres in a docker container
echo "Starting postgres in a docker container."
docker run --rm -d --name hudson-postgres \
-p 5432:5432 \
-e POSTGRES_PASSWORD=hudson \
-e POSTGRES_USER=hudson \
-e POSTGRES_PASSWORD=hudson \
-e POSTGRES_DB=hudson \
postgres:15.1

# Create another database called hudson_test
echo "Creating another database called hudson_test for testing."
docker exec -it hudson-postgres psql -h 0.0.0.0 -U hudson -c "CREATE DATABASE hudson_test;"
