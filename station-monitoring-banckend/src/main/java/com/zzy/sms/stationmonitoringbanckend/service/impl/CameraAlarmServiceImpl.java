package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.zzy.sms.stationmonitoringbanckend.dto.CameraAlarmDTO;
import com.zzy.sms.stationmonitoringbanckend.entity.CameraAlarm;
import com.zzy.sms.stationmonitoringbanckend.mapper.CameraAlarmDTOMapper;
import com.zzy.sms.stationmonitoringbanckend.mapper.CameraAlarmMapper;
import com.zzy.sms.stationmonitoringbanckend.service.CameraAlarmService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-30 21:46
 **/
@Service
public class CameraAlarmServiceImpl implements CameraAlarmService {

    @Autowired
    private CameraAlarmDTOMapper cameraAlarmDTOMapper;
    @Autowired
    private CameraAlarmMapper cameraAlarmMapper;

    @Override
    public List<CameraAlarmDTO> getAllCameraAlarm() {
        return cameraAlarmDTOMapper.getAllCameraAlarm();
    }

    @Override
    public List<CameraAlarmDTO> getUndisposedCameraAlarm() {
        return cameraAlarmDTOMapper.getUndisposedCameraAlarm();
    }

    @Override
    public int updateCameraAlarmById(Long id, Long userId, Date dealDate) {
        return cameraAlarmMapper.updateCameraAlarmById(id, userId, dealDate);
    }

    @Override
    public int insertCameraAlarm(CameraAlarm cameraAlarm) {
        return cameraAlarmMapper.insertCameraAlarm(cameraAlarm);
    }

    @Override
    public List<CameraAlarmDTO> search(String cameraName, int day, String type) {
        // 当前时间
        Date now = new Date();

        // 计算 day 天前的时间
        LocalDate localDate = now.toInstant()
                .atZone(ZoneId.systemDefault())
                .toLocalDate()
                .minusDays(day);
        Date startDate = Date.from(localDate.atStartOfDay(ZoneId.systemDefault()).toInstant());
        List<CameraAlarmDTO> list = null;
        if(type.equals("1")) {
            list = cameraAlarmDTOMapper.getAllCameraAlarm();    //传入1代表针对所有的摄像头警告进行搜索
        }else {
            list = cameraAlarmDTOMapper.getUndisposedCameraAlarm();   //传入其他值针对未处理的摄像头警告进行搜索
        }
        // 查询所有数据（你也可以优化为数据库层做条件筛选）
        // 条件筛选
        Stream<CameraAlarmDTO> stream = list.stream();

        if (day > 0) {
            stream = stream.filter(item -> item.getCreateTime().after(startDate) && item.getCreateTime().before(now));
        }

        if (cameraName != null && !cameraName.trim().isEmpty()) {
            stream = stream.filter(item -> item.getCameraName().equals(cameraName));
        }

        return stream.collect(Collectors.toList());
    }


    @Override
    public List<Map<String, Integer>> getCameraAlarmByDay() {
        return cameraAlarmMapper.getCameraAlarmByDay();
    }

}
