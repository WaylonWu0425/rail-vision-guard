package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.dto.CameraAlarmDTO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface CameraAlarmDTOMapper {
    List<CameraAlarmDTO> getAllCameraAlarm();
    List<CameraAlarmDTO> getUndisposedCameraAlarm();
}
