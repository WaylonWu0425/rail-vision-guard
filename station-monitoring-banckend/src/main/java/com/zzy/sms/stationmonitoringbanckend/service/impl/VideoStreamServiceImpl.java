package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.zzy.sms.stationmonitoringbanckend.service.VideoStreamService;

import com.zzy.sms.stationmonitoringbanckend.websocket.VideoStreamHandler;

import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

/**
 * @description:
 * @author: zzy
 * @create: 2025-02-15 22:37
 **/

@Service
public class VideoStreamServiceImpl implements VideoStreamService {

    Map<String,Map<String,Object>> streamMap = new HashMap<>();

    private static final String rtmpUrl = "rtmp://localhost:1935/live";


    @Override
    public void startStreaming(String videoSource) {
        try {
            VideoStreamHandler videoStreamHandler = new VideoStreamHandler();

            videoStreamHandler.startStreaming(videoSource, rtmpUrl + "?key=123456");

        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public void stopStreaming(String videoSource) {
//        videoStreamHandler.stopStreaming();
    }


}
