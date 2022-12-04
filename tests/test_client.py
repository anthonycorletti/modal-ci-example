from hudson.exc import BaseHudsonException


def test_base_exception() -> None:
    assert issubclass(BaseHudsonException, Exception)
