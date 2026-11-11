package com.zzy.sms.stationmonitoringbanckend.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientResponseException;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class DeepSeekService {

    private static final Logger LOGGER = LoggerFactory.getLogger(DeepSeekService.class);
    private static final int MAX_MESSAGES = 20;
    private static final int MAX_MESSAGE_LENGTH = 4_000;
    private static final int MAX_TOTAL_LENGTH = 24_000;
    private static final String SYSTEM_PROMPT = String.join("\n",
            "你是‘视界巡警’车站视频监控系统中的AI运维助手。",
            "你的回答应围绕当前系统的实际模块：摄像头管理、实时预览、YOLO智能检测、告警中心、告警历史、手动录像、视频回放、预置点管理、数据统计和作业任务。",
            "当前比赛演示主流程是：摄像头取流、YOLO人车检测、告警记录与截图、手动录像、按摄像头和时间关联回放。",
            "当前演示设备是大华DH-IPC-HFW4443T-AS-P固定枪机，不具备云台旋转和光学变焦能力；目标检测由本机服务运行，不是摄像头自身能力。",
            "当前项目已验证的检测类别只有人员和车辆；异物检测属于固定机位、固定光照下的基线比对原型。",
            "当信息不足时明确说明需要核查的条件，不虚构设备能力、准确率、部署结果、订单或现场数据。",
            "回答使用专业、简洁的中文；涉及操作时按‘现象判断、排查步骤、预期结果、仍失败时的下一步’组织内容。"
    );

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private final String apiKey;
    private final String baseUrl;
    private final String model;

    public DeepSeekService(
            RestTemplateBuilder builder,
            ObjectMapper objectMapper,
            @Value("${deepseek.api-key:}") String apiKey,
            @Value("${deepseek.base-url:https://api.deepseek.com}") String baseUrl,
            @Value("${deepseek.model:deepseek-flash}") String model
    ) {
        this.restTemplate = builder
                .setConnectTimeout(Duration.ofSeconds(10))
                .setReadTimeout(Duration.ofSeconds(90))
                .build();
        this.objectMapper = objectMapper;
        this.apiKey = apiKey == null ? "" : apiKey.trim();
        this.baseUrl = trimTrailingSlash(baseUrl);
        this.model = model == null || model.isBlank() ? "deepseek-flash" : model.trim();
    }

    public boolean isConfigured() {
        return !apiKey.isBlank();
    }

    public String getModel() {
        return model;
    }

    public ChatResult chat(List<ChatMessage> inputMessages) {
        if (!isConfigured()) {
            throw new DeepSeekException("AI服务尚未配置密钥");
        }

        List<Map<String, String>> messages = normalizeMessages(inputMessages);
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("model", model);
        payload.put("messages", messages);
        payload.put("stream", false);
        payload.put("max_tokens", 1_500);
        payload.put("temperature", 0.3);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(apiKey);

        try {
            String rawResponse = restTemplate.postForObject(
                    baseUrl + "/chat/completions",
                    new HttpEntity<>(payload, headers),
                    String.class
            );
            JsonNode root = objectMapper.readTree(rawResponse);
            JsonNode contentNode = root.path("choices").path(0).path("message").path("content");
            String content = contentNode.asText("").trim();
            if (content.isBlank()) {
                throw new DeepSeekException("AI服务返回了空内容");
            }
            return new ChatResult(content, root.path("model").asText(model), root.path("usage"));
        } catch (RestClientResponseException exception) {
            LOGGER.warn("DeepSeek request failed with status {}", exception.getRawStatusCode());
            if (exception.getRawStatusCode() == 401 || exception.getRawStatusCode() == 403) {
                throw new DeepSeekException("AI服务密钥无效或无访问权限");
            }
            if (exception.getRawStatusCode() == 429) {
                throw new DeepSeekException("AI服务请求过于频繁，请稍后重试");
            }
            throw new DeepSeekException("AI服务暂时不可用，请稍后重试");
        } catch (DeepSeekException exception) {
            throw exception;
        } catch (Exception exception) {
            LOGGER.warn("DeepSeek request failed", exception);
            throw new DeepSeekException("无法连接AI服务，请检查网络后重试");
        }
    }

    private List<Map<String, String>> normalizeMessages(List<ChatMessage> inputMessages) {
        if (inputMessages == null || inputMessages.isEmpty()) {
            throw new IllegalArgumentException("消息不能为空");
        }

        int start = Math.max(0, inputMessages.size() - MAX_MESSAGES);
        int totalLength = SYSTEM_PROMPT.length();
        List<Map<String, String>> normalized = new ArrayList<>();
        normalized.add(Map.of("role", "system", "content", SYSTEM_PROMPT));

        for (int index = start; index < inputMessages.size(); index++) {
            ChatMessage message = inputMessages.get(index);
            if (message == null || message.content() == null) continue;
            String role = "assistant".equals(message.role()) ? "assistant" : "user";
            String content = message.content().trim();
            if (content.isBlank()) continue;
            if (content.length() > MAX_MESSAGE_LENGTH) {
                throw new IllegalArgumentException("单条消息不能超过4000字");
            }
            totalLength += content.length();
            if (totalLength > MAX_TOTAL_LENGTH) {
                throw new IllegalArgumentException("对话内容过长，请清空会话后重试");
            }
            normalized.add(Map.of("role", role, "content", content));
        }

        if (normalized.size() == 1 || !"user".equals(normalized.get(normalized.size() - 1).get("role"))) {
            throw new IllegalArgumentException("最后一条消息必须是用户问题");
        }
        return normalized;
    }

    private static String trimTrailingSlash(String value) {
        String result = value == null ? "https://api.deepseek.com" : value.trim();
        while (result.endsWith("/")) result = result.substring(0, result.length() - 1);
        return result;
    }

    public record ChatMessage(String role, String content) {}

    public record ChatResult(String content, String model, JsonNode usage) {}

    public static class DeepSeekException extends RuntimeException {
        public DeepSeekException(String message) {
            super(message);
        }
    }
}
