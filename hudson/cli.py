import typer
import uvicorn

from hudson import __version__
from hudson.const import APP_IMPORT_STRING, HUDSON

name = f"{HUDSON} {__version__}"

app = typer.Typer(
    name=name,
    rich_markup_mode="markdown",
    no_args_is_help=True,
)


@app.callback()
def main_callback() -> None:
    pass


main_callback.__doc__ = name


@app.command("version")
def _version() -> None:
    """Print the version of Hudson."""
    typer.echo(__version__, nl=False)


@app.command("server")
def _server(
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="Bind socket to this host.",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        help="Bind socket to this port.",
    ),
    reload: bool = typer.Option(
        False,
        help="Reload the server on code changes.",
    ),
    workers: int = typer.Option(
        1,
        "--workers",
        help="Number of workers to run.",
    ),
) -> None:
    """Start the Hudson server."""
    uvicorn.run(  # pragma: no cover
        app=APP_IMPORT_STRING,
        port=port,
        host=host,
        reload=reload,
        workers=workers,
    )


@app.command("test")
def _test() -> None:
    # TODO: this doesnt work as is – need to figure out how to run pytest
    pass
    # parallelized in modal
    # import os

    # import modal
    # import pytest

    # from hudson.settings import _Env

    # stub = modal.Stub("ci")

    # stub["env"] = modal.Secret(_Env(_env_file=".env.test").dict())
    # image = modal.Image.debian_slim().pip_install(["pytest"])

    # @stub.function(
    #     image=image,
    #     mounts=[
    #         modal.Mount(
    #             local_dir=f"{os.environ['HOME']}/modal-async-pubsub-example/app",
    #             remote_dir="/root/modal-async-pubsub-example/app",
    #         ),
    #         modal.Mount(
    #             local_dir=f"{os.environ['HOME']}/modal-async-pubsub-example/tests",
    #             remote_dir="/root/modal-async-pubsub-example/tests",
    #         ),
    #     ],
    #     secret=stub["env"],
    # )
    # def _test() -> int:

    #     return pytest.main(["/root/modal-async-pubsub-example/tests"])

    # if __name__ == "__main__":
    #     with stub.run():
    #         rcode = _test()
    #         if rcode != 0:
    #             raise RuntimeError(f"pytest returned {rcode}")


@app.command("deploy")
def _deploy(
    name: str = typer.Argument(..., help="Name of the project to deploy."),
    stub_filepath: str = typer.Option(
        "hudson._modal",
        "--stub-path",
        "-s",
        help="Filepath reference to the stub to deploy. "
        "Relative the project module root.",
    ),
) -> None:  # pragma: no cover
    """Deploy Hudson to Modal."""
    from modal.cli.app import deploy

    deploy(
        name=name,
        stub_ref=stub_filepath,
    )
