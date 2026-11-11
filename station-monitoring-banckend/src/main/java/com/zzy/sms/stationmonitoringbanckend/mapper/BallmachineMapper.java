package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.entity.Ballmachine;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface BallmachineMapper {
    int insertBallmachine(Ballmachine ballmachine);
    int updateBallmachine(Ballmachine ballmachine);
    int deleteBallmachineById(Long id);

}
