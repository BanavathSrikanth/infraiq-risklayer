"""Keep same-named service packages isolated during repository test collection."""

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parent
SERVICE_ROOTS = {
    "ai-orchestration-service",
    "geospatial-service",
    "risk-service",
    "integration-service",
}


def pytest_collect_file(file_path, parent):
    if file_path.suffix != ".py" or not file_path.name.startswith("test"):
        return None

    parts = set(file_path.parts)
    service_name = next((name for name in SERVICE_ROOTS if name in parts), None)
    if service_name is None:
        return None

    service_root = ROOT / "apps" / "services" / service_name
    sys.path[:] = [
        entry
        for entry in sys.path
        if entry not in {str(ROOT), str(service_root)}
    ]
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(service_root))

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            del sys.modules[module_name]

    return pytest.Module.from_parent(parent, path=file_path)
