package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.dto.GunmachineDTO;
import com.zzy.sms.stationmonitoringbanckend.entity.Gunmachine;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface GunmachineCameraMapper {

    List<GunmachineDTO> getAllGunmachine();
    List<GunmachineDTO> search(Long cameraId, Long trackId);
}
