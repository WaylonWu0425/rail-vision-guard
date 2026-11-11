package com.zzy.sms.stationmonitoringbanckend.controller;

import com.zzy.sms.stationmonitoringbanckend.service.VideoStreamService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody;

/**
 * @description:
 * @author: zzy
 * @create: 2025-02-15 22:56
 **/
@RestController
@RequestMapping("/videoStream")
public class VideoStreamController {
    @Autowired
    private VideoStreamService videoStreamService;

    @GetMapping("/startStream")
    public void liveStream(@RequestParam("source")String source) {
        videoStreamService.startStreaming(source);
    }

}
