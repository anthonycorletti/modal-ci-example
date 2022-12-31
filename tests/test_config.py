import json


async def test_load_config() -> None:
    from hudson.config import config

    config.init()
    c = config.load()
    assert c["server_url"] == "http://localhost:8000"


async def test_load_config_update() -> None:
    from hudson.config import config

    with open(config.config_path, "w") as f:
        json.dump({"server_url": "http://localhost:8002"}, f)

    config.init()

    assert config.server_url == "http://localhost:8000"

    config.server_url = "http://localhost:8002"
    config.save()

    assert config.server_url == "http://localhost:8002"
