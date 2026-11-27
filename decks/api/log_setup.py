import logging

import structlog


class LogSetup:
    """Configure structlog and route the standard ``logging`` records through it."""

    def __init__(self, *, json_logs: bool) -> None:
        self._json_logs = json_logs

    def configure(self) -> None:
        """Set up logging. Call it once, from the app factory."""
        shared = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
        ]
        structlog.configure(
            processors=[*shared, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        renderer = (
            structlog.processors.JSONRenderer()
            if self._json_logs
            else structlog.dev.ConsoleRenderer()
        )
        handler = logging.StreamHandler()
        handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                foreign_pre_chain=shared,
                processors=[structlog.stdlib.ProcessorFormatter.remove_processors_meta, renderer],
            )
        )
        root = logging.getLogger()
        root.handlers = [handler]
        root.setLevel(logging.INFO)
