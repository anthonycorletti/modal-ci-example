## Install Hudson

```sh
pip install hudson
```

## Run postgres and make database migrations

Here's an example of how to run postgres in a docker container. You can also run postgres locally if you prefer.

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

## Run the example

In another shell session, stream some data into Hudson.

The code below is copy-pastable and runs as is. It will create a new namespace and dataset in Hudson, stream some data into it, and then print the data back out.

```Python
{!../docs_src/quickstart.py!}
```
