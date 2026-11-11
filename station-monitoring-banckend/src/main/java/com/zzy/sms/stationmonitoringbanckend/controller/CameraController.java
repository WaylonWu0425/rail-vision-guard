package com.zzy.sms.stationmonitoringbanckend.controller;

import com.zzy.sms.stationmonitoringbanckend.entity.Camera;
import com.zzy.sms.stationmonitoringbanckend.mapper.CameraMapper;
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
    @Autowired
    private CameraMapper cameraMapper;

    @GetMapping("getCameras")
    public ResponseEntity<List<Camera>> getAllCameras() {
//        cameraLoginService.initCameraObject();
        List<Camera> cameraList = cameraService.getAllCameras();
        return ResponseEntity.ok(cameraList);
    }

    /**
     * 云台控制（PTZ）标准化接口
     * POST /camera/ptzControl
     * body: {"cameraId":7, "code":"Up", "stop":false, "speed":5, "channel":0}
     * code: Up/Down/Left/Right/LeftUp/RightUp/LeftDown/RightDown/ZoomTele/ZoomWide/FocusNear/FocusFar/IrisLarge/IrisSmall
     */
    @PostMapping("ptzControl")
    public ResponseEntity<Map<String, Object>> ptzControl(@RequestBody Map<String, Object> body) {
        Map<String, Object> result = new HashMap<>();
        try {
            Long cameraId = Long.valueOf(String.valueOf(body.get("cameraId")));
            String code = String.valueOf(body.get("code"));
            boolean stop = Boolean.parseBoolean(String.valueOf(body.get("stop")));
            int speed = body.get("speed") == null ? 5 : Integer.parseInt(String.valueOf(body.get("speed")));
            int channel = body.get("channel") == null ? 0 : Integer.parseInt(String.valueOf(body.get("channel")));

            boolean ok = cameraLoginService.ptzControl(cameraId, code, stop, speed, channel);
            result.put("success", ok);
            result.put("msg", ok ? "指令下发成功" : "指令下发失败（摄像头离线或指令无效）");
            return ResponseEntity.ok(result);
        } catch (NumberFormatException e) {
            result.put("success", false);
            result.put("msg", "参数格式错误");
            return ResponseEntity.badRequest().body(result);
        }
    }

    /**
     * 跳转预置点（回到初始位置）
     * POST /camera/gotoPreset
     * body: {"cameraId":7, "presetId":1, "channel":0}
     * presetId 可选，不传则自动使用 camera 表的 initViewPoint 字段
     */
    @PostMapping("gotoPreset")
    public ResponseEntity<Map<String, Object>> gotoPreset(@RequestBody Map<String, Object> body) {
        Map<String, Object> result = new HashMap<>();
        try {
            Long cameraId = Long.valueOf(String.valueOf(body.get("cameraId")));
            int presetId;
            if (body.get("presetId") != null) {
                presetId = Integer.parseInt(String.valueOf(body.get("presetId")));
            } else {
                // 从 camera 表取 initViewPoint 作为默认预置点
                Camera camera = cameraMapper.getCameraById(cameraId);
                if (camera == null || camera.getInitViewPoint() == null) {
                    result.put("success", false);
                    result.put("msg", "摄像头不存在或未设置初始预置点");
                    return ResponseEntity.badRequest().body(result);
                }
                presetId = camera.getInitViewPoint();
            }
            int channel = body.get("channel") == null ? 0 : Integer.parseInt(String.valueOf(body.get("channel")));

            boolean ok = cameraLoginService.gotoPreset(cameraId, presetId, channel);
            result.put("success", ok);
            result.put("msg", ok ? "已跳转至预置点 " + presetId : "跳转失败（摄像头离线或预置点不存在）");
            return ResponseEntity.ok(result);
        } catch (NumberFormatException e) {
            result.put("success", false);
            result.put("msg", "参数格式错误");
            return ResponseEntity.badRequest().body(result);
        }
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
        // 前端新增表单只填 名称/IP/产品编号/类型/账号/密码，以下 NOT NULL 列补默认值，否则插入失败
        if (camera.getStatus() == null) camera.setStatus("1");      // 初始离线，SDK 登录成功后自动置 0
        if (camera.getPort() == null) camera.setPort(37777);        // 大华 SDK 默认端口
        if (camera.getBridgeType() == null) camera.setBridgeType(1);
        if (camera.getInitViewPoint() == null) camera.setInitViewPoint(1);
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
