from datetime import datetime
from typing import Any
from uuid import uuid4

from hudson.server.log import log


def test_logger(capsys: Any) -> None:
    log.exception("this is an exception")

    log.info(
        "testing types",
        extra={
            "string": "string",
            "bytes": b"test",
            "set": {"test", "test2"},
            "time": datetime.now(),
            "uuid": uuid4(),
        },
    )

    class MyUnsupportedType:
        def __init__(self, data: str) -> None:
            self.data = data

    log.info("testing types", extra={"random": MyUnsupportedType("test")})
    out, err = capsys.readouterr()
    assert out == ""
    assert "TypeError: Object of type MyUnsupportedType is not JSON serializable" in err
