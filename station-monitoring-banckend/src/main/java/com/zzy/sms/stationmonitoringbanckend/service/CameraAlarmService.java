package com.zzy.sms.stationmonitoringbanckend.service;

import com.zzy.sms.stationmonitoringbanckend.dto.CameraAlarmDTO;
import com.zzy.sms.stationmonitoringbanckend.entity.CameraAlarm;

import java.util.Date;
import java.util.List;
import java.util.Map;

public interface CameraAlarmService {
    List<CameraAlarmDTO> getAllCameraAlarm();
    List<CameraAlarmDTO> getUndisposedCameraAlarm();
    int updateCameraAlarmById(Long id, Long userId, Date dealDate);
    int insertCameraAlarm(CameraAlarm cameraAlarm);
    List<CameraAlarmDTO> search(String cameraName, int day, String type);
    List<Map<String, Integer>> getCameraAlarmByDay();
}
