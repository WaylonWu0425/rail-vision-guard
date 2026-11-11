package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.entity.Camera;
import com.zzy.sms.stationmonitoringbanckend.entity.GunCamera;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.util.List;

@Mapper
public interface GunCameraMapper {
    @Select("select * from camera where type='1'")
    List<GunCamera> getAllGunCamera();

    @Select("select count(*) from camera where type='1'")
    int getGunCameraCount();

    @Update("UPDATE camera SET status = #{status} WHERE id = #{id} AND type = '1'")
    void updateStatus(Long id, int status);


}
