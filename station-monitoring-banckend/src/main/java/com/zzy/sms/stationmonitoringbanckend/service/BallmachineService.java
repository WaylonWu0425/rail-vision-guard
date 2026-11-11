package com.zzy.sms.stationmonitoringbanckend.service;

import com.zzy.sms.stationmonitoringbanckend.dto.GunmachineDTO;
import com.zzy.sms.stationmonitoringbanckend.entity.Ballmachine;

import java.util.List;

public interface BallmachineService {
    int insertBallmachine(Ballmachine ballmachine);
    int updateBallmachine(Ballmachine ballmachine);
    int deleteBallmachineById(Long id);
}
