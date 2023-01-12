## Install Hudson

```sh
pip install hudson
```

## Run postgres

Hudson uses postgres as it's relational database. You can run postgres locally or in a docker container. For this example, we'll run postgres in a docker container. You can also run postgres locally if you prefer.

```sh
docker run --rm -d --name hudson-postgres \
-p 5432:5432 \
-e POSTGRES_PASSWORD=hudson \
-e POSTGRES_USER=hudson \
-e POSTGRES_PASSWORD=hudson \
-e POSTGRES_DB=hudson \
postgres:15.1
```

Run hudson's database migrations.

```sh
alembic upgrade head
```

## Start Hudson

```sh
hudson server
```

## ... 🤔

More coming soon!
