package com.zzy.sms.stationmonitoringbanckend.controller;

import cn.dev33.satoken.stp.StpUtil;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody;

import javax.sql.DataSource;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

/**
 * 录像管理：文件保存在 recordings/，录像索引保存来源、摄像头和录制起止时间。
 * 未进入索引的既有文件仍可播放，并明确标为“历史录像”。
 */
@RestController
@RequestMapping("/recording")
public class RecordingController {

    private static final String RECORDING_DIR = "recordings/";
    private static final long MAX_UPLOAD_SIZE_BYTES = 200L * 1024 * 1024;
    private static final int STREAM_BUFFER_SIZE = 64 * 1024;
    private static final Set<String> REVIEW_OUTCOMES = Set.of("visible", "misread", "unclear");
    private final DataSource dataSource;
    private volatile boolean schemaReady = false;
    private volatile boolean reviewSchemaReady = false;

    public RecordingController(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    private Path dir() throws java.io.IOException {
        Path dir = Paths.get(RECORDING_DIR).toAbsolutePath().normalize();
        Files.createDirectories(dir);
        return dir;
    }

    private Path resolveSafe(String filename) throws java.io.IOException {
        if (filename == null || filename.contains("..") || filename.contains("/") || filename.contains("\\")) {
            throw new IllegalArgumentException("非法文件名");
        }
        return dir().resolve(filename).normalize();
    }

    private synchronized void ensureSchema() throws SQLException {
        if (schemaReady) return;
        try (Connection connection = dataSource.getConnection(); Statement statement = connection.createStatement()) {
            statement.execute(
                    "CREATE TABLE IF NOT EXISTS recording_index (" +
                            "id BIGINT NOT NULL AUTO_INCREMENT," +
                            "filename VARCHAR(255) NOT NULL," +
                            "original_name VARCHAR(255) NULL," +
                            "camera_id BIGINT NULL," +
                            "started_at DATETIME NULL," +
                            "ended_at DATETIME NULL," +
                            "source VARCHAR(32) NOT NULL DEFAULT 'manual'," +
                            "size_bytes BIGINT NOT NULL DEFAULT 0," +
                            "created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP," +
                            "PRIMARY KEY (id), UNIQUE KEY uk_recording_filename (filename)," +
                            "KEY idx_recording_camera_time (camera_id, started_at, ended_at)" +
                            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            );
            schemaReady = true;
        }
    }

    private Timestamp parseTime(String value, String fieldName) {
        if (value == null || value.isBlank()) return null;
        try {
            return Timestamp.from(Instant.parse(value));
        } catch (Exception ignored) {
            try {
                return Timestamp.valueOf(LocalDateTime.parse(value, DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            } catch (Exception ex) {
                throw new IllegalArgumentException(fieldName + "必须为 ISO-8601 时间");
            }
        }
    }

    private String normalizeSource(String value) {
        return "import".equals(value) ? "import" : "manual";
    }

    private boolean isSupportedVideo(String filename, String contentType) {
        if (filename == null) return false;
        String lower = filename.toLowerCase();
        if (!(lower.endsWith(".mp4") || lower.endsWith(".webm") || lower.endsWith(".avi")
                || lower.endsWith(".mov") || lower.endsWith(".mkv") || lower.endsWith(".wmv")
                || lower.endsWith(".flv") || lower.endsWith(".mpg") || lower.endsWith(".mpeg"))) return false;
        return contentType == null || contentType.isBlank()
                || contentType.startsWith("video/")
                || "application/octet-stream".equalsIgnoreCase(contentType);
    }

    private String ffmpegExecutable() {
        String configured = System.getenv("RAIL_FFMPEG_PATH");
        if (configured != null && !configured.isBlank()) return configured;
        Path supplied = Paths.get("D:/AAA空信242/视频转码助手/core/ffmpeg.exe");
        return Files.isRegularFile(supplied) ? supplied.toString() : "ffmpeg";
    }

    private void convertForBrowser(Path input, Path output) throws Exception {
        Path log = Files.createTempFile(Files.createDirectories(dir().resolve(".transcoding")), "ffmpeg-", ".log");
        try {
            Process process = new ProcessBuilder(ffmpegExecutable(), "-nostdin", "-hide_banner", "-loglevel", "error",
                    "-i", input.toString(), "-map", "0:v:0", "-map", "0:a:0?",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "23",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-f", "mp4", "-y", output.toString())
                    .redirectErrorStream(true).redirectOutput(log.toFile()).start();
            if (!process.waitFor(180, TimeUnit.SECONDS)) {
                process.destroyForcibly();
                throw new IllegalArgumentException("视频转码超时，请截取较短片段后重试");
            }
            if (process.exitValue() != 0 || !Files.isRegularFile(output) || Files.size(output) == 0)
                throw new IllegalArgumentException("视频无法转成浏览器可播放的 MP4，请检查源文件是否完整");
        } finally { Files.deleteIfExists(log); }
    }

    private StreamingResponseBody streamFile(Path path, long start, long length) {
        return outputStream -> {
            try (FileChannel channel = FileChannel.open(path, StandardOpenOption.READ)) {
                channel.position(start);
                ByteBuffer buffer = ByteBuffer.allocate(STREAM_BUFFER_SIZE);
                long remaining = length;
                while (remaining > 0) {
                    buffer.clear();
                    buffer.limit((int) Math.min(buffer.capacity(), remaining));
                    int read = channel.read(buffer);
                    if (read < 0) break;
                    outputStream.write(buffer.array(), 0, read);
                    remaining -= read;
                }
                outputStream.flush();
            }
        };
    }

    private Map<String, Object> toIndexMap(ResultSet rs) throws SQLException {
        Map<String, Object> item = new HashMap<>();
        item.put("id", rs.getLong("id"));
        item.put("filename", rs.getString("filename"));
        item.put("originalName", rs.getString("original_name"));
        long cameraId = rs.getLong("camera_id");
        item.put("cameraId", rs.wasNull() ? null : cameraId);
        Timestamp startedAt = rs.getTimestamp("started_at");
        Timestamp endedAt = rs.getTimestamp("ended_at");
        item.put("startedAt", startedAt == null ? null : startedAt.toInstant().toString());
        item.put("endedAt", endedAt == null ? null : endedAt.toInstant().toString());
        item.put("source", rs.getString("source"));
        item.put("size", rs.getLong("size_bytes"));
        return item;
    }

    private void saveIndex(String filename, String originalName, Long cameraId,
                           Timestamp startedAt, Timestamp endedAt, String source, long size) throws SQLException {
        ensureSchema();
        if (startedAt != null && endedAt != null && endedAt.before(startedAt)) {
            throw new IllegalArgumentException("结束时间不能早于开始时间");
        }
        String sql = "INSERT INTO recording_index " +
                "(filename, original_name, camera_id, started_at, ended_at, source, size_bytes) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE " +
                "original_name=VALUES(original_name), camera_id=VALUES(camera_id), " +
                "started_at=VALUES(started_at), ended_at=VALUES(ended_at), " +
                "source=VALUES(source), size_bytes=VALUES(size_bytes)";
        try (Connection connection = dataSource.getConnection(); PreparedStatement ps = connection.prepareStatement(sql)) {
            ps.setString(1, filename);
            ps.setString(2, originalName);
            if (cameraId == null) ps.setNull(3, java.sql.Types.BIGINT); else ps.setLong(3, cameraId);
            if (startedAt == null) ps.setNull(4, java.sql.Types.TIMESTAMP); else ps.setTimestamp(4, startedAt);
            if (endedAt == null) ps.setNull(5, java.sql.Types.TIMESTAMP); else ps.setTimestamp(5, endedAt);
            ps.setString(6, source);
            ps.setLong(7, size);
            ps.executeUpdate();
        }
    }

    private Map<String, Map<String, Object>> getIndexes() throws SQLException {
        ensureSchema();
        Map<String, Map<String, Object>> indexes = new HashMap<>();
        try (Connection connection = dataSource.getConnection();
             PreparedStatement ps = connection.prepareStatement("SELECT * FROM recording_index");
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                Map<String, Object> item = toIndexMap(rs);
                indexes.put((String) item.get("filename"), item);
            }
        }
        return indexes;
    }

    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> upload(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "cameraId", required = false) Long cameraId,
            @RequestParam(value = "startedAt", required = false) String startedAt,
            @RequestParam(value = "endedAt", required = false) String endedAt,
            @RequestParam(value = "source", required = false) String source) {
        Map<String, Object> result = new HashMap<>();
        if (file == null || file.isEmpty()) {
            result.put("success", false);
            result.put("msg", "文件为空");
            return ResponseEntity.badRequest().body(result);
        }
        if (file.getSize() > MAX_UPLOAD_SIZE_BYTES) {
            result.put("success", false);
            result.put("msg", "录像超过 200 MB 上传限制");
            return ResponseEntity.status(HttpStatus.PAYLOAD_TOO_LARGE).body(result);
        }
        if (!isSupportedVideo(file.getOriginalFilename(), file.getContentType())) {
            result.put("success", false);
            result.put("msg", "不支持该视频格式");
            return ResponseEntity.badRequest().body(result);
        }
        if (cameraId != null && cameraId <= 0) {
            result.put("success", false);
            result.put("msg", "摄像头编号无效");
            return ResponseEntity.badRequest().body(result);
        }
        Path temporarySource = null, converted = null;
        try {
            String original = file.getOriginalFilename();
            Path temporaryDir = Files.createDirectories(dir().resolve(".transcoding"));
            temporarySource = Files.createTempFile(temporaryDir, "incoming-", ".video");
            converted = Files.createTempFile(temporaryDir, "converted-", ".mp4");
            file.transferTo(temporarySource.toFile());
            convertForBrowser(temporarySource, converted);
            if (Files.size(converted) > MAX_UPLOAD_SIZE_BYTES) throw new IllegalArgumentException("转码后超过 200 MB，请截取较短片段后重试");
            String ts = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
            String filename = "record_" + ts + "_" + UUID.randomUUID().toString().substring(0, 4) + ".mp4";
            Path target = dir().resolve(filename);
            Files.move(converted, target);
            try {
                saveIndex(filename, original, cameraId, parseTime(startedAt, "startedAt"),
                        parseTime(endedAt, "endedAt"), normalizeSource(source), Files.size(target));
            } catch (Exception metadataError) {
                Files.deleteIfExists(target);
                throw metadataError;
            }
            result.put("success", true);
            result.put("filename", filename);
            result.put("msg", "上传成功");
            return ResponseEntity.ok(result);
        } catch (IllegalArgumentException e) {
            result.put("success", false);
            result.put("msg", e.getMessage());
            return ResponseEntity.badRequest().body(result);
        } catch (Exception e) {
            result.put("success", false);
            result.put("msg", "保存录像失败: " + e.getMessage());
            return ResponseEntity.status(500).body(result);
        } finally {
            try { if (temporarySource != null) Files.deleteIfExists(temporarySource); } catch (Exception ignored) { }
            try { if (converted != null) Files.deleteIfExists(converted); } catch (Exception ignored) { }
        }
    }

    @GetMapping("/list")
    public ResponseEntity<?> list() {
        List<Map<String, Object>> list = new ArrayList<>();
        try {
            Map<String, Map<String, Object>> indexes = getIndexes();
            try (DirectoryStream<Path> stream = Files.newDirectoryStream(dir())) {
                for (Path p : stream) {
                    if (!Files.isRegularFile(p)) continue;
                    String filename = p.getFileName().toString();
                    Map<String, Object> item = new HashMap<>(indexes.getOrDefault(filename, new HashMap<>()));
                    item.put("filename", filename);
                    item.put("size", Files.size(p));
                    item.put("mtime", Files.getLastModifiedTime(p).toMillis());
                    if (!item.containsKey("source")) item.put("source", "history");
                    list.add(item);
                }
            }
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("success", false);
            result.put("msg", "读取录像列表失败，请检查录像目录和数据库服务");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(result);
        }
        list.sort((a, b) -> Long.compare(((Number) b.get("mtime")).longValue(), ((Number) a.get("mtime")).longValue()));
        return ResponseEntity.ok(list);
    }

    @GetMapping("/match")
    public ResponseEntity<Map<String, Object>> match(@RequestParam Long cameraId, @RequestParam String at) {
        Map<String, Object> result = new HashMap<>();
        try {
            Timestamp eventAt = parseTime(at, "at");
            if (eventAt == null || cameraId == null || cameraId <= 0) throw new IllegalArgumentException("查询参数无效");
            ensureSchema();
            String sql = "SELECT * FROM recording_index WHERE camera_id = ? " +
                    "AND started_at IS NOT NULL AND ended_at IS NOT NULL " +
                    "AND started_at <= ? AND ended_at >= ? ORDER BY started_at DESC LIMIT 1";
            try (Connection connection = dataSource.getConnection(); PreparedStatement ps = connection.prepareStatement(sql)) {
                ps.setLong(1, cameraId);
                ps.setTimestamp(2, eventAt);
                ps.setTimestamp(3, eventAt);
                try (ResultSet rs = ps.executeQuery()) {
                    if (rs.next()) result.put("data", toIndexMap(rs));
                }
            }
            result.put("success", result.containsKey("data"));
            if (!result.containsKey("data")) result.put("msg", "没有覆盖该告警时刻的录像");
            return ResponseEntity.ok(result);
        } catch (IllegalArgumentException e) {
            result.put("success", false);
            result.put("msg", e.getMessage());
            return ResponseEntity.badRequest().body(result);
        } catch (Exception e) {
            result.put("success", false);
            result.put("msg", "查询关联录像失败");
            return ResponseEntity.status(500).body(result);
        }
    }

    @GetMapping("/stream/{filename:.+}")
    public ResponseEntity<StreamingResponseBody> stream(@PathVariable String filename,
                                                         @RequestHeader(value = HttpHeaders.RANGE, required = false) String range) {
        try {
            Path path = resolveSafe(filename);
            if (!Files.exists(path)) return ResponseEntity.notFound().build();
            long size = Files.size(path);
            String contentType = filename.toLowerCase().endsWith(".mp4") ? "video/mp4" : "video/webm";
            if (range == null || range.isEmpty()) {
                StreamingResponseBody body = streamFile(path, 0, size);
                return ResponseEntity.ok().contentType(MediaType.parseMediaType(contentType))
                        .header(HttpHeaders.ACCEPT_RANGES, "bytes").header(HttpHeaders.CONTENT_LENGTH, String.valueOf(size)).body(body);
            }
            long start = 0, end = size - 1;
            String value = range.replace("bytes=", "").trim();
            int dash = value.indexOf('-');
            if (dash >= 0) {
                String startValue = value.substring(0, dash).trim();
                String endValue = value.substring(dash + 1).trim();
                if (!startValue.isEmpty()) start = Long.parseLong(startValue);
                if (!endValue.isEmpty()) end = Math.min(Long.parseLong(endValue), size - 1);
            }
            if (start > end || start >= size) {
                return ResponseEntity.status(HttpStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                        .header(HttpHeaders.CONTENT_RANGE, "bytes */" + size).build();
            }
            long length = end - start + 1;
            StreamingResponseBody body = streamFile(path, start, length);
            return ResponseEntity.status(HttpStatus.PARTIAL_CONTENT).contentType(MediaType.parseMediaType(contentType))
                    .header(HttpHeaders.ACCEPT_RANGES, "bytes").header(HttpHeaders.CONTENT_RANGE, "bytes " + start + "-" + end + "/" + size)
                    .header(HttpHeaders.CONTENT_LENGTH, String.valueOf(length)).body(body);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            return ResponseEntity.status(500).build();
        }
    }

    private synchronized void ensureReviewSchema() throws SQLException {
        if (reviewSchemaReady) return;
        try (Connection conn = dataSource.getConnection(); Statement statement = conn.createStatement()) {
            statement.execute(
                    "CREATE TABLE IF NOT EXISTS recording_review (" +
                            "id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY," +
                            "recording_id BIGINT NOT NULL," +
                            "reviewer_id BIGINT NOT NULL," +
                            "request_id CHAR(36) NOT NULL," +
                            "start_sec DOUBLE NOT NULL, end_sec DOUBLE NOT NULL, anchor_sec DOUBLE NOT NULL," +
                            "outcome VARCHAR(16) NOT NULL, note VARCHAR(200) NOT NULL," +
                            "created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)," +
                            "UNIQUE KEY uk_recording_review_request (recording_id, reviewer_id, request_id)," +
                            "KEY idx_recording_review (recording_id, created_at, id)" +
                            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
            reviewSchemaReady = true;
        }
    }

    private Map<String, Object> reviewSource(Long recordingId) throws Exception {
        ensureSchema();
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement("SELECT * FROM recording_index WHERE id = ?")) {
            ps.setLong(1, recordingId);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) return null;
                Map<String, Object> item = toIndexMap(rs);
                return Files.isRegularFile(resolveSafe((String) item.get("filename"))) ? item : null;
            }
        }
    }

    private Map<String, Object> reviewRow(ResultSet rs) throws SQLException {
        return Map.of("id", rs.getLong("id"), "reviewerId", rs.getLong("reviewer_id"),
                "start", rs.getDouble("start_sec"), "end", rs.getDouble("end_sec"),
                "at", rs.getDouble("anchor_sec"), "outcome", rs.getString("outcome"),
                "note", rs.getString("note"), "createdAt", rs.getTimestamp("created_at").toInstant().toString());
    }

    @GetMapping("/reviews/{recordingId}")
    public ResponseEntity<?> reviews(@PathVariable Long recordingId) {
        try {
            Map<String, Object> source = reviewSource(recordingId);
            if (source == null) return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("msg", "原录像已删除或不可用"));
            ensureReviewSchema();
            List<Map<String, Object>> items = new ArrayList<>();
            try (Connection conn = dataSource.getConnection();
                 PreparedStatement ps = conn.prepareStatement(
                         "SELECT * FROM recording_review WHERE recording_id = ? ORDER BY created_at DESC, id DESC")) {
                ps.setLong(1, recordingId);
                try (ResultSet rs = ps.executeQuery()) {
                    while (rs.next()) items.add(reviewRow(rs));
                }
            }
            return ResponseEntity.ok(Map.of("source", source, "reviews", items));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("msg", "读取录像复核记录失败"));
        }
    }

    public record ReviewInput(Double start, Double end, Double at, String outcome, String note, UUID requestId) {}

    @PostMapping("/reviews/{recordingId}")
    public ResponseEntity<?> addReview(@PathVariable Long recordingId, @RequestBody ReviewInput input) {
        if (input.start() == null || input.end() == null || input.at() == null
                || !Double.isFinite(input.start()) || !Double.isFinite(input.end()) || !Double.isFinite(input.at())
                || input.start() < 0 || input.end() <= input.start()
                || input.at() < input.start() || input.at() > input.end()
                || input.outcome() == null || !REVIEW_OUTCOMES.contains(input.outcome())
                || input.requestId() == null || (input.note() != null && input.note().length() > 200)) {
            return ResponseEntity.badRequest().body(Map.of("msg", "复核区间或意见无效"));
        }
        long reviewerId = StpUtil.getLoginIdAsLong();
        try {
            Map<String, Object> source = reviewSource(recordingId);
            if (source == null) return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("msg", "原录像已删除或不可用"));
            if (source.get("startedAt") instanceof String started && source.get("endedAt") instanceof String ended) {
                double indexedSeconds = (Instant.parse(ended).toEpochMilli() - Instant.parse(started).toEpochMilli()) / 1000.0;
                if (input.end() > indexedSeconds + 2) {
                    return ResponseEntity.badRequest().body(Map.of("msg", "复核终点超出录像索引范围"));
                }
            }
            ensureReviewSchema();
            String requestId = input.requestId().toString();
            try (Connection conn = dataSource.getConnection();
                 PreparedStatement insert = conn.prepareStatement(
                         "INSERT INTO recording_review (recording_id, reviewer_id, request_id, start_sec, end_sec, anchor_sec, outcome, note) " +
                                 "VALUES (?,?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE id = id");
                 PreparedStatement read = conn.prepareStatement(
                         "SELECT * FROM recording_review WHERE recording_id = ? AND reviewer_id = ? AND request_id = ?")) {
                insert.setLong(1, recordingId);
                insert.setLong(2, reviewerId);
                insert.setString(3, requestId);
                insert.setDouble(4, input.start());
                insert.setDouble(5, input.end());
                insert.setDouble(6, input.at());
                insert.setString(7, input.outcome());
                insert.setString(8, input.note() == null ? "" : input.note());
                insert.executeUpdate();

                read.setLong(1, recordingId);
                read.setLong(2, reviewerId);
                read.setString(3, requestId);
                try (ResultSet rs = read.executeQuery()) {
                    if (rs.next()) return ResponseEntity.ok(reviewRow(rs));
                }
            }
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("msg", "保存复核记录失败，请重试"));
        }
        return ResponseEntity.internalServerError().body(Map.of("msg", "暂时无法读取已保存的复核记录"));
    }

    @DeleteMapping("/{filename:.+}")
    public ResponseEntity<Map<String, Object>> delete(@PathVariable String filename) {
        Map<String, Object> result = new HashMap<>();
        try {
            Path path = resolveSafe(filename);
            boolean ok = Files.deleteIfExists(path);
            ensureSchema();
            try (Connection connection = dataSource.getConnection(); PreparedStatement ps = connection.prepareStatement("DELETE FROM recording_index WHERE filename = ?")) {
                ps.setString(1, filename);
                ps.executeUpdate();
            }
            result.put("success", ok);
            result.put("msg", ok ? "删除成功" : "文件不存在");
            return ResponseEntity.ok(result);
        } catch (IllegalArgumentException e) {
            result.put("success", false);
            result.put("msg", "非法文件名");
            return ResponseEntity.badRequest().body(result);
        } catch (Exception e) {
            result.put("success", false);
            result.put("msg", "删除失败");
            return ResponseEntity.status(500).body(result);
        }
    }
}
