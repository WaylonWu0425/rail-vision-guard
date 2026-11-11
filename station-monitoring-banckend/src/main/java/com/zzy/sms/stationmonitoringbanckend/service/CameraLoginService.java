package com.zzy.sms.stationmonitoringbanckend.service;

public interface CameraLoginService {
    int countOnlineCameras();
    int countOfflineCameras();

    void initCameraObject();

    void loginAllCameras();
}
