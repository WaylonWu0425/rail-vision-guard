package com.zzy.sms.stationmonitoringbanckend.controller;

import com.zzy.sms.stationmonitoringbanckend.dto.SwitchDTO;
import com.zzy.sms.stationmonitoringbanckend.entity.Switch;
import com.zzy.sms.stationmonitoringbanckend.entity.SwitchPresetPoint;
import com.zzy.sms.stationmonitoringbanckend.service.SwitchService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-09 14:01
 **/

@RestController
@RequestMapping("/switch")
public class SwitchController {

    @Autowired
    private SwitchService switchService;

    @GetMapping("/getSwitch")
    public ResponseEntity getSwitch() {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "获取成功");
        response.put("success", true);
        response.put("data", switchService.getSwitch());
        return ResponseEntity.ok(response);
    }

    @GetMapping("/getSwitchPresetPoint")
    public ResponseEntity getSwitchPresetPoint(@RequestParam("trackId") Long trackId, @RequestParam("field") int field, @RequestParam("throat") String throat) {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "获取成功");
        response.put("success", true);
        response.put("data", switchService.getSwitchPresetPoint(trackId, field, throat));
        return ResponseEntity.ok(response);
    }

    @PostMapping("/insertSwitchPresetPoint")
    public ResponseEntity insertSwitchPresetPoint(@RequestBody SwitchDTO switchDTO) {
        Map<String, Object> response = new HashMap<>();
        List<SwitchPresetPoint> switchPresetPointList = switchService.checkSwitchPresetPoint(switchDTO.getPanPosition(), switchDTO.getTiltPosition(), switchDTO.getZoom());
        for (SwitchPresetPoint i : switchPresetPointList) {
            List<String> switchList = Arrays.asList(i.getSwitchNumber().split("、"));
            if(switchDTO.getSwitchNumber().equals(switchList)) {
                response.put("message", "在数据库中找到id");
                response.put("success", false);
                response.put("data", i.getId());
                return ResponseEntity.ok(response);
            }
        }
        String switchNumber = String.join("、",switchDTO.getSwitchNumber());
        SwitchPresetPoint switchPresetPoint = new SwitchPresetPoint(null, switchDTO.getPanPosition(), switchDTO.getTiltPosition(), switchDTO.getZoom(), switchNumber);
        response.put("data", switchService.insertSwitchPresetPoint(switchPresetPoint));
        response.put("success", true);
        response.put("message", "在数据库生成新的id");
        return ResponseEntity.ok(response);
    }
    @PostMapping("/insertSwitch")
    public ResponseEntity insertSwitch(@RequestBody Switch switchData) {
        Map<String, Object> response = new HashMap<>();
        try {
            switchService.insertSwitch(switchData);
            response.put("success", true);
            response.put("message", "插入成功");
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            response.put("success", false);
            response.put("message", "插入失败");
            return ResponseEntity.ok(response);
        }
    }
    @PostMapping("/updateSwitch")
    public ResponseEntity updateSwitch(@RequestBody Switch switchData, @RequestParam("switchPresetPointId") Long switchPresetPointId) {
        Map<String, Object> response = new HashMap<>();
        switchData.setId(switchService.getSwitchID(switchData).getId());
        switchData.setSwitchPresetPointId(switchPresetPointId);
        try {
            switchService.updateSwitch(switchData);
            response.put("success", true);
            response.put("message", "修改成功");
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            response.put("success", false);
            response.put("message", "修改失败");
            return ResponseEntity.badRequest().body(response);
        }
    }
    @DeleteMapping("/deleteSwitch")
    public ResponseEntity deleteSwitch(@RequestBody Switch switchData) {
        Map<String, Object> response = new HashMap<>();
        try {
            Long switchId = switchService.getSwitchID(switchData).getId();
            switchService.deleteById(switchId);
            response.put("success", true);
            response.put("message", "删除成功");
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            response.put("success", false);
            response.put("message", "删除失败");
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/search")
    public ResponseEntity search(@RequestParam(value = "field", required = false) int field,
                                 @RequestParam(value = "trackId", required = false) Long trackId,
                                 @RequestParam(value = "throat", required = false) String throat) {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "获取成功");
        response.put("success", true);
        response.put("data", switchService.search(field, trackId, throat));
        return ResponseEntity.ok(response);
    }
}
