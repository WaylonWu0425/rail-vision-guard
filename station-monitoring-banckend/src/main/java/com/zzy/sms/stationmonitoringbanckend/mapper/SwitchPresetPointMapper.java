package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.entity.SwitchPresetPoint;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface SwitchPresetPointMapper {
    List<SwitchPresetPoint> getSwitchPresetPoint(Long trackId, int field, String throat);

    @Select("select * from switch_preset_point where pan_position = #{panPosition} and tilt_position = #{tiltPosition} and zoom = #{zoom}")
    List<SwitchPresetPoint> checkSwitchPresetPoint(int panPosition, int tiltPosition, int zoom);

    Long insertSwitchPresetPoint(SwitchPresetPoint switchPresetPoint);
}
