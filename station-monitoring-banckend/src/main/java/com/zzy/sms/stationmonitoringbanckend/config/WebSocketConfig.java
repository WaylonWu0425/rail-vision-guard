package com.zzy.sms.stationmonitoringbanckend.config;

import com.zzy.sms.stationmonitoringbanckend.controller.CameraWebSocketController;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-30 13:43
 **/

@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {
    private final CameraWebSocketController cameraWebSocketController;

    @Autowired
    public WebSocketConfig(CameraWebSocketController cameraWebSocketController) {
        this.cameraWebSocketController = cameraWebSocketController;
    }

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        // 配置原生WebSocket处理器
        registry.addHandler(cameraWebSocketController, "/ws/cameraStatus")    //ws的端点
                .setAllowedOrigins("*"); //允许跨域
    }

}
