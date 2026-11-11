-- 手动录像索引：让录像可按摄像头、录制时段检索，并可定位覆盖告警时刻的录像。
-- 应用启动后的 RecordingController 也会执行同样的 CREATE TABLE IF NOT EXISTS，
-- 此文件用于需要手工初始化数据库的演示环境。
CREATE TABLE IF NOT EXISTS recording_index (
    id BIGINT NOT NULL AUTO_INCREMENT,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NULL,
    camera_id BIGINT NULL,
    started_at DATETIME NULL,
    ended_at DATETIME NULL,
    source VARCHAR(32) NOT NULL DEFAULT 'manual',
    size_bytes BIGINT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_recording_filename (filename),
    KEY idx_recording_camera_time (camera_id, started_at, ended_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
