package com.zzy.sms.stationmonitoringbanckend.controller;

import cn.dev33.satoken.stp.StpUtil;
import com.zzy.sms.stationmonitoringbanckend.dto.CameraAlarmDTO;
import com.zzy.sms.stationmonitoringbanckend.service.CameraAlarmService;
import com.zzy.sms.stationmonitoringbanckend.util.DateTimeUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-30 21:52
 **/

@RestController
@RequestMapping("/cameraAlarm")
public class CameraAlarmController {
    @Autowired
    private CameraAlarmService cameraAlarmService;
    @Autowired
    private DateTimeUtil dateTimeUtil;


    @GetMapping("/getAllCameraAlarm")   //获取摄像头所有警告信息
    public List<CameraAlarmDTO> getAllCameraAlarm() {
        return cameraAlarmService.getAllCameraAlarm();
    }

    @GetMapping("/getUndisposedCameraAlarm")    //获取未处理的摄像头警告
    public List<CameraAlarmDTO> getUndisposedCameraAlarm() {
        return cameraAlarmService.getUndisposedCameraAlarm();
    }

    @PostMapping("/updateCameraAlarmById")      //处理摄像头警告
    public ResponseEntity updateCameraAlarmById(@RequestParam("id") Long id) {
        Map<String, Object> response = new HashMap<>();
        Long userId = StpUtil.getLoginIdAsLong();
        Date dealDate = dateTimeUtil.getCurrentTime();
        try {
            cameraAlarmService.updateCameraAlarmById(id, userId, dealDate);
            response.put("success", true);
            response.put("message", "处理成功");
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            System.out.println(e);
            response.put("success", false);
            response.put("message", "处理失败");
            return ResponseEntity.badRequest().body(response);
        }
    }
    @GetMapping("/search")      //搜索
    public ResponseEntity search(@RequestParam(value = "cameraName", required = false) String cameraName, @RequestParam(value = "day", defaultValue = "0") int day, @RequestParam String type) {
        Map<String, Object> response = new HashMap<>();
        try {
            List<CameraAlarmDTO> cameraAlarmDTOList = cameraAlarmService.search(cameraName, day, type);
            response.put("data", cameraAlarmDTOList);
            response.put("success", true);
            response.put("message", "查询成功");
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            System.out.println(e);
            response.put("success", false);
            response.put("message", "查询失败");
            return ResponseEntity.badRequest().body(response);
        }
    }
}
