package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.zzy.sms.stationmonitoringbanckend.dto.GunmachineDTO;
import com.zzy.sms.stationmonitoringbanckend.entity.Gunmachine;
import com.zzy.sms.stationmonitoringbanckend.mapper.GunmachineCameraMapper;
import com.zzy.sms.stationmonitoringbanckend.mapper.GunmachineMapper;
import com.zzy.sms.stationmonitoringbanckend.service.GunmachineService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-06 20:52
 **/

@Service
public class GunmachineServiceImpl implements GunmachineService {

    @Autowired
    private GunmachineCameraMapper gunmachineCameraMapper;

    @Autowired
    private GunmachineMapper gunmachineMapper;

    @Override
    public List<GunmachineDTO> getAllGunmachine() {
        return gunmachineCameraMapper.getAllGunmachine();
    }

    @Override
    public int insertGunmachine(Gunmachine gunmachine) {
        return gunmachineMapper.insertGunmachine(gunmachine);
    }

    @Override
    public int updateGunmachine(Gunmachine gunmachine) {
        return gunmachineMapper.updateGunmachine(gunmachine);
    }

    @Override
    public int deleteById(Long id) {
        return gunmachineMapper.deleteById(id);
    }

    @Override
    public List<GunmachineDTO> search(Long cameraId, Long trackId) {
        return gunmachineCameraMapper.search(cameraId, trackId);
    }
}
