package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.entity.PresetPoint;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface PresetPointMapper {
    Long insertPresetPoint(PresetPoint presetPoint);
    int updatePresetPoint(PresetPoint presetPoint);
    PresetPoint queryAllByLimit(PresetPoint presetPoint);
}
