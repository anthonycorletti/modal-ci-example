import typer
import uvicorn

from hudson import __version__
from hudson.server.config import HudsonServerConfig

name = f"Hudson ⛵️ {__version__}"

app = typer.Typer(name=name, no_args_is_help=True)


@app.callback()
def main_callback() -> None:
    pass


main_callback.__doc__ = name


@app.command("version")
def _version() -> None:
    typer.echo(__version__, nl=False)


@app.command("server")
def _server() -> None:
    from hudson.server.main import app as server_app

    _config = HudsonServerConfig()
    uvicorn.run(
        app=server_app,
        port=_config.port,
        host=_config.host,
    )
