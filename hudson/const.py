from enum import Enum


class HudsonResourceKind(str, Enum):
    namespace = "namespace"
    node = "node"
    volume = "volume"
    keyvaluemap = "keyvaluemap"
    secret = "secret"
    permission = "permission"
    permission_group = "permission_group"
    service_account = "service_account"
    workload_identity = "workload_identity"
    app = "app"
    deployment = "deployment"
