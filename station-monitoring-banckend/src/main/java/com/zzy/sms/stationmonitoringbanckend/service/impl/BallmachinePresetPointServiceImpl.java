package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.zzy.sms.stationmonitoringbanckend.dto.BallmachineDTO;
import com.zzy.sms.stationmonitoringbanckend.mapper.BallmachinePresetPointMapper;
import com.zzy.sms.stationmonitoringbanckend.service.BallmachinePresetPointService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-04 15:21
 **/
@Service
public class BallmachinePresetPointServiceImpl implements BallmachinePresetPointService {
    @Autowired
    private BallmachinePresetPointMapper ballmachinePresetPointMapper;
    @Override
    public List<BallmachineDTO> getAllBallmachine() {
        return ballmachinePresetPointMapper.getAllBallmachine();
    }

    @Override
    public List<BallmachineDTO> search(Long cameraId, Long trackId) {
        return ballmachinePresetPointMapper.search(cameraId, trackId);
    }
}
