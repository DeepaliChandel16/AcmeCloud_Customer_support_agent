"""In-memory mock telemetry provider for development and testing."""
from src.tools.interfaces import TelemetryProvider

_SERVICES = {
    "api-gateway": {"status": "operational", "uptime_pct": 99.98, "latency_ms": 45},
    "auth-service": {"status": "operational", "uptime_pct": 99.95, "latency_ms": 120},
    "storage-service": {"status": "degraded", "uptime_pct": 98.50, "latency_ms": 350},
    "billing-service": {"status": "operational", "uptime_pct": 99.99, "latency_ms": 80},
    "notification-service": {"status": "operational", "uptime_pct": 99.90, "latency_ms": 60},
}


class MockTelemetry(TelemetryProvider):
    def get_service_status(self, service_name: str = "") -> str:
        if service_name:
            svc = _SERVICES.get(service_name)
            if not svc:
                available = ", ".join(_SERVICES.keys())
                return f"Error: Service '{service_name}' not found. Available: {available}."
            return (
                f"Service '{service_name}': Status={svc['status']}, "
                f"Uptime={svc['uptime_pct']}%, Latency={svc['latency_ms']}ms."
            )
        lines = []
        for name, svc in _SERVICES.items():
            lines.append(f"  {name}: {svc['status']} (uptime {svc['uptime_pct']}%, latency {svc['latency_ms']}ms)")
        return "AcmeCloud Service Status:\n" + "\n".join(lines)
