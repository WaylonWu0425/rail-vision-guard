package com.zzy.sms.stationmonitoringbanckend.service;

import com.zzy.sms.stationmonitoringbanckend.entity.AlarmInfo;

import java.util.Date;
import java.util.List;

public interface AlarmInfoService {
    List<AlarmInfo> getAllAlarmInfo();
    List<AlarmInfo> getUndisposedAlarmInfo();
    List<AlarmInfo> search(String cameraName, int day, Byte type, String status);
    int updateAlarmInfoById(Long id, Long userId, Date dealTime);
}
