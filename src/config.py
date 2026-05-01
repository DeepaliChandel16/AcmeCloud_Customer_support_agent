import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = Path(__file__).parent.parent / "config" / "settings.yaml"


@dataclass
class OllamaConfig:
    host: str = "http://localhost:11434"
    model: str = "qwen3:4b"


@dataclass
class ObservabilityConfig:
    enable: bool = True
    exporter: str = "console"  # "console" or "otlp"
    endpoint: str = "http://localhost:4317"
    service_name: str = "acmecloud-support"
    sensitive_data: bool = False


@dataclass
class AgentConfig:
    name: str = ""
    instructions: str = ""
    description: str = ""


@dataclass
class ToolsConfig:
    retry_max: int = 3
    retry_delay: float = 1.0


@dataclass
class AppConfig:
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    observability: ObservabilityConfig = field(default_factory=ObservabilityConfig)
    agents: dict[str, AgentConfig] = field(default_factory=dict)
    tools: ToolsConfig = field(default_factory=ToolsConfig)
    integrations: dict[str, dict] = field(default_factory=dict)


def load_config(path: Path = CONFIG_PATH) -> AppConfig:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    ollama_raw = raw.get("ollama", {})
    ollama = OllamaConfig(
        host=os.getenv("OLLAMA_HOST", ollama_raw.get("host", "http://localhost:11434")),
        model=os.getenv("OLLAMA_MODEL", ollama_raw.get("model", "qwen3:4b")),
    )

    obs_raw = raw.get("observability", {})
    observability = ObservabilityConfig(
        enable=obs_raw.get("enable", True),
        exporter=os.getenv("OTEL_EXPORTER", obs_raw.get("exporter", "console")),
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", obs_raw.get("endpoint", "http://localhost:4317")),
        service_name=os.getenv("OTEL_SERVICE_NAME", obs_raw.get("service_name", "acmecloud-support")),
        sensitive_data=obs_raw.get("sensitive_data", False),
    )

    agents = {}
    for key, val in raw.get("agents", {}).items():
        agents[key] = AgentConfig(
            name=val.get("name", key),
            instructions=val.get("instructions", ""),
            description=val.get("description", ""),
        )

    tools_raw = raw.get("tools", {})
    tools = ToolsConfig(
        retry_max=tools_raw.get("retry_max", 3),
        retry_delay=tools_raw.get("retry_delay", 1.0),
    )

    integrations = {}
    for key, val in raw.get("integrations", {}).items():
        integrations[key] = val if isinstance(val, dict) else {"provider": val}

    return AppConfig(ollama=ollama, observability=observability, agents=agents, tools=tools, integrations=integrations)
