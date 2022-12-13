#!/bin/sh -e

#
# TODO: automatically invoke this when the tests start
#
echo "Dropping the test database."
docker exec -it hudson-postgres psql -h 0.0.0.0 -U hudson -c "DROP DATABASE hudson_test;" || true

echo "Creating another database called hudson_test for testing."
docker exec -it hudson-postgres psql -h 0.0.0.0 -U hudson -c "CREATE DATABASE hudson_test;" || true
