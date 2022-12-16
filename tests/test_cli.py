import time
from multiprocessing import Process

from typer.testing import CliRunner

from hudson import __version__
from hudson.cli.main import app


def test_cli_version(runner: CliRunner) -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output == __version__


def test_cli_start_server(runner: CliRunner) -> None:
    p = Process(target=runner.invoke, args=(app, ["server"]))
    p.start()
    time.sleep(1.8)
    p.terminate()
    p.join()
