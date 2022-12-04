from pydantic import BaseModel, StrictInt, StrictStr


class HudsonServerConfig(BaseModel):
    host: StrictStr = "127.0.0.1"
    port: StrictInt = 8000
