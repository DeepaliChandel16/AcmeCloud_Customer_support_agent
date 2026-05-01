import logging
import os
import sys

from src.config import AppConfig

logger = logging.getLogger("acmecloud")


def setup_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    ))
    root.setLevel(level)
    root.addHandler(handler)


def configure_observability(config: AppConfig) -> None:
    setup_logging()

    if not config.observability.enable:
        logger.info("Observability disabled in config")
        return

    os.environ.setdefault("ENABLE_INSTRUMENTATION", "true")
    os.environ.setdefault("OTEL_SERVICE_NAME", config.observability.service_name)

    if config.observability.sensitive_data:
        os.environ.setdefault("ENABLE_SENSITIVE_DATA", "true")

    exporter = config.observability.exporter

    if exporter == "console":
        logger.info("OTel exporter: console (traces printed to stdout)")
        os.environ.setdefault("OTEL_TRACES_EXPORTER", "console")
        os.environ.setdefault("OTEL_METRICS_EXPORTER", "none")
        os.environ.setdefault("OTEL_LOGS_EXPORTER", "none")
        os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", "")
        logging.getLogger("opentelemetry.exporter.otlp.proto.grpc.exporter").setLevel(logging.CRITICAL)
    else:
        logger.info("OTel exporter: otlp -> %s", config.observability.endpoint)
        os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", config.observability.endpoint)

    from agent_framework.observability import configure_otel_providers
    configure_otel_providers()
    logger.info("OpenTelemetry configured (service=%s)", config.observability.service_name)
