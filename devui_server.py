"""Launch Microsoft Agent Framework DevUI for debugging and tracing.

DevUI provides a web UI with built-in OpenTelemetry trace viewer.
Run this alongside the Streamlit app for development/debugging.

Usage:
    python devui_server.py
    # Opens http://localhost:8080
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent_framework.devui import serve

from src.config import load_config
from src.observability.setup import configure_observability
from src.orchestration.workflow import build_support_workflow

config = load_config()
configure_observability(config)

workflow = build_support_workflow(config)

serve(
    entities=[workflow],
    port=8080,
    auto_open=True,
    instrumentation_enabled=True,
)
