package com.zzy.sms.stationmonitoringbanckend.controller;

import com.zzy.sms.stationmonitoringbanckend.service.DeepSeekService;
import com.zzy.sms.stationmonitoringbanckend.service.DeepSeekService.ChatMessage;
import com.zzy.sms.stationmonitoringbanckend.service.DeepSeekService.ChatResult;
import com.zzy.sms.stationmonitoringbanckend.service.DeepSeekService.DeepSeekException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/ai")
public class AiChatController {

    private final DeepSeekService deepSeekService;

    public AiChatController(DeepSeekService deepSeekService) {
        this.deepSeekService = deepSeekService;
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("configured", deepSeekService.isConfigured());
        body.put("model", deepSeekService.getModel());
        body.put("status", deepSeekService.isConfigured() ? "READY" : "NOT_CONFIGURED");
        return ResponseEntity.ok(body);
    }

    @PostMapping("/chat")
    public ResponseEntity<Map<String, Object>> chat(@RequestBody ChatRequest request) {
        try {
            ChatResult result = deepSeekService.chat(request == null ? null : request.messages());
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("content", result.content());
            data.put("model", result.model());
            data.put("usage", result.usage());
            return ResponseEntity.ok(Map.of("code", 200, "msg", "success", "data", data));
        } catch (IllegalArgumentException exception) {
            return ResponseEntity.badRequest().body(errorBody(exception.getMessage()));
        } catch (DeepSeekException exception) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY).body(errorBody(exception.getMessage()));
        }
    }

    private Map<String, Object> errorBody(String message) {
        return Map.of("code", 500, "msg", message);
    }

    public record ChatRequest(List<ChatMessage> messages) {}
}
