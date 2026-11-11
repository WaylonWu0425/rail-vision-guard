package com.zzy.sms.stationmonitoringbanckend.service;

import com.zzy.sms.stationmonitoringbanckend.entity.Camera;

import java.util.List;

public interface CameraService {
    List<Camera> getAllCameras();
    List<Camera> getBallmachineCameras();
    List<Camera> getGunmachineCameras();
    Camera queryAllByLimit(Camera camera);
    int insertCamera(Camera camera);
    int updateCameraById(Camera camera);
    int deleteCameraById(Long id);
    List<Camera> searchCamera(String keyword);
    List<Camera> getCameraByName(String cameraName);
}
