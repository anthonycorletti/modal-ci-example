## Install Hudson

```sh
pip install hudson
```

## Start Hudson

In one shell session, start a new Hudson server and postgres server

```sh
hudson server # TODO this should also start the database and alembic upgrade head
```

## Run the example

In another shell session, stream some data into Hudson.

The code below is copy-pastable and runs as is. It will create a new namespace and dataset in Hudson, stream some data into it, and then print the data back out.

```Python
{!../docs_src/quickstart.py!}
```
