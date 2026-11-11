package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.zzy.sms.stationmonitoringbanckend.entity.PresetPoint;
import com.zzy.sms.stationmonitoringbanckend.mapper.PresetPointMapper;
import com.zzy.sms.stationmonitoringbanckend.service.PresetPointService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-05 16:11
 **/
@Service
public class PresetPointServiceImpl implements PresetPointService {

    @Autowired
    private PresetPointMapper presetPointMapper;

    @Override
    public Long insertPresetPoint(PresetPoint presetPoint) {
        presetPointMapper.insertPresetPoint(presetPoint);
        return presetPoint.getId();
    }
    @Override
    public int updatePresetPoint(PresetPoint presetPoint) {
        return presetPointMapper.updatePresetPoint(presetPoint);
    }

    @Override
    public PresetPoint queryAllByLimit(PresetPoint presetPoint) {
        return presetPointMapper.queryAllByLimit(presetPoint);
    }
}
