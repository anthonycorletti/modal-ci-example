import json
import os
from pathlib import Path
from typing import Optional

from pydantic import UUID4, AnyUrl, BaseModel, DirectoryPath, Field, FilePath, StrictInt


class HudsonClientConfig(BaseModel):
    config_path: FilePath = Field(
        default=Path(f"{os.environ['HOME']}/.hudson/config.json"),
        description="The path to the config file",
    )
    namespace_id: Optional[UUID4] = Field(
        description="The namespace ID",
    )
    dataset_id: Optional[UUID4] = Field(
        description="The dataset ID",
    )
    server_url: AnyUrl = Field(
        default="http://localhost:8000",
        description="The hudson server URL",
    )
    min_batch_upload_size: StrictInt = Field(
        default=64,
        description="The minimum number of samples needed to upload data",
    )
    timeout_seconds: StrictInt = Field(
        default=60,
        description="Max seconds the client will wait for the server",
    )
    client_watch_dir: DirectoryPath = Field(
        default=Path(f"{os.environ['PWD']}/.hudson/watch"),
        description="The directory to watch for data.",
    )

    def init(self) -> None:
        if self.config_path.exists():
            self.load()
        else:
            self.save()

    def load(self) -> None:
        self.__dict__.update(self.load_config())

    def save(self) -> None:
        self.save_config()

    def load_config(self) -> dict:
        with open(str(self.config_path), "r") as f:
            return json.load(f)

    def save_config(self) -> None:
        data = json.loads(self.json())
        with open(str(self.config_path), "w") as f:
            json.dump(data, f)


config = HudsonClientConfig()
config.init()
