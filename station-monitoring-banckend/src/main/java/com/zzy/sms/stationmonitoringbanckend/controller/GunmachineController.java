package com.zzy.sms.stationmonitoringbanckend.controller;

import com.zzy.sms.stationmonitoringbanckend.dto.GunmachineDTO;
import com.zzy.sms.stationmonitoringbanckend.entity.Camera;
import com.zzy.sms.stationmonitoringbanckend.entity.Gunmachine;
import com.zzy.sms.stationmonitoringbanckend.service.GunmachineService;
import org.apache.ibatis.annotations.Delete;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-06 20:53
 **/

@RestController
@RequestMapping("/gunmachine")
public class GunmachineController {

    @Autowired
    private GunmachineService gunmachineService;

    @GetMapping("/getAllGunmachine")
    public List<GunmachineDTO> getAllGunmachine() {
        List<GunmachineDTO> gunmachineList = gunmachineService.getAllGunmachine();
        return gunmachineList;
    }
    @PostMapping("/insertGunmachine")
    public ResponseEntity insertGunmachine(@RequestBody Gunmachine gunmachine) {
        try {
            gunmachineService.insertGunmachine(gunmachine);
        }catch (Exception e) {
            System.out.println(e);
        }
        return ResponseEntity.ok("true");
    }

    @PostMapping("/updateGunmachine")
    public ResponseEntity updateGunmachine(@RequestBody Gunmachine gunmachine) {
        try{
            gunmachineService.updateGunmachine(gunmachine);
        }catch (Exception e) {
            System.out.println(e);
            return ResponseEntity.badRequest().body("false");
        }
        return ResponseEntity.ok("ture");
    }
    @PostMapping("/deleteById")
    public ResponseEntity deleteById(@RequestParam("id") Long id) {
        Map<String, Object> response = new HashMap<>();
        if(gunmachineService.deleteById(id)==1) {
            response.put("success", true);
            return ResponseEntity.ok(response);
        }else {
            response.put("success", false);
            return ResponseEntity.ok(response);
        }
    }

    @GetMapping("/search")
    public List<GunmachineDTO> search(@RequestParam(value = "cameraId", required = false) Long cameraId,
                                      @RequestParam(value = "trackId", required = false) Long trackId) {
        return gunmachineService.search(cameraId, trackId);
    }
}
