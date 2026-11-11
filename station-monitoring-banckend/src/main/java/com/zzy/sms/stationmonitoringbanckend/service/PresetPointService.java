package com.zzy.sms.stationmonitoringbanckend.service;

import com.zzy.sms.stationmonitoringbanckend.entity.PresetPoint;

public interface PresetPointService {
    Long insertPresetPoint(PresetPoint presetPoint);
    int updatePresetPoint(PresetPoint presetPoint);
    PresetPoint queryAllByLimit(PresetPoint presetPoint);
}
