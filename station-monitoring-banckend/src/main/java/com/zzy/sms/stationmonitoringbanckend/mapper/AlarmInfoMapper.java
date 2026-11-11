package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.entity.AlarmInfo;
import org.apache.ibatis.annotations.Update;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Date;
import java.util.List;

public interface AlarmInfoMapper {

    List<AlarmInfo> getAllAlarmInfo();
    List<AlarmInfo> getUndisposedAlarmInfo();
    @Update("UPDATE alarm_info SET deal_flag = 1, deal_user_id = #{userId}, deal_time = #{dealTime} WHERE id = #{id}")
    int updateAlarmInfoById(Long id, Long userId, Date dealTime);

    // 统计时间范围内的总报警次数
    int countByTimeRange(LocalDateTime startTime, LocalDateTime endTime);

    // 统计时间范围内已处理的报警次数
    int countHandledByTimeRange(LocalDateTime startTime, LocalDateTime endTime);

    // 统计指定日期的报警次数
    int countByDate(LocalDate date);
    //通过日期和处理状态统计报警次数
    int countAlarmsByTimeRangeAndStatus(LocalDateTime startTime, LocalDateTime endTime, String dealFlag);
}
