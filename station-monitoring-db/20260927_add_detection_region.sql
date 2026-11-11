-- 人工智能检测规则：每台摄像头保存一个可绘制的多边形警戒区域。
-- detection_service.py 启动时也会以 CREATE TABLE IF NOT EXISTS 自动保障此表存在。
CREATE TABLE IF NOT EXISTS detection_region (
    camera_id BIGINT NOT NULL,
    name VARCHAR(64) NOT NULL DEFAULT '警戒区域',
    points_json TEXT NOT NULL,
    enabled TINYINT(1) NOT NULL DEFAULT 1,
    dwell_seconds DECIMAL(5,2) NOT NULL DEFAULT 2.00,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (camera_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 受控演示场景下的新增静止物体（异物遗留）基准图与阈值规则。
CREATE TABLE IF NOT EXISTS foreign_object_rule (
    camera_id BIGINT NOT NULL,
    baseline_file VARCHAR(255) NOT NULL,
    enabled TINYINT(1) NOT NULL DEFAULT 1,
    dwell_seconds DECIMAL(5,2) NOT NULL DEFAULT 8.00,
    min_area_ratio DECIMAL(7,5) NOT NULL DEFAULT 0.00500,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (camera_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 算法检测事件与告警证据截图。
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
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_detection_event_alarm (alarm_id),
    KEY idx_detection_event_camera_time (camera_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 旧版 detection_event 已存在时，由 detection_service.py 在启动时按列补齐。
-- 本文件用于新数据库初始化；不删除任何历史告警或任务。
