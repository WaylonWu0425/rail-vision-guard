package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.entity.Switch;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface SwitchMapper {

    @Select("select distinct field, track_id, throat from switch")
    List<Switch> getSwitch();
    int insertSwitch(Switch switchData);
    Switch getSwitchID(Switch switchData);
    int updateSwitch(Switch switchData);
    int deleteById(Long id);
    List<Switch> search(int field, Long trackId, String throat);
}
