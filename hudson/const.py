from enum import Enum


class HudsonResourceKind(str, Enum):
    namespace = "namespace"
    node = "node"
    volume = "volume"
    config = "config"
    app = "app"
    deployment = "deployment"
    secret = "secret"
    permission = "permission"
    permission_group = "permission_group"
    service_account = "service_account"
    workload_identity = "workload_identity"
