"""Telemetry tool factory."""
from src.tools.interfaces import TelemetryProvider


def get_telemetry_provider(config: dict) -> TelemetryProvider:
    provider = config.get("provider", "mock")
    if provider == "mock":
        from src.tools.telemetry_module.mock import MockTelemetry
        return MockTelemetry()
    else:
        raise ValueError(f"Unknown telemetry provider: {provider}")
