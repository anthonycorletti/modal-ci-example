from enum import Enum


class HudsonResourceKind(str, Enum):
    namespace = "namespace"
    node = "node"
    volume = "volume"
    config = "config"
    app = "app"
    deployment = "deployment"
    secret = "secret"
    serviceaccount = "serviceaccount"
    workloadid = "workloadid"
