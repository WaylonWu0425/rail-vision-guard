"""MySQL settings shared by the detection worker and the camera reader."""

import os
import re
from pathlib import Path

import yaml


SPRING_CONFIG_PATH = (
    Path(__file__).resolve().parents[2]
    / "station-monitoring-banckend/src/main/resources/application.yaml"
)
PLACEHOLDER = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)(?::([^}]*))?\}")
JDBC_URL = re.compile(r"jdbc:mysql://([^:/?]+)(?::(\d+))?/([^?]+)(?:\?.*)?")


def spring_value(value):
    """Resolve named environment variables and optional Spring defaults."""
    raw = "" if value is None else str(value)
    return PLACEHOLDER.sub(
        lambda match: os.getenv(match[1], match[2] or ""),
        raw,
    )


def mysql_options(config_path=SPRING_CONFIG_PATH):
    datasource = {}
    if config_path.is_file():
        with config_path.open(encoding="utf-8") as stream:
            config = yaml.safe_load(stream) or {}
        datasource = config.get("spring", {}).get("datasource", {})

    jdbc = JDBC_URL.fullmatch(spring_value(datasource.get("url")))
    settings = {
        "host": os.getenv("DETECTION_DB_HOST") or (jdbc[1] if jdbc else ""),
        "port": os.getenv("DETECTION_DB_PORT") or (jdbc[2] if jdbc else None) or "3306",
        "user": os.getenv("DETECTION_DB_USER") or spring_value(datasource.get("username")),
        "password": os.getenv("DETECTION_DB_PASSWORD", spring_value(datasource.get("password"))),
        "database": os.getenv("DETECTION_DB_NAME") or (jdbc[3] if jdbc else ""),
    }
    missing = [key for key in ("host", "user", "database") if not settings[key]]
    if missing:
        raise RuntimeError("Database configuration is incomplete: " + ", ".join(missing))

    try:
        port = int(settings["port"])
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        raise RuntimeError("MySQL port must be between 1 and 65535") from None
    settings["port"] = port
    return settings
