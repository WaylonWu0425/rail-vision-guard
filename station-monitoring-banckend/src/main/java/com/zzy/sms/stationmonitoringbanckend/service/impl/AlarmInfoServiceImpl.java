package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.zzy.sms.stationmonitoringbanckend.entity.AlarmInfo;
import com.zzy.sms.stationmonitoringbanckend.mapper.AlarmInfoMapper;
import com.zzy.sms.stationmonitoringbanckend.service.AlarmInfoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * @description:
 * @author: zzy
 * @create: 2025-04-12 00:07
 **/
@Service
public class AlarmInfoServiceImpl  implements AlarmInfoService {
    @Autowired
    private AlarmInfoMapper alarmInfoMapper;
    @Override
    public List<AlarmInfo> getAllAlarmInfo() {
        return alarmInfoMapper.getAllAlarmInfo();
    }

    @Override
    public List<AlarmInfo> getUndisposedAlarmInfo() {
        return alarmInfoMapper.getUndisposedAlarmInfo();
    }

    public List<AlarmInfo> search(String cameraName, int day, Byte type, String status) {
        // 当前时间
        Date now = new Date();

        // 计算 day 天前的时间
        LocalDate localDate = now.toInstant()
                .atZone(ZoneId.systemDefault())
                .toLocalDate()
                .minusDays(day);
        Date startDate = Date.from(localDate.atStartOfDay(ZoneId.systemDefault()).toInstant());
        List<AlarmInfo> list = null;
        if(status.equals("1")) {
            list = alarmInfoMapper.getAllAlarmInfo();  //传入1代表针对所有的危险警告进行搜索
        }else {
            list = alarmInfoMapper.getUndisposedAlarmInfo();   //传入其他值针对未处理的危险警告进行搜索
        }

        // 查询所有数据（你也可以优化为数据库层做条件筛选）
        // 条件筛选
        Stream<AlarmInfo> stream = list.stream();

        if (day > 0) {
            stream = stream.filter(item -> item.getCreateTime().after(startDate) && item.getCreateTime().before(now));
        }
        //根据摄像头名称筛选
        if (cameraName != null && !cameraName.trim().isEmpty()) {
            stream = stream.filter(item -> item.getCameraName().equals(cameraName));
        }
        //根据警报类型筛选
        if (type != null && type > 0) {
            stream = stream.filter(item -> item.getType() != null && item.getType().equals(type));
        }

        return stream.collect(Collectors.toList());
    }

    @Override
    public int updateAlarmInfoById(Long id, Long userId, Date dealTime) {
        return alarmInfoMapper.updateAlarmInfoById(id, userId, dealTime);
    }
}
