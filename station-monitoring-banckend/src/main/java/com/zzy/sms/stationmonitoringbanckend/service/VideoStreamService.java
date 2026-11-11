package com.zzy.sms.stationmonitoringbanckend.service;

public interface VideoStreamService {
    public void startStreaming(String videoSource);
    public void stopStreaming(String videoSource);
}
