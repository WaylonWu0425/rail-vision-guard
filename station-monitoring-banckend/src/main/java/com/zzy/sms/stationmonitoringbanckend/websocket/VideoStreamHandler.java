package com.zzy.sms.stationmonitoringbanckend.websocket;// 依赖（Maven pom.xml）
/*
<dependency>
    <groupId>org.bytedeco</groupId>
    <artifactId>javacv-platform</artifactId>
    <version>1.5.8</version>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-websocket</artifactId>
</dependency>
*/

import org.bytedeco.ffmpeg.global.avcodec;
import org.bytedeco.ffmpeg.global.avutil;
import org.bytedeco.javacv.*;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.BinaryMessage;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.AbstractWebSocketHandler;

import java.io.ByteArrayOutputStream;
import java.nio.ByteBuffer;
import java.util.concurrent.CopyOnWriteArrayList;

public class VideoStreamHandler {

    private FFmpegFrameGrabber grabber;
    private FFmpegFrameRecorder recorder;

    // 初始化视频采集（根据实际摄像头设备名称修改）
    public void startStreaming(String cameraDevice,String rtmp) throws FrameGrabber.Exception, FFmpegFrameRecorder.Exception {

        grabber = new FFmpegFrameGrabber(cameraDevice);
        // Windows摄像头参数示例
        grabber.setFormat("dshow");
        grabber.setOption("rtbufsize", "1024M");
        grabber.setImageWidth(640);
        grabber.setImageHeight(480);
        grabber.start();

        recorder = new FFmpegFrameRecorder(rtmp, 640, 480);
        recorder.setVideoCodec(avcodec.AV_CODEC_ID_H264);
        recorder.setFormat("h264");
        recorder.setPixelFormat(avutil.AV_PIX_FMT_YUV420P);
        recorder.setFrameRate(25); // 修正为合理帧率
        recorder.start();
    }

    public void stopStreaming() {
        try {
            if (recorder != null) recorder.close();
            if (grabber != null) grabber.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}