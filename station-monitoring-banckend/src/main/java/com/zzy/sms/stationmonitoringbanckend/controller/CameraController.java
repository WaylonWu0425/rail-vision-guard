package com.zzy.sms.stationmonitoringbanckend.controller;

import com.zzy.sms.stationmonitoringbanckend.entity.Camera;
import com.zzy.sms.stationmonitoringbanckend.service.CameraLoginService;
import com.zzy.sms.stationmonitoringbanckend.service.CameraService;
import com.zzy.sms.stationmonitoringbanckend.util.DateTimeUtil;
import com.zzy.sms.stationmonitoringbanckend.util.IPv4Validator;
import org.apache.ibatis.annotations.Delete;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @description:
 * @author: zzy
 * @create: 2025-02-09 14:33
 **/
@RestController
@RequestMapping("/camera/")
public class CameraController {
    @Autowired
    private CameraService cameraService;
    @Autowired
    private DateTimeUtil dateTimeUtil;
    @Autowired
    private IPv4Validator iPv4Validator;
    @Autowired
    private CameraLoginService cameraLoginService;

    @GetMapping("getCameras")
    public ResponseEntity<List<Camera>> getAllCameras() {
//        cameraLoginService.initCameraObject();
        List<Camera> cameraList = cameraService.getAllCameras();
        return ResponseEntity.ok(cameraList);
    }
    @GetMapping("getBallmachineCameras")
    public ResponseEntity<List<Camera>> getBallmachineCameras() {
        List<Camera> cameraList = cameraService.getBallmachineCameras();
        return ResponseEntity.ok(cameraList);
    }
    @GetMapping("getGunmachineCameras")
    public ResponseEntity<List<Camera>> getGunmachineCameras() {
        List<Camera> cameraList = cameraService.getGunmachineCameras();
        return ResponseEntity.ok(cameraList);
    }
    @PostMapping("insertCamera")
    public ResponseEntity insertCamera(@RequestBody Camera camera) {
        Date dateTime = dateTimeUtil.getCurrentTime();
//        if(!iPv4Validator.isValidIPv4(ip))return ResponseEntity.badRequest().body("格式不正确");
        camera.setCreateTime(dateTime);
        camera.setUpdateTime(dateTime);
        try{
            cameraService.insertCamera(camera);
        }catch (Exception e) {
            System.out.println(e);
            return ResponseEntity.badRequest().body("摄像头添加失败");
        }
        Map<String, Object> response = new HashMap<>();
        response.put("message", "摄像头添加成功");
        response.put("success", true);
        return ResponseEntity.ok(response);
    }
    @PostMapping("updateCameraById")
    public ResponseEntity updateCameraById(@RequestBody Camera camera) {
        System.out.println(camera);
        try {
            cameraService.updateCameraById(camera);
        }catch (Exception e) {
            return ResponseEntity.badRequest().body("修改失败");
        }
        Map<String, Object> response = new HashMap<>();
        response.put("message", "摄像头修改成功");
        response.put("success", true);
        return ResponseEntity.ok(response);
    }
    @DeleteMapping("deleteCameraById")
    public ResponseEntity deleteCameraById(@RequestParam("id") Long id) {
        try {
            cameraService.deleteCameraById(id);
        }catch (Exception e) {
            System.out.println(e);
            return ResponseEntity.badRequest().body("摄像头删除失败");
        }
        Map<String, Object> response = new HashMap<>();
        response.put("message", "摄像头删除成功");
        response.put("success", true);
        return ResponseEntity.ok(response);
    }
    @GetMapping("searchCamera")
    public ResponseEntity<List<Camera>> searchCamera(@RequestParam("keyword") String keyword) {
        List<Camera> camera = cameraService.searchCamera(keyword);
        return ResponseEntity.ok(camera);
    }
    @GetMapping("searchCameraByName")
    public ResponseEntity getCameraByName(@RequestParam("cameraName") String cameraName) {
        Map<String, Object> response = new HashMap<>();
        List<Camera> cameraList = cameraService.getCameraByName(cameraName);
        response.put("success", true);
        response.put("data", cameraList);
        return ResponseEntity.ok(response);
    }
    @GetMapping("countOnlineCameras")
    public int countOnlineCameras() {
        return cameraLoginService.countOnlineCameras();
    }
    @GetMapping("countOfflineCameras")
    public int countOfflineCameras() {
        return cameraLoginService.countOfflineCameras();
    }
}
