package com.zzy.sms.stationmonitoringbanckend.controller;

import org.springframework.data.redis.connection.RedisConnection;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.Statement;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 演示环境健康检查。只返回组件可用性，不返回连接地址、账号或其他敏感配置。
 */
@RestController
public class HealthController {

    private final DataSource dataSource;
    private final RedisConnectionFactory redisConnectionFactory;

    public HealthController(DataSource dataSource, RedisConnectionFactory redisConnectionFactory) {
        this.dataSource = dataSource;
        this.redisConnectionFactory = redisConnectionFactory;
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> body = new LinkedHashMap<>();
        boolean databaseReady = isDatabaseReady();
        boolean redisReady = isRedisReady();
        boolean recordingDirectoryReady = isRecordingDirectoryReady();
        boolean ready = databaseReady && redisReady && recordingDirectoryReady;

        body.put("status", ready ? "UP" : "DEGRADED");
        body.put("database", databaseReady ? "UP" : "DOWN");
        body.put("redis", redisReady ? "UP" : "DOWN");
        body.put("recordingDirectory", recordingDirectoryReady ? "UP" : "DOWN");
        return ResponseEntity.status(ready ? 200 : 503).body(body);
    }

    private boolean isDatabaseReady() {
        try (Connection connection = dataSource.getConnection(); Statement statement = connection.createStatement()) {
            statement.execute("SELECT 1");
            return true;
        } catch (Exception ignored) {
            return false;
        }
    }

    private boolean isRedisReady() {
        try (RedisConnection connection = redisConnectionFactory.getConnection()) {
            return connection.ping() != null;
        } catch (Exception ignored) {
            return false;
        }
    }

    private boolean isRecordingDirectoryReady() {
        try {
            Path directory = Paths.get("recordings").toAbsolutePath().normalize();
            Files.createDirectories(directory);
            return Files.isDirectory(directory) && Files.isWritable(directory);
        } catch (Exception ignored) {
            return false;
        }
    }
}
