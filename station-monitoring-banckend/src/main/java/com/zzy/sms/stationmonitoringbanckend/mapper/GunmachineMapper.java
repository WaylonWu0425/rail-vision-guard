package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.dto.GunmachineDTO;
import com.zzy.sms.stationmonitoringbanckend.entity.Gunmachine;

import java.util.List;

public interface GunmachineMapper {
    int insertGunmachine(Gunmachine gunmachine);
    int updateGunmachine(Gunmachine gunmachine);
    int deleteById(Long id);
    List<GunmachineDTO> search(Long cameraId, Long trackId);
}
