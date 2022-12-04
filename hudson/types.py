from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, StrictStr

from hudson.const import HudsonResourceKind


class HealthResponse(BaseModel):
    message: StrictStr
    version: StrictStr
    time: datetime


class BaseResource(BaseModel):
    id: StrictStr
    name: StrictStr
    kind: HudsonResourceKind
    version: StrictStr
    labels: Optional[Dict[StrictStr, StrictStr]] = None
    metadata: Optional[Dict[StrictStr, StrictStr]] = None
    spec: Optional[Dict[StrictStr, StrictStr]] = None


class Namespace(BaseResource):
    kind = HudsonResourceKind.namespace


class Node(BaseResource):
    kind = HudsonResourceKind.node
