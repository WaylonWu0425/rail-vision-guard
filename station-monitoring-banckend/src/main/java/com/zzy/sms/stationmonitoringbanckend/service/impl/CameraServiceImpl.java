package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.zzy.sms.stationmonitoringbanckend.controller.CameraWebSocketController;
import com.zzy.sms.stationmonitoringbanckend.entity.Camera;
import com.zzy.sms.stationmonitoringbanckend.mapper.CameraMapper;
import com.zzy.sms.stationmonitoringbanckend.service.CameraService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @description:
 * @author: zzy
 * @create: 2025-02-09 14:23
 **/
@Service
public class CameraServiceImpl implements CameraService {
    @Autowired
    private CameraMapper cameraMapper;
    @Autowired
    private CameraWebSocketController cameraWebSocketController; // 注入 WebSocket 处理器

    @Override
    public List<Camera> getAllCameras() {
        return cameraMapper.getAllCameras();
    }

    @Override
    public List<Camera> getBallmachineCameras() {
        return cameraMapper.getBallmachineCameras();
    }

    @Override
    public List<Camera> getGunmachineCameras() {
        return cameraMapper.getGunmachineCameras();
    }

    @Override
    public Camera queryAllByLimit(Camera camera) {
        return cameraMapper.queryAllByLimit(camera);
    }

    @Override
    public int insertCamera(Camera camera) {
        return cameraMapper.insertCamera(camera);
    }

    @Override
    public int updateCameraById(Camera camera) {
        return cameraMapper.updateCameraById(camera);
    }

    @Override
    public int deleteCameraById(Long id) {
        return cameraMapper.deleteCameraById(id);
    }

    @Override
    public List<Camera> searchCamera(String keyword) {
        return cameraMapper.searchCamera(keyword);
    }
    @Override
    public List<Camera> getCameraByName(String cameraName) {
        return cameraMapper.getCameraByName(cameraName);
    }

    //实时获取摄像头状态
    @Scheduled(fixedRate = 2000)
    public void pushCameraStatus() {
        List<Camera> cameras = cameraMapper.getAllCameras();
        cameraWebSocketController.broadcast(cameras);
    }
}
