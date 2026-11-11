package com.zzy.sms.stationmonitoringbanckend.controller;

import cn.dev33.satoken.stp.StpUtil;
import com.zzy.sms.stationmonitoringbanckend.entity.AlarmInfo;
import com.zzy.sms.stationmonitoringbanckend.service.AlarmInfoService;
import com.zzy.sms.stationmonitoringbanckend.util.DateTimeUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @description:
 * @author: zzy
 * @create: 2025-04-12 00:09
 **/
@RestController
@RequestMapping("/alarmInfo")
public class AlarmInfoController {
    @Autowired
    private AlarmInfoService alarmInfoService;

    @Autowired
    private DateTimeUtil dateTimeUtil;


    @GetMapping("/getAllAlarmInfo")
    public ResponseEntity getAllAlarmInfo() {
        Map<String, Object> response = new HashMap<>();
        try {
            List<AlarmInfo> alarmInfoList = alarmInfoService.getAllAlarmInfo();
            response.put("code", 200);
            response.put("message", "查询成功");
            response.put("data", alarmInfoList);
            response.put("success", true);
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            response.put("code", 200);
            response.put("message", "查询失败");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/getUndisposedAlarmInfo")
    public ResponseEntity getUndisposedAlarmInfo() {
        Map<String, Object> response = new HashMap<>();
        try {
            List<AlarmInfo> alarmInfoList = alarmInfoService.getUndisposedAlarmInfo();
            response.put("code", 200);
            response.put("message", "查询成功");
            response.put("data", alarmInfoList);
            response.put("success", true);
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            response.put("code", 200);
            response.put("message", "查询失败");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
    }
    @GetMapping("/search")
    public ResponseEntity search(@RequestParam(value = "cameraName", required = false) String cameraName,
                                 @RequestParam(value = "day", defaultValue = "0") int day,
                                 @RequestParam(value = "type", defaultValue = "0") Byte type,
                                 @RequestParam("status") String status) {
        Map<String, Object> response = new HashMap<>();
        try {
            List<AlarmInfo> alarmInfoList = alarmInfoService.search(cameraName, day, type, status);
            response.put("code", 200);
            response.put("message", "搜索成功");
            response.put("data", alarmInfoList);
            response.put("success", true);
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            response.put("code", 200);
            response.put("message", "搜索失败");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
    }
    @GetMapping("/updateAlarmInfoById")
    public ResponseEntity updateAlarmInfoById(@RequestParam("id") Long id) {
        Map<String, Object> response = new HashMap<>();
        Date dealTime = dateTimeUtil.getCurrentTime();
        Long userId = StpUtil.getLoginIdAsLong();
        try {
            alarmInfoService.updateAlarmInfoById(id, userId, dealTime);
            response.put("code", 200);
            response.put("message", "处理成功");
            response.put("success", true);
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            System.out.println(e);
            response.put("code", 200);
            response.put("message", "处理失败");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
    }
}
