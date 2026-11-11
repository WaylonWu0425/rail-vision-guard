package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.entity.BallCamera;
import com.zzy.sms.stationmonitoringbanckend.entity.Camera;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.util.List;

@Mapper
public interface BallCameraMapper {
    @Select("select * from camera where type='0'")
    List<BallCamera> getAllBallCamera();
    @Select("select count(*) from camera where type='0'")
    int getBallCameraCount();
    @Update("UPDATE camera SET status = #{status} WHERE id = #{id} AND type = '0'")
    void updateStatus(Long id, Byte status);

}
