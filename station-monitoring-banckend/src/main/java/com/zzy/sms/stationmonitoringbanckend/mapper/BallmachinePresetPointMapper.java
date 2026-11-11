package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.dto.BallmachineDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface BallmachinePresetPointMapper {

    List<BallmachineDTO> getAllBallmachine();
    List<BallmachineDTO> search(Long cameraId, Long trackId);

}
