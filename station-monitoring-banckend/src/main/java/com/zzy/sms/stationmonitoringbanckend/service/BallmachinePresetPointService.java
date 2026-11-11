package com.zzy.sms.stationmonitoringbanckend.service;

import com.zzy.sms.stationmonitoringbanckend.dto.BallmachineDTO;

import java.util.List;

public interface BallmachinePresetPointService {
    List<BallmachineDTO> getAllBallmachine();
    List<BallmachineDTO> search(Long cameraId, Long trackId);
}
