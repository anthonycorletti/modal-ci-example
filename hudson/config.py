import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional

from pydantic import UUID4, BaseModel, Field, StrictInt, StrictStr


class HudsonClientConfig(BaseModel):
    config_path: StrictStr = Field(
        default=f"{os.environ['HOME']}/.hudson/config.json",
        description="The path to the config file",
    )
    namespace_id: Optional[UUID4] = Field(
        description="The namespace ID",
    )
    server_url: StrictStr = Field(
        default="http://localhost:8000",
        description="The hudson server URL",
    )
    min_batch_upload_size: StrictInt = Field(
        default=64,
        description="The minimum number of samples needed to upload data",
    )
    timeout_seconds: StrictInt = Field(
        default=300,
        description="Max seconds the client will wait for the server",
    )

    def init(self) -> None:
        if Path(self.config_path).exists():
            self.load()
        else:
            self.save()

    def load(self) -> Dict:
        return self._load_config()

    def save(self) -> None:
        self._save_config()

    def _load_config(self) -> Dict:
        with open(self.config_path, "r") as f:
            return json.load(f)

    def _save_config(self) -> None:
        data = json.loads(self.json())
        # if the config file dir doesn't exist, create it
        Path(os.path.dirname(self.config_path)).mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(data, f)


config = HudsonClientConfig()

if "pytest" in "".join(sys.argv):
    config = HudsonClientConfig(
        config_path=f"{os.environ['HOME']}/.hudson/config.json.test",
    )

config.init()
