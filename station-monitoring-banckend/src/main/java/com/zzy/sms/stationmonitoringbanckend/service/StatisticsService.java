package com.zzy.sms.stationmonitoringbanckend.service;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * 统计服务接口
 */
public interface StatisticsService {

    /**
     * 获取设备运行统计数据
     * @param startTime 开始时间
     * @param endTime 结束时间
     * @return 设备运行统计数据
     */
    Map<String, Object> getDeviceRunningStats(LocalDateTime startTime, LocalDateTime endTime);

    /**
     * 获取报警统计数据
     * @param startTime 开始时间
     * @param endTime 结束时间
     * @return 报警统计数据
     */
    Map<String, Object> getAlarmStats(LocalDateTime startTime, LocalDateTime endTime);

    /**
     * 获取任务统计数据
     * @param startTime 开始时间
     * @param endTime 结束时间
     * @return 任务统计数据
     */
    Map<String, Object> getTaskStats(LocalDateTime startTime, LocalDateTime endTime);

    /**
     * 导出统计报表为PDF格式
     * @param startTime 开始时间
     * @param endTime 结束时间
     * @param reportType 报表类型：1-设备运行报表 2-报警信息报表 3-任务完成报表 4-综合统计报表
     * @return PDF二进制数据
     * @throws Exception 导出过程中可能出现的异常
     */
    byte[] exportStatisticsPDF(LocalDateTime startTime, LocalDateTime endTime, String reportType) throws Exception;

    /**
     * 导出统计报表为Excel格式
     * @param startTime 开始时间
     * @param endTime 结束时间
     * @param reportType 报表类型：1-设备运行报表 2-报警信息报表 3-任务完成报表 4-综合统计报表
     * @return Excel二进制数据
     * @throws Exception 导出过程中可能出现的异常
     */
    byte[] exportStatisticsExcel(LocalDateTime startTime, LocalDateTime endTime, String reportType) throws Exception;
}