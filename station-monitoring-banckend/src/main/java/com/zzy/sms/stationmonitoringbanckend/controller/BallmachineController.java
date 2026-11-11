package com.zzy.sms.stationmonitoringbanckend.controller;

import com.zzy.sms.stationmonitoringbanckend.entity.Ballmachine;
import com.zzy.sms.stationmonitoringbanckend.dto.BallmachineDTO;
import com.zzy.sms.stationmonitoringbanckend.entity.PresetPoint;
import com.zzy.sms.stationmonitoringbanckend.service.BallmachinePresetPointService;
import com.zzy.sms.stationmonitoringbanckend.service.BallmachineService;
import com.zzy.sms.stationmonitoringbanckend.service.PresetPointService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-04 15:23
 **/
@RestController
@RequestMapping("/BallmachinePresetPoint")
public class BallmachineController {

    @Autowired
    private BallmachinePresetPointService ballmachinePresetPointService;

    @Autowired
    private PresetPointService presetPointService;

    @Autowired
    private BallmachineService ballmachineService;

    @GetMapping("/getAllBallmachine")
    public List<BallmachineDTO> getAllBallmachine() {
        return ballmachinePresetPointService.getAllBallmachine();
    }

    @PostMapping("/insertPresetPoint")
    public ResponseEntity insertPresetPoint(@RequestBody PresetPoint presetPoint) {
        PresetPoint presetPointRes = presetPointService.queryAllByLimit(presetPoint);
        if(presetPointRes==null) {
            return ResponseEntity.ok(presetPointService.insertPresetPoint(presetPoint));
        }
        Long presetPointId = presetPointService.queryAllByLimit(presetPoint).getId();
        return ResponseEntity.ok(presetPointId);
    }

    @PostMapping("/insertBallmachine")
    public ResponseEntity insertBallmachine(@RequestBody Ballmachine ballmachine) {
        Map<String, Object> response = new HashMap<>();
        try {
            if(ballmachineService.insertBallmachine(ballmachine) == 1) {
                response.put("code", 200);
                response.put("message", "插入成功");
                return ResponseEntity.ok(response);
            }else {
                response.put("code", 400);
                response.put("message", "插入失败");
                return ResponseEntity.ok(response);
            }
        }catch (Exception e) {
            response.put("code", 400);
            response.put("message", "数据违反唯一性约束");
            return ResponseEntity.badRequest().body(response);
        }
    }
    @PostMapping("/updateBallmachine")
    public ResponseEntity updateBallmachine(@RequestBody Ballmachine ballmachine) {
        System.out.println(ballmachine);
        try {
            ballmachineService.updateBallmachine(ballmachine);
        }catch (Exception e) {
            System.out.println(e);
        }
        return ResponseEntity.ok("true");
    }
    @DeleteMapping("/deleteBallmachine")
    public ResponseEntity deleteBallmachineById(@RequestParam("id") Long id) {
        Map<String, Object> response = new HashMap<>();
        try {
            ballmachineService.deleteBallmachineById(id);
        }catch (Exception e) {
            System.out.println(e);
            response.put("success", false);
            return ResponseEntity.ok(response);
        }
        response.put("success", true);
        return ResponseEntity.ok(response);
    }
    @PostMapping("/search")
    public List<BallmachineDTO> search(@RequestParam(value = "cameraId", required = false) Long cameraId,
                                       @RequestParam(value = "trackId", required = false) Long trackId) {
        List<BallmachineDTO> ballmachinePresetPointList = ballmachinePresetPointService.search(cameraId, trackId);
        return ballmachinePresetPointList;
    }
}
