package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.zzy.sms.stationmonitoringbanckend.dto.GunmachineDTO;
import com.zzy.sms.stationmonitoringbanckend.entity.Ballmachine;
import com.zzy.sms.stationmonitoringbanckend.mapper.BallmachineMapper;
import com.zzy.sms.stationmonitoringbanckend.service.BallmachineService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-05 17:21
 **/


@Service
public class BallmachineServiceImpl implements BallmachineService {

    @Autowired
    private BallmachineMapper ballmachineMapper;
    @Override
    public int insertBallmachine(Ballmachine ballmachine) {
        return ballmachineMapper.insertBallmachine(ballmachine);
    }
    @Override
    public int updateBallmachine(Ballmachine ballmachine) {
        return ballmachineMapper.updateBallmachine(ballmachine);
    }

    @Override
    public int deleteBallmachineById(Long id) {
        return ballmachineMapper.deleteBallmachineById(id);
    }
}
