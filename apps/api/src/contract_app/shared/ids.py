import uuid

def generate_id(prefix: str = "") -> str:
    unique_str = uuid.uuid4().hex[:12]
    return f"{prefix}_{unique_str}" if prefix else unique_str

def contract_id() -> str:
    return generate_id("ctr")

def version_id() -> str:
    return generate_id("ver")

def session_id() -> str:
    return generate_id("ses")

def run_id() -> str:
    return generate_id("run")

def issue_group_id() -> str:
    return generate_id("iss")

def operation_id() -> str:
    return generate_id("op")

def plan_id() -> str:
    return generate_id("plan")

def command_id() -> str:
    return generate_id("cmd")

def export_id() -> str:
    return generate_id("exp")

def save_request_id() -> str:
    return generate_id("save")
