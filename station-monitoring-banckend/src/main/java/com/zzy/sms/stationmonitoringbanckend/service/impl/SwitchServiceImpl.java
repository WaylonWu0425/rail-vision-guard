package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.zzy.sms.stationmonitoringbanckend.entity.Switch;
import com.zzy.sms.stationmonitoringbanckend.entity.SwitchPresetPoint;
import com.zzy.sms.stationmonitoringbanckend.mapper.SwitchMapper;
import com.zzy.sms.stationmonitoringbanckend.mapper.SwitchPresetPointMapper;
import com.zzy.sms.stationmonitoringbanckend.service.SwitchService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-09 13:59
 **/

@Service
public class SwitchServiceImpl implements SwitchService {

    @Autowired
    private SwitchMapper switchMapper;

    @Autowired
    private SwitchPresetPointMapper switchPresetPointMapper;


    @Override
    public List<Switch> getSwitch() {
        return switchMapper.getSwitch();
    }

    @Override
    public List<SwitchPresetPoint> getSwitchPresetPoint(Long trackId, int field, String throat) {
        return switchPresetPointMapper.getSwitchPresetPoint(trackId, field, throat);
    }

    @Override
    public List<SwitchPresetPoint> checkSwitchPresetPoint(int panPosition, int tiltPosition, int zoom) {
        return switchPresetPointMapper.checkSwitchPresetPoint(panPosition, tiltPosition, zoom);
    }

    @Override
    public Long insertSwitchPresetPoint(SwitchPresetPoint switchPresetPoint) {
        switchPresetPointMapper.insertSwitchPresetPoint(switchPresetPoint);
        return switchPresetPoint.getId();
    }

    @Override
    public int insertSwitch(Switch switchData) {
        return switchMapper.insertSwitch(switchData);
    }

    @Override
    public Switch getSwitchID(Switch switchData) {
        return switchMapper.getSwitchID(switchData);
    }

    @Override
    public int updateSwitch(Switch switchData) {
        return switchMapper.updateSwitch(switchData);
    }

    @Override
    public int deleteById(Long id) {
        return switchMapper.deleteById(id);
    }

    @Override
    public List<Switch> search(int field, Long trackId, String throat) {
        return switchMapper.search(field, trackId, throat);
    }

}
