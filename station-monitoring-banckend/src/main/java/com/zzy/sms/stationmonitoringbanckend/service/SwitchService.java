package com.zzy.sms.stationmonitoringbanckend.service;

import com.zzy.sms.stationmonitoringbanckend.entity.Switch;
import com.zzy.sms.stationmonitoringbanckend.entity.SwitchPresetPoint;

import java.util.List;

public interface SwitchService {
    List<Switch> getSwitch();
    List<SwitchPresetPoint> getSwitchPresetPoint(Long trackId, int field, String throat);

    List<SwitchPresetPoint> checkSwitchPresetPoint(int panPosition, int tiltPosition, int zoom);

    Long insertSwitchPresetPoint(SwitchPresetPoint switchPresetPoint);
    int insertSwitch(Switch switchData);
    Switch getSwitchID(Switch switchData);
    int updateSwitch(Switch switchData);
    int deleteById(Long id);

    List<Switch> search(int field, Long trackId, String throat);
}
