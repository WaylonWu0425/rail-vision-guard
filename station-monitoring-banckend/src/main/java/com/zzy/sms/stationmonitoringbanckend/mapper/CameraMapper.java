package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.entity.BallCamera;
import com.zzy.sms.stationmonitoringbanckend.entity.Camera;
import com.zzy.sms.stationmonitoringbanckend.entity.GunCamera;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.util.List;
@Mapper
public interface CameraMapper {
    @Select("select * from camera")
    List<Camera> getAllCameras();
    @Select("select * from camera where type = 0")
    List<Camera> getBallmachineCameras();
    @Select("select * from camera where type = 1")
    List<Camera> getGunmachineCameras();
    Camera queryAllByLimit(Camera camera);
    int insertCamera(Camera camera);
    int updateCameraById(Camera camera);
    int deleteCameraById(Long id);
    @Select("select * from camera where name like concat('%', #{keyword}, '%')")
    List<Camera> searchCamera(String keyword);
    @Select("select * from camera where name like concat('%', #{cameraName}, '%')")
    List<Camera> getCameraByName(String cameraName);
    @Select("select count(*) from camera")
    int countAllCamera();
    @Select("select * from camera where ip = #{ip}")
    Camera getCameraByIp(String ip);
    @Update("UPDATE camera SET status = #{status} WHERE id = #{id}")
    void updateStatus(Long id, Byte status);
    @Select("select * from camera where id = #{id}")
    Camera getCameraById(Long id);


}
