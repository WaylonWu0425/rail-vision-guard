package com.zzy.sms.stationmonitoringbanckend.mapper;


import com.zzy.sms.stationmonitoringbanckend.entity.CameraAlarm;
import org.apache.ibatis.annotations.Mapper;

import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Date;
import java.util.List;
import java.util.Map;


@Mapper
public interface CameraAlarmMapper {
    @Update("UPDATE camera_alarm SET deal_flag = '1', user_id = #{userId}, deal_time = #{dealDate} WHERE id = #{id} ")
    int updateCameraAlarmById(Long id, Long userId, Date dealDate);
    int insertCameraAlarm(CameraAlarm cameraAlarm);
    @Select("SELECT DATE(create_time) AS alarm_date, COUNT(*) AS alarm_count FROM camera_alarm\n" +
            "WHERE\n" +
            "    create_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)\n" +
            "GROUP BY\n" +
            "    alarm_date\n" +
            "ORDER BY\n" +
            " alarm_date;")
    List<Map<String, Integer>> getCameraAlarmByDay();
    @Select("SELECT COUNT(*) FROM camera_alarm WHERE camera_id = #{cameraId} AND create_time BETWEEN #{startTime} AND #{endTime}")
    int failureCount(Long cameraId, LocalDateTime startTime, LocalDateTime endTime);

    // 统计指定日期的报警次数
    int countByDate(LocalDate date);
    //通过日期和处理状态统计报警次数
    int countAlarmsByTimeRangeAndStatus(LocalDateTime startTime, LocalDateTime endTime, String dealFlag);
}

