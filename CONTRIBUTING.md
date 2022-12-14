# Contributing

Assuming you have cloned this repository to your local machine, you can follow these guidelines to make contributions.

**First, please install pyenv <https://github.com/pyenv/pyenv> to manage your python environment.**

Install the version of python as mentioned in this repo.

```sh
pyenv install $(cat .python-version)
```

## Use a virtual environment

```sh
python -m venv .venv
```

This will create a directory `.venv` with python binaries and then you will be able to install packages for that isolated environment.

Next, activate the environment.

```sh
source .venv/bin/activate
```

To check that it worked correctly;

```sh
which python pip
```

You should see paths that use the .venv/bin in your current working directory.

## Installing dependencies

This project uses `pip` to manage our project's dependencies.

Install dependencies;

```sh
./scripts/install.sh
pyenv rehash
```

## Formatting

```sh
./scripts/format.sh
```

## Tests

Make sure postgres is running. We have a script that runs a postgres docker container for you.

```sh
./scripts/run-postgres.sh
```

Then run the tests. The tests should automatically run migrations for the app.

```sh
./scripts/test.sh
```

## Running hudson

Start postgres

```sh
./scripts/run-postgres.sh
```

Start hudson

```sh
hudson server --reload
```

Check that hudson is running

```
$ curl -s "http://localhost:8000/healthcheck" | jq .message
"⛵️"
```
