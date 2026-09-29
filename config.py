import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 5000
    columns: int = 3
    max_height: int = 500
    monitor_interval_ms: int = 1000
    preset_file: str = "presets.json"
    log_level: str = "INFO"


def load_settings() -> Settings:
    return Settings(
        host=os.getenv("EMBED_HOST", "127.0.0.1"),
        port=int(os.getenv("EMBED_PORT", "5000")),
        columns=max(1, int(os.getenv("EMBED_COLUMNS", "3"))),
        max_height=max(100, int(os.getenv("EMBED_MAX_HEIGHT", "500"))),
        monitor_interval_ms=max(250, int(os.getenv("EMBED_MONITOR_MS", "1000"))),
        preset_file=os.getenv("EMBED_PRESETS", "presets.json"),
        log_level=os.getenv("EMBED_LOG_LEVEL", "INFO"),
    )
