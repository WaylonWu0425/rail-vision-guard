"""YOLO camera detection service used by the Vue monitoring page.

The service reads online cameras from the existing MySQL database, opens their
RTSP sub-streams, runs the trained Ultralytics model and exposes annotated MJPEG
streams.  An alarm is written only when a configured class actually changes
from absent to present; there is no timer-based synthetic alarm generation.
"""

from __future__ import annotations

import atexit
import json
import logging
import os
import re
import threading
import time
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from urllib.parse import quote

import cv2
import numpy as np
import pymysql
import yaml
from inference_strategies import STRATEGIES, predict_boxes
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent.parent
DEFAULT_MODEL_PATH = BASE_DIR / "models" / "best.pt"
EVIDENCE_DIR = BASE_DIR / "evidence"
BASELINE_DIR = BASE_DIR / "baselines"
BACKEND_CONFIG_PATH = (
    PROJECT_DIR
    / "station-monitoring-banckend"
    / "src"
    / "main"
    / "resources"
    / "application.yaml"
)

logging.basicConfig(
    level=os.getenv("DETECTION_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
LOGGER = logging.getLogger("detection-service")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
BASELINE_DIR.mkdir(parents=True, exist_ok=True)


def env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


CONFIDENCE = min(max(env_float("DETECTION_CONFIDENCE", 0.45), 0.05), 0.99)
INFERENCE_INTERVAL = max(env_float("DETECTION_INTERVAL_SECONDS", 0.5), 0.05)
ALARM_COOLDOWN = max(env_float("DETECTION_ALARM_COOLDOWN_SECONDS", 30.0), 0.0)
ABSENCE_RESET = max(env_float("DETECTION_ABSENCE_RESET_SECONDS", 2.0), 0.2)
REGION_RULE_REFRESH_SECONDS = max(env_float("DETECTION_REGION_REFRESH_SECONDS", 1.0), 0.2)
JPEG_QUALITY = min(max(env_int("DETECTION_JPEG_QUALITY", 82), 30), 100)
RTSP_PORT = env_int("DETECTION_RTSP_PORT", 554)
RTSP_SUBTYPE = env_int("DETECTION_RTSP_SUBTYPE", 1)
DEVICE_REQUEST = os.getenv("DETECTION_DEVICE", "auto").strip().lower() or "auto"
TRACK_BUFFER = max(env_int("DETECTION_TRACK_BUFFER", 30), 5)
TRACK_HIGH_THRESHOLD = min(max(env_float("DETECTION_TRACK_HIGH_THRESHOLD", 0.25), 0.05), 0.95)
TRACK_LOW_THRESHOLD = min(max(env_float("DETECTION_TRACK_LOW_THRESHOLD", 0.10), 0.01), TRACK_HIGH_THRESHOLD)
TRACK_MATCH_THRESHOLD = min(max(env_float("DETECTION_TRACK_MATCH_THRESHOLD", 0.80), 0.1), 0.99)
BASELINE_MAX_BRIGHTNESS_DELTA = max(env_float("DETECTION_BASELINE_MAX_BRIGHTNESS_DELTA", 60.0), 5.0)
BASELINE_MAX_SHIFT_RATIO = min(max(env_float("DETECTION_BASELINE_MAX_SHIFT_RATIO", 0.025), 0.005), 0.20)
ALARM_CLASSES = {
    value.strip().lower()
    for value in os.getenv("DETECTION_ALARM_CLASSES", "person,car").split(",")
    if value.strip()
}

CLASS_TEXT = {
    "person": ("人员", 0, 1),
    "car": ("车辆", 1, 1),
}


def load_database_config() -> dict[str, Any]:
    """Read database settings from environment or the Spring configuration."""
    config: dict[str, Any] = {
        "host": os.getenv("DETECTION_DB_HOST"),
        "port": env_int("DETECTION_DB_PORT", 3306),
        "user": os.getenv("DETECTION_DB_USER"),
        "password": os.getenv("DETECTION_DB_PASSWORD"),
        "database": os.getenv("DETECTION_DB_NAME"),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "connect_timeout": 5,
        "read_timeout": 5,
        "write_timeout": 5,
        "autocommit": True,
    }

    if BACKEND_CONFIG_PATH.exists():
        with BACKEND_CONFIG_PATH.open("r", encoding="utf-8") as stream:
            spring_config = yaml.safe_load(stream) or {}
        datasource = spring_config.get("spring", {}).get("datasource", {})
        jdbc_url = str(datasource.get("url", ""))
        match = re.search(r"jdbc:mysql://([^:/?]+)(?::(\d+))?/([^?]+)", jdbc_url)
        if match:
            config["host"] = config["host"] or match.group(1)
            config["port"] = env_int(
                "DETECTION_DB_PORT", int(match.group(2) or 3306)
            )
            config["database"] = config["database"] or match.group(3)
        config["user"] = config["user"] or datasource.get("username")
        if config["password"] is None:
            config["password"] = datasource.get("password", "")

    missing = [key for key in ("host", "user", "database") if not config.get(key)]
    if missing:
        raise RuntimeError(
            "Database configuration is incomplete: " + ", ".join(missing)
        )
    # YAML interprets an unquoted numeric password as int; database drivers
    # require text/bytes credentials.
    config["host"] = str(config["host"])
    config["user"] = str(config["user"])
    config["password"] = str(config.get("password") or "")
    config["database"] = str(config["database"])
    return config


class Repository:
    def __init__(self) -> None:
        self.config = load_database_config()
        self.ensure_schema()

    def connect(self):
        return pymysql.connect(**self.config)

    def ensure_schema(self) -> None:
        """Create the small rule table without changing existing business tables."""
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS detection_region (
                        camera_id BIGINT NOT NULL,
                        name VARCHAR(64) NOT NULL DEFAULT '警戒区域',
                        points_json TEXT NOT NULL,
                        enabled TINYINT(1) NOT NULL DEFAULT 1,
                        dwell_seconds DECIMAL(5,2) NOT NULL DEFAULT 2.00,
                        target_classes_json TEXT NULL,
                        cooldown_seconds DECIMAL(6,2) NOT NULL DEFAULT 30.00,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                            ON UPDATE CURRENT_TIMESTAMP,
                        PRIMARY KEY (camera_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS foreign_object_rule (
                        camera_id BIGINT NOT NULL,
                        baseline_file VARCHAR(255) NOT NULL,
                        enabled TINYINT(1) NOT NULL DEFAULT 1,
                        dwell_seconds DECIMAL(5,2) NOT NULL DEFAULT 8.00,
                        min_area_ratio DECIMAL(7,5) NOT NULL DEFAULT 0.00500,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                            ON UPDATE CURRENT_TIMESTAMP,
                        PRIMARY KEY (camera_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS detection_event (
                        id BIGINT NOT NULL AUTO_INCREMENT,
                        alarm_id BIGINT NOT NULL,
                        camera_id BIGINT NOT NULL,
                        event_type VARCHAR(32) NOT NULL,
                        label VARCHAR(32) NOT NULL,
                        confidence DECIMAL(6,5) NULL,
                        snapshot_file VARCHAR(255) NULL,
                        review_status VARCHAR(16) NOT NULL DEFAULT 'pending',
                        review_reason VARCHAR(500) NULL,
                        reviewed_at DATETIME NULL,
                        linked_task_id BIGINT NULL,
                        track_id BIGINT NULL,
                        rule_type VARCHAR(32) NULL,
                        rule_name VARCHAR(64) NULL,
                        first_seen_at DATETIME NULL,
                        triggered_at DATETIME NULL,
                        duration_seconds DECIMAL(8,2) NULL,
                        model_version VARCHAR(128) NULL,
                        metadata_json TEXT NULL,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (id),
                        UNIQUE KEY uk_detection_event_alarm (alarm_id),
                        KEY idx_detection_event_camera_time (camera_id, created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
                # Upgrade the original event table in place without touching
                # historic alarms, recordings or task data.
                cursor.execute(
                    """
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = DATABASE() AND table_name = 'detection_event'
                    """
                )
                # PyMySQL normally returns dictionaries because DictCursor is
                # configured above.  Some local driver builds return tuples
                # for information_schema queries, so accept both shapes here.
                columns = {
                    next(iter(row.values())) if isinstance(row, dict) else row[0]
                    for row in cursor.fetchall()
                }
                additions = {
                    "review_status": "VARCHAR(16) NOT NULL DEFAULT 'pending'",
                    "review_reason": "VARCHAR(500) NULL",
                    "reviewed_at": "DATETIME NULL",
                    "linked_task_id": "BIGINT NULL",
                    "track_id": "BIGINT NULL",
                    "rule_type": "VARCHAR(32) NULL",
                    "rule_name": "VARCHAR(64) NULL",
                    "first_seen_at": "DATETIME NULL",
                    "triggered_at": "DATETIME NULL",
                    "duration_seconds": "DECIMAL(8,2) NULL",
                    "model_version": "VARCHAR(128) NULL",
                    "metadata_json": "TEXT NULL",
                }
                for name, definition in additions.items():
                    if name not in columns:
                        cursor.execute(f"ALTER TABLE detection_event ADD COLUMN {name} {definition}")

                cursor.execute(
                    """
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = DATABASE() AND table_name = 'detection_region'
                    """
                )
                region_columns = {
                    next(iter(row.values())) if isinstance(row, dict) else row[0]
                    for row in cursor.fetchall()
                }
                region_additions = {
                    "target_classes_json": "TEXT NULL",
                    "cooldown_seconds": "DECIMAL(6,2) NOT NULL DEFAULT 30.00",
                }
                for name, definition in region_additions.items():
                    if name not in region_columns:
                        cursor.execute(f"ALTER TABLE detection_region ADD COLUMN {name} {definition}")

    def health(self) -> bool:
        try:
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return cursor.fetchone() is not None
        except Exception as exc:  # pragma: no cover - depends on local DB
            LOGGER.warning("Database health check failed: %s", exc)
            return False

    def get_camera(self, camera_id: int) -> dict[str, Any] | None:
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, status, ip, username, password
                    FROM camera
                    WHERE id = %s
                    LIMIT 1
                    """,
                    (camera_id,),
                )
                row = cursor.fetchone()
        if not row or str(row.get("status")) != "0":
            return None
        return row

    def list_online_cameras(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, name, ip, status FROM camera WHERE status = '0' ORDER BY id"
                )
                return list(cursor.fetchall())

    def create_alarm(self, camera_id: int, label: str, confidence: float) -> int:
        display_name, alarm_type, level = CLASS_TEXT.get(label, (label, 1, 1))
        content = f"YOLO检测到{display_name}，最高置信度 {confidence:.1%}"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO alarm_info
                        (content, camera_id, type, deal_flag, create_time, level)
                    VALUES (%s, %s, %s, 0, NOW(), %s)
                    """,
                    (content, camera_id, alarm_type, level),
                )
                alarm_id = int(cursor.lastrowid)
        LOGGER.info(
            "Created real detection alarm: camera=%s label=%s confidence=%.3f",
            camera_id,
            label,
            confidence,
        )
        return alarm_id

    def create_region_intrusion_alarm(
        self,
        camera_id: int,
        rule: "RegionRule",
        label: str,
        track_id: int | None,
        confidence: float,
        dwell_seconds: float,
    ) -> int:
        display_name, alarm_type, level = CLASS_TEXT.get(label, (label, 1, 1))
        identity = f"#{track_id}" if track_id is not None else ""
        content = (
            f"{display_name}{identity}进入{rule.name}并持续{dwell_seconds:.1f}秒，"
            f"最高置信度 {confidence:.1%}"
        )
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO alarm_info
                        (content, camera_id, type, deal_flag, create_time, level)
                    VALUES (%s, %s, %s, 0, NOW(), %s)
                    """,
                    (content, camera_id, alarm_type, level),
                )
                alarm_id = int(cursor.lastrowid)
        LOGGER.warning(
            "Created zone intrusion alarm: camera=%s rule=%s track=%s confidence=%.3f",
            camera_id,
            rule.name,
            track_id,
            confidence,
        )
        return alarm_id

    def create_foreign_object_alarm(
        self, camera_id: int, rule: "ForeignObjectRule", confidence: float, dwell_seconds: float
    ) -> int:
        content = (
            f"{rule.dwell_seconds:.0f}秒基准场景比对发现新增静止物体，"
            f"持续{dwell_seconds:.1f}秒，变化置信度 {confidence:.1%}"
        )
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO alarm_info
                        (content, camera_id, type, deal_flag, create_time, level)
                    VALUES (%s, %s, 1, 0, NOW(), 1)
                    """,
                    (content, camera_id),
                )
                alarm_id = int(cursor.lastrowid)
        LOGGER.warning(
            "Created foreign-object alarm: camera=%s confidence=%.3f",
            camera_id,
            confidence,
        )
        return alarm_id

    def get_region(self, camera_id: int) -> "RegionRule | None":
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT camera_id, name, points_json, enabled, dwell_seconds,
                           target_classes_json, cooldown_seconds, updated_at
                    FROM detection_region
                    WHERE camera_id = %s
                    """,
                    (camera_id,),
                )
                row = cursor.fetchone()
        if not row:
            return None
        try:
            points = normalize_points(json.loads(row["points_json"]))
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            LOGGER.warning("Invalid stored region for camera %s: %s", camera_id, exc)
            return None
        target_classes = normalize_target_classes(row.get("target_classes_json"))
        return RegionRule(
            camera_id=int(row["camera_id"]),
            name=str(row["name"]),
            points=points,
            enabled=bool(row["enabled"]),
            dwell_seconds=float(row["dwell_seconds"]),
            target_classes=target_classes,
            cooldown_seconds=float(row.get("cooldown_seconds") or ALARM_COOLDOWN),
            updated_at=row["updated_at"].isoformat() if row.get("updated_at") else None,
        )

    def save_region(self, camera_id: int, payload: dict[str, Any]) -> "RegionRule":
        rule = RegionRule(
            camera_id=camera_id,
            name=str(payload.get("name") or "警戒区域").strip()[:64] or "警戒区域",
            points=normalize_points(payload.get("points")),
            enabled=bool(payload.get("enabled", True)),
            dwell_seconds=bounded_float(payload.get("dwellSeconds", 2), 0.5, 60.0),
            target_classes=normalize_target_classes(payload.get("targetClasses", ["person"])),
            cooldown_seconds=bounded_float(
                payload.get("cooldownSeconds", ALARM_COOLDOWN), 0.0, 600.0
            ),
        )
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO detection_region
                        (camera_id, name, points_json, enabled, dwell_seconds,
                         target_classes_json, cooldown_seconds)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        name = VALUES(name),
                        points_json = VALUES(points_json),
                        enabled = VALUES(enabled),
                        dwell_seconds = VALUES(dwell_seconds),
                        target_classes_json = VALUES(target_classes_json),
                        cooldown_seconds = VALUES(cooldown_seconds)
                    """,
                    (
                        rule.camera_id,
                        rule.name,
                        json.dumps(rule.points, ensure_ascii=False),
                        int(rule.enabled),
                        rule.dwell_seconds,
                        json.dumps(rule.target_classes, ensure_ascii=False),
                        rule.cooldown_seconds,
                    ),
                )
        return self.get_region(camera_id) or rule

    def delete_region(self, camera_id: int) -> None:
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM detection_region WHERE camera_id = %s", (camera_id,))

    def create_detection_event(
        self,
        alarm_id: int,
        camera_id: int,
        event_type: str,
        label: str,
        confidence: float,
        snapshot_file: str | None,
        *,
        track_id: int | None = None,
        rule_name: str | None = None,
        first_seen_at: float | None = None,
        duration_seconds: float | None = None,
        model_version: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO detection_event
                        (alarm_id, camera_id, event_type, label, confidence, snapshot_file,
                         track_id, rule_type, rule_name, first_seen_at, triggered_at,
                         duration_seconds, model_version, metadata_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s)
                    """,
                    (
                        alarm_id,
                        camera_id,
                        event_type,
                        label,
                        confidence,
                        snapshot_file,
                        track_id,
                        event_type,
                        rule_name,
                        datetime.fromtimestamp(first_seen_at) if first_seen_at else None,
                        duration_seconds,
                        model_version,
                        json.dumps(metadata or {}, ensure_ascii=False),
                    ),
                )

    def list_recent_events(self, limit: int = 100) -> list[dict[str, Any]]:
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, alarm_id, camera_id, event_type, label, confidence,
                           snapshot_file, review_status, review_reason, reviewed_at,
                           linked_task_id, track_id, rule_type, rule_name,
                           first_seen_at, triggered_at, duration_seconds,
                           model_version, metadata_json, created_at
                    FROM detection_event
                    ORDER BY id DESC
                    LIMIT %s
                    """,
                    (min(max(int(limit), 1), 500),),
                )
                rows = list(cursor.fetchall())
        for row in rows:
            row["alarmId"] = int(row.pop("alarm_id"))
            row["cameraId"] = int(row.pop("camera_id"))
            row["eventType"] = row.pop("event_type")
            row["snapshotFile"] = row.pop("snapshot_file")
            row["reviewStatus"] = row.pop("review_status") or "pending"
            row["reviewReason"] = row.pop("review_reason")
            row["linkedTaskId"] = row.pop("linked_task_id")
            row["trackId"] = row.pop("track_id")
            row["ruleType"] = row.pop("rule_type")
            row["ruleName"] = row.pop("rule_name")
            row["durationSeconds"] = (
                float(row.pop("duration_seconds"))
                if row.get("duration_seconds") is not None
                else None
            )
            row["modelVersion"] = row.pop("model_version")
            metadata_json = row.pop("metadata_json")
            try:
                row["metadata"] = json.loads(metadata_json) if metadata_json else {}
            except (TypeError, json.JSONDecodeError):
                row["metadata"] = {}
            row["confidence"] = float(row["confidence"]) if row["confidence"] is not None else None
            if row.get("reviewed_at"):
                row["reviewedAt"] = row.pop("reviewed_at").isoformat()
            if row.get("first_seen_at"):
                row["firstSeenAt"] = row.pop("first_seen_at").isoformat()
            else:
                row.pop("first_seen_at", None)
            if row.get("triggered_at"):
                row["triggeredAt"] = row.pop("triggered_at").isoformat()
            else:
                row.pop("triggered_at", None)
            if row.get("created_at"):
                row["createdAt"] = row.pop("created_at").isoformat()
        return rows

    def review_event(self, event_id: int, status: str, reason: str | None) -> dict[str, Any]:
        if status not in {"confirmed", "rejected"}:
            raise ValueError("复核状态仅支持 confirmed 或 rejected")
        reason = (reason or "").strip() or None
        if reason and len(reason) > 500:
            raise ValueError("复核说明不能超过500字")
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE detection_event
                    SET review_status = %s, review_reason = %s, reviewed_at = NOW()
                    WHERE id = %s
                    """,
                    (status, reason, event_id),
                )
                if cursor.rowcount != 1:
                    raise ValueError("检测事件不存在")
        return {"id": event_id, "reviewStatus": status, "reviewReason": reason}

    def link_event_task(self, event_id: int, task_id: int) -> dict[str, int]:
        if task_id <= 0:
            raise ValueError("任务编号必须为正整数")
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE detection_event SET linked_task_id = %s WHERE id = %s",
                    (task_id, event_id),
                )
                if cursor.rowcount != 1:
                    raise ValueError("检测事件不存在")
        return {"id": event_id, "linkedTaskId": task_id}

    def get_foreign_object_rule(self, camera_id: int) -> "ForeignObjectRule | None":
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT camera_id, baseline_file, enabled, dwell_seconds,
                           min_area_ratio, updated_at
                    FROM foreign_object_rule
                    WHERE camera_id = %s
                    """,
                    (camera_id,),
                )
                row = cursor.fetchone()
        if not row:
            return None
        return ForeignObjectRule(
            camera_id=int(row["camera_id"]),
            baseline_file=str(row["baseline_file"]),
            enabled=bool(row["enabled"]),
            dwell_seconds=float(row["dwell_seconds"]),
            min_area_ratio=float(row["min_area_ratio"]),
            updated_at=row["updated_at"].isoformat() if row.get("updated_at") else None,
        )

    def save_foreign_object_rule(
        self,
        camera_id: int,
        baseline_file: str,
        payload: dict[str, Any],
    ) -> "ForeignObjectRule":
        enabled = bool(payload.get("enabled", True))
        dwell_seconds = bounded_float(payload.get("dwellSeconds", 8), 2.0, 300.0)
        min_area_ratio = bounded_float(payload.get("minAreaRatio", 0.005), 0.001, 0.25)
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO foreign_object_rule
                        (camera_id, baseline_file, enabled, dwell_seconds, min_area_ratio)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        baseline_file = VALUES(baseline_file),
                        enabled = VALUES(enabled),
                        dwell_seconds = VALUES(dwell_seconds),
                        min_area_ratio = VALUES(min_area_ratio)
                    """,
                    (camera_id, baseline_file, int(enabled), dwell_seconds, min_area_ratio),
                )
        return self.get_foreign_object_rule(camera_id)  # type: ignore[return-value]

    def delete_foreign_object_rule(self, camera_id: int) -> None:
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM foreign_object_rule WHERE camera_id = %s", (camera_id,))


@dataclass
class Detection:
    label: str
    confidence: float
    box: tuple[int, int, int, int]
    track_id: int | None = None


@dataclass
class TrackRuleState:
    track_id: int
    label: str
    entered_at: float
    last_seen_at: float
    confidence: float
    alarm_emitted: bool = False
    last_alarm_at: float = 0.0


@dataclass
class RegionRule:
    camera_id: int
    name: str
    points: list[dict[str, float]]
    enabled: bool
    dwell_seconds: float
    target_classes: list[str]
    cooldown_seconds: float
    updated_at: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "cameraId": self.camera_id,
            "name": self.name,
            "points": self.points,
            "enabled": self.enabled,
            "dwellSeconds": self.dwell_seconds,
            "targetClasses": self.target_classes,
            "cooldownSeconds": self.cooldown_seconds,
            "updatedAt": self.updated_at,
        }


@dataclass
class ForeignObjectRule:
    camera_id: int
    baseline_file: str
    enabled: bool
    dwell_seconds: float
    min_area_ratio: float
    updated_at: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "cameraId": self.camera_id,
            "baselineReady": bool(self.baseline_file),
            "enabled": self.enabled,
            "dwellSeconds": self.dwell_seconds,
            "minAreaRatio": self.min_area_ratio,
            "updatedAt": self.updated_at,
        }


def bounded_float(value: Any, minimum: float, maximum: float) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        result = minimum
    return min(max(result, minimum), maximum)


def normalize_target_classes(value: Any) -> list[str]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            value = [item.strip() for item in value.split(",")]
    if not isinstance(value, list):
        value = ["person"]
    allowed = {"person", "car"}
    result = [str(item).strip().lower() for item in value if str(item).strip().lower() in allowed]
    return list(dict.fromkeys(result)) or ["person"]


def normalize_points(value: Any) -> list[dict[str, float]]:
    if not isinstance(value, list) or not 3 <= len(value) <= 20:
        raise ValueError("A region must contain 3 to 20 points")
    points: list[dict[str, float]] = []
    for point in value:
        if not isinstance(point, dict):
            raise ValueError("Invalid region point")
        x = bounded_float(point.get("x"), 0.0, 1.0)
        y = bounded_float(point.get("y"), 0.0, 1.0)
        if not 0.0 <= x <= 1.0 or not 0.0 <= y <= 1.0:
            raise ValueError("Region coordinates must be normalized")
        points.append({"x": round(x, 6), "y": round(y, 6)})
    return points


def create_tracker():
    """Create an isolated ByteTrack instance for one camera worker."""
    try:
        from ultralytics.trackers.byte_tracker import BYTETracker

        args = SimpleNamespace(
            tracker_type="bytetrack",
            track_high_thresh=TRACK_HIGH_THRESHOLD,
            track_low_thresh=TRACK_LOW_THRESHOLD,
            new_track_thresh=TRACK_HIGH_THRESHOLD,
            track_buffer=TRACK_BUFFER,
            match_thresh=TRACK_MATCH_THRESHOLD,
            fuse_score=True,
        )
        return BYTETracker(args)
    except Exception as exc:
        LOGGER.exception("Unable to initialize ByteTrack; detections will have no stable IDs: %s", exc)
        return None


class ModelRuntime:
    def __init__(self) -> None:
        self.model = None
        self.error: str | None = None
        self.names: dict[int, str] = {}
        self.lock = threading.Lock()
        self.model_path = Path(os.getenv("DETECTION_MODEL_PATH", DEFAULT_MODEL_PATH))
        self.device = "cpu"
        self.device_name = "CPU"
        self.half = False
        self.model_version = self.model_path.name
        self.strategy = os.getenv("DETECTION_STRATEGY", "full640").strip()
        self._load()

    def _load(self) -> None:
        try:
            import torch
            from ultralytics import YOLO

            if self.strategy not in STRATEGIES:
                raise ValueError(f"Invalid DETECTION_STRATEGY: {self.strategy}")

            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            requested = DEVICE_REQUEST
            cuda_ready = bool(torch.cuda.is_available())
            if requested == "auto":
                self.device = "cuda:0" if cuda_ready else "cpu"
            elif requested.startswith("cuda") and not cuda_ready:
                LOGGER.warning("CUDA was requested but is unavailable; falling back to CPU")
                self.device = "cpu"
            else:
                self.device = requested
            self.half = self.device.startswith("cuda")
            if self.half:
                self.device_name = torch.cuda.get_device_name(0)
            else:
                self.device_name = "CPU"
            self.model = YOLO(str(self.model_path))
            self.model.to(self.device)
            raw_names = getattr(self.model, "names", {})
            if isinstance(raw_names, list):
                self.names = {index: value for index, value in enumerate(raw_names)}
            else:
                self.names = {int(key): str(value) for key, value in raw_names.items()}
            stat = self.model_path.stat()
            self.model_version = f"{self.model_path.name}-{stat.st_size}-{stat.st_mtime_ns}"
            LOGGER.info(
                "Loaded YOLO model %s on %s with classes %s",
                self.model_path.name,
                self.device_name,
                list(self.names.values()),
            )
        except Exception as exc:
            self.error = str(exc)
            LOGGER.exception("Unable to load YOLO model")

    @property
    def ready(self) -> bool:
        return self.model is not None and self.error is None

    def predict(self, frame: np.ndarray, tracker=None) -> list[Detection]:
        if not self.ready:
            return []
        with self.lock:
            boxes = predict_boxes(self.model, frame, self.strategy, CONFIDENCE,
                                  self.device, self.half)
        detections: list[Detection] = []
        if tracker is not None:
            tracked = tracker.update(boxes, frame)
            for row in tracked.tolist() if hasattr(tracked, "tolist") else tracked:
                if len(row) < 7:
                    continue
                x1, y1, x2, y2, track_id, score, class_id = row[:7]
                label = self.names.get(int(class_id), str(int(class_id))).lower()
                detections.append(
                    Detection(
                        label=label,
                        confidence=float(score),
                        box=(int(x1), int(y1), int(x2), int(y2)),
                        track_id=int(track_id),
                    )
                )
            return detections
        for xyxy, score, class_id in zip(
            boxes.xyxy.tolist(),
            boxes.conf.tolist(),
            boxes.cls.tolist(),
        ):
            label = self.names.get(int(class_id), str(int(class_id))).lower()
            detections.append(
                Detection(
                    label=label,
                    confidence=float(score),
                    box=tuple(int(value) for value in xyxy),
                    track_id=None,
                )
            )
        return detections


def make_rtsp_url(camera: dict[str, Any]) -> str:
    username = quote(str(camera.get("username") or ""), safe="")
    password = quote(str(camera.get("password") or ""), safe="")
    credentials = f"{username}:{password}@" if username else ""
    return (
        f"rtsp://{credentials}{camera['ip']}:{RTSP_PORT}/cam/realmonitor"
        f"?channel=1&subtype={RTSP_SUBTYPE}"
    )


def draw_detections(frame: np.ndarray, detections: list[Detection]) -> np.ndarray:
    for detection in detections:
        x1, y1, x2, y2 = detection.box
        color = (40, 190, 80) if detection.label == "person" else (30, 150, 240)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        identity = f" #{detection.track_id}" if detection.track_id is not None else ""
        caption = f"{detection.label}{identity} {detection.confidence:.0%}"
        cv2.putText(
            frame,
            caption,
            (x1, max(y1 - 8, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            color,
            2,
            cv2.LINE_AA,
        )
    return frame


def region_polygon(rule: RegionRule, frame: np.ndarray) -> np.ndarray:
    height, width = frame.shape[:2]
    return np.array(
        [(round(point["x"] * width), round(point["y"] * height)) for point in rule.points],
        dtype=np.int32,
    )


def detection_in_region(detection: Detection, rule: RegionRule, frame: np.ndarray) -> bool:
    if detection.label not in rule.target_classes or not rule.enabled:
        return False
    x1, _y1, x2, y2 = detection.box
    foot_point = ((x1 + x2) // 2, y2)
    return cv2.pointPolygonTest(region_polygon(rule, frame), foot_point, False) >= 0


def draw_region(
    frame: np.ndarray,
    rule: RegionRule | None,
    intrusion_active: bool,
) -> np.ndarray:
    if rule is None or not rule.enabled:
        return frame
    polygon = region_polygon(rule, frame)
    overlay = frame.copy()
    color = (30, 30, 235) if intrusion_active else (0, 190, 245)
    cv2.fillPoly(overlay, [polygon], color)
    cv2.addWeighted(overlay, 0.16, frame, 0.84, 0, frame)
    cv2.polylines(frame, [polygon], True, color, 2, cv2.LINE_AA)
    x, y = polygon[0]
    cv2.putText(
        frame,
        f"ZONE: {rule.name}",
        (int(x), max(int(y) - 8, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        color,
        2,
        cv2.LINE_AA,
    )
    return frame


def baseline_scene_health(frame: np.ndarray, baseline: np.ndarray) -> tuple[bool, str | None]:
    if baseline.shape[:2] != frame.shape[:2]:
        return False, "画面尺寸已变化，请重新采集基准"
    current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    baseline_gray = cv2.cvtColor(baseline, cv2.COLOR_BGR2GRAY)
    brightness_delta = abs(float(current_gray.mean()) - float(baseline_gray.mean()))
    if brightness_delta > BASELINE_MAX_BRIGHTNESS_DELTA:
        return False, "现场亮度变化过大，请恢复光照或重新采集基准"
    try:
        shift, response = cv2.phaseCorrelate(
            np.float32(cv2.GaussianBlur(baseline_gray, (9, 9), 0)),
            np.float32(cv2.GaussianBlur(current_gray, (9, 9), 0)),
        )
        shift_ratio = max(abs(shift[0]) / max(frame.shape[1], 1), abs(shift[1]) / max(frame.shape[0], 1))
        if response >= 0.30 and shift_ratio > BASELINE_MAX_SHIFT_RATIO:
            return False, "摄像头机位疑似变化，请固定镜头后重新采集基准"
    except cv2.error:
        pass
    return True, None


def foreign_object_detections(
    frame: np.ndarray,
    baseline: np.ndarray,
    rule: ForeignObjectRule,
    region: RegionRule | None,
    ignored_detections: list[Detection] | None = None,
) -> list[Detection]:
    """Find persistent, newly changed areas in a captured baseline scene.

    This is intentionally a controlled-environment first version: it is only
    enabled after the operator captures an empty baseline and works best inside
    a user-drawn region.
    """
    if baseline.shape[:2] != frame.shape[:2]:
        baseline = cv2.resize(baseline, (frame.shape[1], frame.shape[0]))
    current_gray_raw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    baseline_gray = cv2.GaussianBlur(
        cv2.cvtColor(baseline, cv2.COLOR_BGR2GRAY), (5, 5), 0
    )
    brightness_offset = float(baseline_gray.mean()) - float(current_gray_raw.mean())
    current_gray = np.clip(
        current_gray_raw.astype(np.float32) + brightness_offset, 0, 255
    ).astype(np.uint8)
    current_gray = cv2.GaussianBlur(current_gray, (5, 5), 0)
    difference = cv2.absdiff(current_gray, baseline_gray)
    _, mask = cv2.threshold(difference, 35, 255, cv2.THRESH_BINARY)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8), iterations=2)

    if region and region.enabled:
        region_mask = np.zeros_like(mask)
        cv2.fillPoly(region_mask, [region_polygon(region, frame)], 255)
        mask = cv2.bitwise_and(mask, region_mask)

    for detection in ignored_detections or []:
        if detection.label not in {"person", "car"}:
            continue
        x1, y1, x2, y2 = detection.box
        margin_x = max(int((x2 - x1) * 0.08), 4)
        margin_y = max(int((y2 - y1) * 0.08), 4)
        cv2.rectangle(
            mask,
            (max(x1 - margin_x, 0), max(y1 - margin_y, 0)),
            (min(x2 + margin_x, frame.shape[1] - 1), min(y2 + margin_y, frame.shape[0] - 1)),
            0,
            thickness=-1,
        )

    minimum_area = frame.shape[0] * frame.shape[1] * rule.min_area_ratio
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    results: list[Detection] = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < minimum_area:
            continue
        x, y, width, height = cv2.boundingRect(contour)
        confidence = min(0.99, max(0.1, area / max(minimum_area * 2, 1)))
        results.append(
            Detection(
                label="foreign_object",
                confidence=float(confidence),
                box=(x, y, x + width, y + height),
            )
        )
    return results


def placeholder_frame(message: str) -> bytes:
    frame = np.zeros((480, 854, 3), dtype=np.uint8)
    cv2.putText(
        frame,
        message[:70],
        (30, 245),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (230, 230, 230),
        2,
        cv2.LINE_AA,
    )
    ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    return encoded.tobytes() if ok else b""


def save_evidence_snapshot(frame: np.ndarray, camera_id: int, event_type: str) -> str | None:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"camera_{camera_id}_{event_type}_{timestamp}_{time.time_ns() % 1_000_000}.jpg"
    target = EVIDENCE_DIR / filename
    try:
        ok = cv2.imwrite(
            str(target), frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
        )
        if not ok:
            raise RuntimeError("OpenCV could not encode evidence snapshot")
        return filename
    except Exception as exc:
        LOGGER.exception("Unable to save evidence snapshot: %s", exc)
        return None


class CameraWorker:
    def __init__(
        self,
        camera: dict[str, Any],
        repository: Repository,
        runtime: ModelRuntime,
    ) -> None:
        self.camera = camera
        self.repository = repository
        self.runtime = runtime
        self.camera_id = int(camera["id"])
        self.condition = threading.Condition()
        self.latest_jpeg = placeholder_frame("Connecting to camera...")
        self.connected = False
        self.last_error: str | None = None
        self.last_inference_at = 0.0
        self.last_frame_at = 0.0
        self.detections: list[Detection] = []
        self.tracker = create_tracker()
        self.object_alarm_tracks: dict[tuple[str, int], float] = {}
        self.last_class_alarm_at: dict[str, float] = {}
        self.region_rule: RegionRule | None = None
        self.region_loaded_at = 0.0
        self.region_track_states: dict[int, TrackRuleState] = {}
        self.foreign_rule: ForeignObjectRule | None = None
        self.foreign_loaded_at = 0.0
        self.foreign_baseline: np.ndarray | None = None
        self.foreign_detections: list[Detection] = []
        self.foreign_entered_at: float | None = None
        self.foreign_last_seen_at = 0.0
        self.foreign_alarm_emitted = False
        self.foreign_confidence = 0.0
        self.foreign_baseline_valid = True
        self.foreign_baseline_message: str | None = None
        self.video_fps = 0.0
        self.inference_fps = 0.0
        self.inference_ms = 0.0
        self._last_video_tick = 0.0
        self._last_inference_tick = 0.0
        self.inference_failed = False
        self.frame_lock = threading.Lock()
        self.latest_raw_frame: np.ndarray | None = None
        self.stop_event = threading.Event()
        self.thread = threading.Thread(
            target=self._run,
            name=f"camera-{self.camera_id}-detector",
            daemon=True,
        )
        self.thread.start()

    @staticmethod
    def _ema(previous: float, current: float, weight: float = 0.18) -> float:
        return current if previous <= 0 else previous * (1.0 - weight) + current * weight

    def _open_capture(self):
        os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", "rtsp_transport;tcp")
        capture = cv2.VideoCapture(make_rtsp_url(self.camera), cv2.CAP_FFMPEG)
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return capture

    def _publish(self, frame: np.ndarray) -> None:
        ok, encoded = cv2.imencode(
            ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
        )
        if not ok:
            return
        with self.condition:
            self.latest_jpeg = encoded.tobytes()
            self.last_frame_at = time.time()
            self.condition.notify_all()

    def _record_detection_event(
        self,
        alarm_id: int,
        event_type: str,
        label: str,
        confidence: float,
        frame: np.ndarray,
        detections: list[Detection],
        *,
        track_id: int | None = None,
        rule_name: str | None = None,
        first_seen_at: float | None = None,
        duration_seconds: float | None = None,
    ) -> None:
        evidence = draw_detections(frame.copy(), detections)
        evidence = draw_region(
            evidence,
            self.region_rule,
            event_type == "region_intrusion",
        )
        snapshot_file = save_evidence_snapshot(evidence, self.camera_id, event_type)
        metadata = {
            "device": self.runtime.device,
            "inferenceMs": round(self.inference_ms, 2),
            "videoFps": round(self.video_fps, 2),
            "inferenceFps": round(self.inference_fps, 2),
        }
        if event_type == "region_intrusion" and self.region_rule:
            metadata["region"] = self.region_rule.as_dict()
            metadata["regionDecision"] = "box_bottom_center"
        try:
            self.repository.create_detection_event(
                alarm_id,
                self.camera_id,
                event_type,
                label,
                confidence,
                snapshot_file,
                track_id=track_id,
                rule_name=rule_name,
                first_seen_at=first_seen_at,
                duration_seconds=duration_seconds,
                model_version=self.runtime.model_version,
                metadata=metadata,
            )
        except Exception as exc:
            LOGGER.exception("Failed to store detection event metadata: %s", exc)

    def _refresh_region_rule(self, now: float) -> None:
        if now - self.region_loaded_at < REGION_RULE_REFRESH_SECONDS:
            return
        self.region_loaded_at = now
        try:
            next_rule = self.repository.get_region(self.camera_id)
        except Exception as exc:
            LOGGER.warning("Unable to refresh region rule for camera %s: %s", self.camera_id, exc)
            return
        if (self.region_rule is None) != (next_rule is None) or (
            self.region_rule and next_rule and self.region_rule.updated_at != next_rule.updated_at
        ):
            self.region_track_states.clear()
        self.region_rule = next_rule

    def _refresh_foreign_rule(self, now: float) -> None:
        if now - self.foreign_loaded_at < REGION_RULE_REFRESH_SECONDS:
            return
        self.foreign_loaded_at = now
        try:
            next_rule = self.repository.get_foreign_object_rule(self.camera_id)
        except Exception as exc:
            LOGGER.warning("Unable to refresh foreign-object rule for camera %s: %s", self.camera_id, exc)
            return
        old_file = self.foreign_rule.baseline_file if self.foreign_rule else None
        next_file = next_rule.baseline_file if next_rule else None
        if next_file != old_file:
            self.foreign_baseline = None
            self.foreign_entered_at = None
            self.foreign_last_seen_at = 0.0
            self.foreign_alarm_emitted = False
            self.foreign_confidence = 0.0
            self.foreign_detections = []
            self.foreign_baseline_valid = True
            self.foreign_baseline_message = None
            if next_rule:
                candidate = BASELINE_DIR / Path(next_rule.baseline_file).name
                loaded = cv2.imread(str(candidate))
                if loaded is None:
                    LOGGER.warning("Baseline image unavailable for camera %s", self.camera_id)
                else:
                    self.foreign_baseline = loaded
        self.foreign_rule = next_rule

    def capture_foreign_object_baseline(self, payload: dict[str, Any]) -> ForeignObjectRule:
        with self.frame_lock:
            if self.latest_raw_frame is None:
                raise RuntimeError("当前尚无摄像头画面，无法采集基准场景")
            baseline = self.latest_raw_frame.copy()
        filename = f"camera_{self.camera_id}_baseline_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
        target = BASELINE_DIR / filename
        if not cv2.imwrite(str(target), baseline, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]):
            raise RuntimeError("基准场景保存失败")
        rule = self.repository.save_foreign_object_rule(self.camera_id, filename, payload)
        self.foreign_rule = rule
        self.foreign_baseline = baseline
        self.foreign_loaded_at = time.time()
        self.foreign_entered_at = None
        self.foreign_last_seen_at = 0.0
        self.foreign_alarm_emitted = False
        self.foreign_confidence = 0.0
        self.foreign_detections = []
        self.foreign_baseline_valid = True
        self.foreign_baseline_message = None
        return rule

    def _handle_foreign_object(self, frame: np.ndarray, now: float) -> None:
        rule = self.foreign_rule
        if rule is None or not rule.enabled or self.foreign_baseline is None:
            self.foreign_detections = []
            self.foreign_entered_at = None
            self.foreign_alarm_emitted = False
            self.foreign_baseline_valid = True
            self.foreign_baseline_message = None
            return
        baseline_valid, baseline_message = baseline_scene_health(frame, self.foreign_baseline)
        self.foreign_baseline_valid = baseline_valid
        self.foreign_baseline_message = baseline_message
        if not baseline_valid:
            self.foreign_detections = []
            self.foreign_entered_at = None
            self.foreign_alarm_emitted = False
            return
        self.foreign_detections = foreign_object_detections(
            frame,
            self.foreign_baseline,
            rule,
            self.region_rule,
            ignored_detections=self.detections,
        )
        if self.foreign_detections:
            self.foreign_last_seen_at = now
            self.foreign_confidence = max(item.confidence for item in self.foreign_detections)
            if self.foreign_entered_at is None:
                self.foreign_entered_at = now
                self.foreign_alarm_emitted = False
            dwell_elapsed = now - self.foreign_entered_at
            if not self.foreign_alarm_emitted and dwell_elapsed >= rule.dwell_seconds:
                try:
                    alarm_id = self.repository.create_foreign_object_alarm(
                        self.camera_id, rule, self.foreign_confidence, dwell_elapsed
                    )
                    self._record_detection_event(
                        alarm_id,
                        "foreign_object",
                        "foreign_object",
                        self.foreign_confidence,
                        frame,
                        self.detections + self.foreign_detections,
                        rule_name="固定机位基线比对",
                        first_seen_at=self.foreign_entered_at,
                        duration_seconds=dwell_elapsed,
                    )
                    self.foreign_alarm_emitted = True
                except Exception as exc:
                    LOGGER.exception("Failed to store foreign-object alarm: %s", exc)
            return
        if now - self.foreign_last_seen_at >= ABSENCE_RESET:
            self.foreign_entered_at = None
            self.foreign_alarm_emitted = False
            self.foreign_confidence = 0.0

    def _handle_region_intrusion(
        self, detections: list[Detection], frame: np.ndarray, now: float
    ) -> None:
        rule = self.region_rule
        if rule is None or not rule.enabled:
            self.region_track_states.clear()
            return
        active_ids: set[int] = set()
        for detection in detections:
            if not detection_in_region(detection, rule, frame):
                continue
            track_id = detection.track_id
            if track_id is None:
                track_id = -1 if detection.label == "person" else -2
            active_ids.add(track_id)
            state = self.region_track_states.get(track_id)
            if state is None or state.label != detection.label:
                state = TrackRuleState(
                    track_id=track_id,
                    label=detection.label,
                    entered_at=now,
                    last_seen_at=now,
                    confidence=detection.confidence,
                )
                self.region_track_states[track_id] = state
            else:
                state.last_seen_at = now
                state.confidence = max(state.confidence, detection.confidence)

            dwell_elapsed = now - state.entered_at
            cooldown_ready = now - state.last_alarm_at >= rule.cooldown_seconds
            if state.alarm_emitted or dwell_elapsed < rule.dwell_seconds or not cooldown_ready:
                continue
            try:
                alarm_id = self.repository.create_region_intrusion_alarm(
                    self.camera_id,
                    rule,
                    detection.label,
                    detection.track_id,
                    state.confidence,
                    dwell_elapsed,
                )
                self._record_detection_event(
                    alarm_id,
                    "region_intrusion",
                    detection.label,
                    state.confidence,
                    frame,
                    detections,
                    track_id=detection.track_id,
                    rule_name=rule.name,
                    first_seen_at=state.entered_at,
                    duration_seconds=dwell_elapsed,
                )
                state.alarm_emitted = True
                state.last_alarm_at = now
            except Exception as exc:
                LOGGER.exception("Failed to store region intrusion alarm: %s", exc)

        expired = [
            track_id
            for track_id, state in self.region_track_states.items()
            if track_id not in active_ids and now - state.last_seen_at >= ABSENCE_RESET
        ]
        for track_id in expired:
            self.region_track_states.pop(track_id, None)

    def _handle_alarms(
        self, detections: list[Detection], frame: np.ndarray, now: float
    ) -> None:
        self._handle_region_intrusion(detections, frame, now)
        if self.region_rule is not None:
            # A configured region governs this camera, including when it is suspended.
            self.object_alarm_tracks.clear()
            return
        for detection in detections:
            label = detection.label
            if label not in ALARM_CLASSES:
                continue
            track_id = detection.track_id if detection.track_id is not None else (-1 if label == "person" else -2)
            key = (label, track_id)
            was_present = key in self.object_alarm_tracks
            self.object_alarm_tracks[key] = now
            if was_present or now - self.last_class_alarm_at.get(label, 0.0) < ALARM_COOLDOWN:
                continue
            try:
                alarm_id = self.repository.create_alarm(self.camera_id, label, detection.confidence)
                self._record_detection_event(
                    alarm_id,
                    "object_detection",
                    label,
                    detection.confidence,
                    frame,
                    detections,
                    track_id=detection.track_id,
                    rule_name="目标出现",
                    first_seen_at=now,
                    duration_seconds=0.0,
                )
                self.last_class_alarm_at[label] = now
            except Exception as exc:
                LOGGER.exception("Failed to store detection alarm: %s", exc)

        expired = [key for key, last_seen in self.object_alarm_tracks.items() if now - last_seen >= ABSENCE_RESET]
        for key in expired:
            self.object_alarm_tracks.pop(key, None)

    def _run(self) -> None:
        while not self.stop_event.is_set():
            capture = None
            try:
                capture = self._open_capture()
                if not capture.isOpened():
                    raise RuntimeError("RTSP stream could not be opened")
                self.connected = True
                self.last_error = None
                LOGGER.info("Camera %s RTSP stream connected", self.camera_id)

                while not self.stop_event.is_set():
                    ok, frame = capture.read()
                    if not ok or frame is None:
                        raise RuntimeError("RTSP frame read failed")

                    now = time.time()
                    if self._last_video_tick > 0 and now > self._last_video_tick:
                        self.video_fps = self._ema(self.video_fps, 1.0 / (now - self._last_video_tick))
                    self._last_video_tick = now
                    with self.frame_lock:
                        self.latest_raw_frame = frame.copy()
                    if now - self.last_inference_at >= INFERENCE_INTERVAL:
                        self._refresh_region_rule(now)
                        self._refresh_foreign_rule(now)
                        inference_started = time.perf_counter()
                        try:
                            self.detections = self.runtime.predict(frame, self.tracker)
                        except Exception:
                            self.inference_failed = True
                            self.stop_event.set()
                            raise
                        inference_elapsed = max(time.perf_counter() - inference_started, 0.000001)
                        self.inference_ms = self._ema(self.inference_ms, inference_elapsed * 1000.0)
                        completed = time.perf_counter()
                        if self._last_inference_tick:
                            self.inference_fps = self._ema(
                                self.inference_fps, 1.0 / max(completed - self._last_inference_tick, 0.000001)
                            )
                        self._last_inference_tick = completed
                        self.last_inference_at = time.time()
                        self._handle_alarms(self.detections, frame, now)
                        self._handle_foreign_object(frame, now)

                    rendered = draw_detections(
                        frame.copy(), self.detections + self.foreign_detections
                    )
                    rendered = draw_region(
                        rendered,
                        self.region_rule,
                        bool(self.region_track_states),
                    )
                    status = (
                        f"YOLO {self.runtime.device} | tracks {sum(1 for item in self.detections if item.track_id is not None)}"
                        if self.runtime.ready
                        else "YOLO unavailable"
                    )
                    cv2.putText(
                        rendered,
                        status,
                        (16, rendered.shape[0] - 18),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.58,
                        (80, 220, 120) if self.runtime.ready else (40, 40, 240),
                        2,
                        cv2.LINE_AA,
                    )
                    self._publish(rendered)
            except Exception as exc:
                self.connected = False
                self.last_error = str(exc)
                LOGGER.warning("Camera %s: %s", self.camera_id, exc)
                with self.condition:
                    self.latest_jpeg = placeholder_frame(
                        f"Camera {self.camera_id}: detection failed; restart task" if self.inference_failed
                        else f"Camera {self.camera_id}: reconnecting..."
                    )
                    self.condition.notify_all()
                self.stop_event.wait(2.0)
            finally:
                if capture is not None:
                    capture.release()

    def frames(self):
        while not self.stop_event.is_set():
            with self.condition:
                self.condition.wait(timeout=1.0)
                jpeg = self.latest_jpeg
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"

    def status(self) -> dict[str, Any]:
        if self.inference_failed:
            state = "failed"
        elif self.stop_event.is_set():
            state = "stopping"
        elif self.connected:
            state = "running"
        elif self.last_error:
            state = "reconnecting"
        else:
            state = "connecting"
        now = time.time()
        region_dwell = max(
            (now - item.entered_at for item in self.region_track_states.values()),
            default=0.0,
        )
        return {
            "cameraId": self.camera_id,
            "state": state,
            "connected": self.connected,
            "lastError": self.last_error,
            "lastFrameAt": self.last_frame_at or None,
            "region": self.region_rule.as_dict() if self.region_rule else None,
            "inRestrictedRegion": bool(self.region_track_states),
            "regionDwellSeconds": round(region_dwell, 2),
            "regionTrackCount": len(self.region_track_states),
            "foreignObjectRule": self.foreign_rule.as_dict() if self.foreign_rule else None,
            "foreignObjectPresent": self.foreign_entered_at is not None,
            "foreignBaselineValid": self.foreign_baseline_valid,
            "foreignBaselineMessage": self.foreign_baseline_message,
            "foreignObjectDwellSeconds": (
                round(time.time() - self.foreign_entered_at, 2)
                if self.foreign_entered_at is not None
                else 0
            ),
            "performance": {
                "strategy": self.runtime.strategy,
                "inputSize": STRATEGIES.get(self.runtime.strategy),
                "device": self.runtime.device,
                "deviceName": self.runtime.device_name,
                "halfPrecision": self.runtime.half,
                "videoFps": round(self.video_fps, 2),
                "inferenceFps": round(self.inference_fps, 2),
                "inferenceMs": round(self.inference_ms, 2),
                "trackCount": sum(1 for item in self.detections if item.track_id is not None),
            },
            "detections": [
                {
                    "label": item.label,
                    "confidence": round(item.confidence, 4),
                    "box": item.box,
                    "trackId": item.track_id,
                }
                for item in self.detections
            ],
        }

    def stop(self) -> None:
        self.stop_event.set()
        with self.condition:
            self.condition.notify_all()


repository = Repository()
runtime = ModelRuntime()
workers: dict[int, CameraWorker] = {}
workers_lock = threading.Lock()

app = Flask(__name__)
# The service is intentionally bound to 127.0.0.1 by default.  Keep the
# browser allowance equally narrow: Vue's development proxy is the supported
# entry point, rather than exposing the detector as a general LAN API.
CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:8080", "http://127.0.0.1:8080"]}},
)


def start_worker(camera_id: int) -> tuple[CameraWorker, bool]:
    if not runtime.ready:
        raise RuntimeError(f"识别服务未就绪：{runtime.error or '模型尚未加载'}")
    with workers_lock:
        worker = workers.get(camera_id)
        if worker:
            if worker.inference_failed:
                raise RuntimeError("检测任务已失败，请先停止任务，再检查配置并重新启动")
            return worker, False
        camera = repository.get_camera(camera_id)
        if camera is None:
            raise LookupError("Camera does not exist or is offline")
        worker = CameraWorker(camera, repository, runtime)
        workers[camera_id] = worker
        return worker, True


def get_active_worker(camera_id: int) -> CameraWorker:
    with workers_lock:
        worker = workers.get(camera_id)
    if worker is None:
        raise RuntimeError("检测任务尚未启动，请先点击“启动检测”")
    return worker


@app.get("/")
def index():
    return jsonify(
        {
            "service": "station-monitoring-yolo",
            "health": "/health",
            "stream": "/video_feed/{cameraId}",
        }
    )


@app.get("/health")
def health():
    database_ready = repository.health()
    status_code = 200 if runtime.ready and database_ready else 503
    return (
        jsonify(
            {
                "success": status_code == 200,
                "modelReady": runtime.ready,
                "model": runtime.model_path.name,
                "modelVersion": runtime.model_version,
                "modelClasses": list(runtime.names.values()),
                "modelError": runtime.error,
                "device": runtime.device,
                "deviceName": runtime.device_name,
                "halfPrecision": runtime.half,
                "tracking": "ByteTrack" if runtime.ready else None,
                "databaseReady": database_ready,
                "activeCameras": len(workers),
                "confidence": CONFIDENCE,
                "strategy": runtime.strategy,
                "inputSize": STRATEGIES.get(runtime.strategy),
            }
        ),
        status_code,
    )


@app.get("/cameras")
def cameras():
    try:
        return jsonify({"success": True, "data": repository.list_online_cameras()})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.get("/cameras/<int:camera_id>/status")
def camera_status(camera_id: int):
    with workers_lock:
        worker = workers.get(camera_id)
    if worker is None:
        return jsonify({"cameraId": camera_id, "connected": False, "started": False})
    return jsonify({"started": True, **worker.status()})


@app.post("/cameras/<int:camera_id>/start")
def start_camera(camera_id: int):
    try:
        worker, created = start_worker(camera_id)
        return jsonify({"success": True, "created": created, "data": {"started": True, **worker.status()}})
    except LookupError as exc:
        return jsonify({"success": False, "message": str(exc)}), 404
    except Exception as exc:
        LOGGER.exception("Unable to start camera %s", camera_id)
        return jsonify({"success": False, "message": str(exc)}), 500


@app.get("/regions/<int:camera_id>")
def get_region(camera_id: int):
    try:
        rule = repository.get_region(camera_id)
        return jsonify({"success": True, "data": rule.as_dict() if rule else None})
    except Exception as exc:
        LOGGER.exception("Unable to fetch region for camera %s", camera_id)
        return jsonify({"success": False, "message": str(exc)}), 500


@app.put("/regions/<int:camera_id>")
def save_region(camera_id: int):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"success": False, "message": "请求体必须是JSON对象"}), 400
    try:
        rule = repository.save_region(camera_id, payload)
        with workers_lock:
            worker = workers.get(camera_id)
        if worker:
            worker.region_loaded_at = 0.0
        return jsonify({"success": True, "data": rule.as_dict()})
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception as exc:
        LOGGER.exception("Unable to save region for camera %s", camera_id)
        return jsonify({"success": False, "message": str(exc)}), 500


@app.delete("/regions/<int:camera_id>")
def delete_region(camera_id: int):
    try:
        repository.delete_region(camera_id)
        with workers_lock:
            worker = workers.get(camera_id)
        if worker:
            worker.region_loaded_at = 0.0
        return jsonify({"success": True})
    except Exception as exc:
        LOGGER.exception("Unable to delete region for camera %s", camera_id)
        return jsonify({"success": False, "message": str(exc)}), 500


@app.get("/foreign-object/<int:camera_id>")
def get_foreign_object_rule(camera_id: int):
    try:
        rule = repository.get_foreign_object_rule(camera_id)
        return jsonify({"success": True, "data": rule.as_dict() if rule else None})
    except Exception as exc:
        LOGGER.exception("Unable to fetch foreign-object rule for camera %s", camera_id)
        return jsonify({"success": False, "message": str(exc)}), 500


@app.post("/foreign-object/<int:camera_id>/baseline")
def capture_foreign_object_baseline(camera_id: int):
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({"success": False, "message": "请求体必须是JSON对象"}), 400
    try:
        worker = get_active_worker(camera_id)
        rule = worker.capture_foreign_object_baseline(payload)
        return jsonify({"success": True, "data": rule.as_dict()})
    except RuntimeError as exc:
        return jsonify({"success": False, "message": str(exc)}), 409
    except Exception as exc:
        LOGGER.exception("Unable to capture foreign-object baseline for camera %s", camera_id)
        return jsonify({"success": False, "message": str(exc)}), 500


@app.delete("/foreign-object/<int:camera_id>")
def delete_foreign_object_rule(camera_id: int):
    try:
        repository.delete_foreign_object_rule(camera_id)
        with workers_lock:
            worker = workers.get(camera_id)
        if worker:
            worker.foreign_rule = None
            worker.foreign_baseline = None
            worker.foreign_detections = []
            worker.foreign_entered_at = None
            worker.foreign_alarm_emitted = False
            worker.foreign_loaded_at = time.time()
            worker.foreign_baseline_valid = True
            worker.foreign_baseline_message = None
        return jsonify({"success": True})
    except Exception as exc:
        LOGGER.exception("Unable to delete foreign-object rule for camera %s", camera_id)
        return jsonify({"success": False, "message": str(exc)}), 500


@app.get("/events")
def events():
    try:
        limit = request.args.get("limit", default=100, type=int)
        return jsonify({"success": True, "data": repository.list_recent_events(limit)})
    except Exception as exc:
        LOGGER.exception("Unable to fetch detection events")
        return jsonify({"success": False, "message": str(exc)}), 500


@app.patch("/events/<int:event_id>/review")
def review_event(event_id: int):
    try:
        payload = request.get_json(silent=True) or {}
        data = repository.review_event(
            event_id,
            str(payload.get("status", "")),
            payload.get("reason"),
        )
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception as exc:
        LOGGER.exception("Unable to review detection event %s", event_id)
        return jsonify({"success": False, "message": str(exc)}), 500


@app.post("/events/<int:event_id>/task")
def link_event_task(event_id: int):
    try:
        payload = request.get_json(silent=True) or {}
        task_id = int(payload.get("taskId", 0))
        data = repository.link_event_task(event_id, task_id)
        return jsonify({"success": True, "data": data})
    except (TypeError, ValueError) as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception as exc:
        LOGGER.exception("Unable to link detection event %s to task", event_id)
        return jsonify({"success": False, "message": str(exc)}), 500


@app.get("/evidence/<path:filename>")
def evidence(filename: str):
    return send_from_directory(EVIDENCE_DIR, filename, conditional=True, max_age=0)


@app.get("/video_feed/<int:camera_id>")
def video_feed(camera_id: int):
    try:
        worker = get_active_worker(camera_id)
    except RuntimeError as exc:
        return jsonify({"success": False, "message": str(exc)}), 409
    except Exception as exc:
        LOGGER.exception("Unable to start camera %s", camera_id)
        return jsonify({"success": False, "message": str(exc)}), 500
    return Response(
        worker.frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )


@app.post("/cameras/<int:camera_id>/stop")
def stop_camera(camera_id: int):
    with workers_lock:
        worker = workers.pop(camera_id, None)
    if worker:
        worker.stop()
    return jsonify({"success": True})


def shutdown_workers() -> None:
    with workers_lock:
        current_workers = list(workers.values())
        workers.clear()
    for worker in current_workers:
        worker.stop()


atexit.register(shutdown_workers)


def main() -> None:
    host = os.getenv("DETECTION_HOST", "127.0.0.1")
    port = env_int("DETECTION_PORT", 5000)
    app.run(host=host, port=port, threaded=True, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
