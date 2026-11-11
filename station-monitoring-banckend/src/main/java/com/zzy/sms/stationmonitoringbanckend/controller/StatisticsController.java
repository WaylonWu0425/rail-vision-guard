package com.zzy.sms.stationmonitoringbanckend.controller;

import com.zzy.sms.stationmonitoringbanckend.mapper.CameraAlarmMapper;
import com.zzy.sms.stationmonitoringbanckend.service.CameraAlarmService;
import com.zzy.sms.stationmonitoringbanckend.service.StatisticsService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @description:
 * @author: zzy
 * @create: 2025-04-07 18:37
 **/

@Slf4j
@RestController
@RequestMapping("/Statistics")
public class StatisticsController {

    @Autowired
    private CameraAlarmService cameraAlarmService;

    @Autowired
    private StatisticsService statisticsService;

    @GetMapping("/getCameraAlarmByDay")
    public ResponseEntity getCameraAlarmByDay() {
        Map<String, Object> response = new HashMap<>();
        List<Map<String, Integer>> alarmStats;
        try {
            alarmStats = cameraAlarmService.getCameraAlarmByDay();
            response.put("success", true);
            response.put("message", "查询成功");
            response.put("data", alarmStats);
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            System.out.println(e);
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/deviceStats")
    public ResponseEntity<?> getDeviceRunningStats(
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startTime,
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endTime) {
        try {
            // 如果只有日期没有时间，则为起始日期添加00:00:00，为结束日期添加23:59:59
            startTime = adjustTimeIfNeeded(startTime, true);
            endTime = adjustTimeIfNeeded(endTime, false);
            
            Map<String, Object> stats = statisticsService.getDeviceRunningStats(startTime, endTime);
            return ResponseEntity.ok(stats);
        } catch (Exception e) {
            log.error("获取设备运行统计数据失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("code", HttpStatus.INTERNAL_SERVER_ERROR.value());
            errorResponse.put("message", "获取设备运行统计数据失败");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    @GetMapping("/alarmStats")
    public ResponseEntity<?> getAlarmStats(
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startTime,
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endTime) {
        try {
            // 如果只有日期没有时间，则为起始日期添加00:00:00，为结束日期添加23:59:59
            startTime = adjustTimeIfNeeded(startTime, true);
            endTime = adjustTimeIfNeeded(endTime, false);
            
            Map<String, Object> stats = statisticsService.getAlarmStats(startTime, endTime);
            return ResponseEntity.ok(stats);
        } catch (Exception e) {
            log.error("获取报警统计数据失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("code", HttpStatus.INTERNAL_SERVER_ERROR.value());
            errorResponse.put("message", "获取报警统计数据失败");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    @GetMapping("/taskStats")
    public ResponseEntity<?> getTaskStats(
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startTime,
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endTime) {
        try {
            // 如果只有日期没有时间，则为起始日期添加00:00:00，为结束日期添加23:59:59
            startTime = adjustTimeIfNeeded(startTime, true);
            endTime = adjustTimeIfNeeded(endTime, false);
            
            Map<String, Object> stats = statisticsService.getTaskStats(startTime, endTime);
            return ResponseEntity.ok(stats);
        } catch (Exception e) {
            log.error("获取任务统计数据失败", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("code", HttpStatus.INTERNAL_SERVER_ERROR.value());
            errorResponse.put("message", "获取任务统计数据失败");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * 导出统计报表为PDF
     * @param startTime 开始时间
     * @param endTime 结束时间
     * @param reportType 报表类型
     * @return PDF文件
     */
    @GetMapping("/exportPDF")
    public ResponseEntity<byte[]> exportStatisticsPDF(
            @RequestParam("startTime") @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startTime,
            @RequestParam("endTime") @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endTime,
            @RequestParam("reportType") String reportType) {
        try {
            // 如果只有日期没有时间，则为起始日期添加00:00:00，为结束日期添加23:59:59
            startTime = adjustTimeIfNeeded(startTime, true);
            endTime = adjustTimeIfNeeded(endTime, false);
            
            byte[] pdfData = statisticsService.exportStatisticsPDF(startTime, endTime, reportType);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_PDF);
            // 使用英文文件名，避免中文编码问题
            String filename = String.format("Statistics_Report_%s_%s.pdf",
                    startTime.toLocalDate().toString().replace("-", ""),
                    endTime.toLocalDate().toString().replace("-", ""));

            // 使用 ISO-8859-1 编码
            headers.add(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=" + filename);
            headers.setCacheControl("must-revalidate, post-check=0, pre-check=0");

            return new ResponseEntity<>(pdfData, headers, HttpStatus.OK);
        } catch (Exception e) {
            e.printStackTrace();
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    /**
     * 导出统计报表为Excel
     * @param startTime 开始时间
     * @param endTime 结束时间
     * @param reportType 报表类型
     * @return Excel文件
     */
    @GetMapping("/exportExcel")
    public ResponseEntity<byte[]> exportStatisticsExcel(
            @RequestParam("startTime") @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startTime,
            @RequestParam("endTime") @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endTime,
            @RequestParam("reportType") String reportType) {
        try {
            // 如果只有日期没有时间，则为起始日期添加00:00:00，为结束日期添加23:59:59
            startTime = adjustTimeIfNeeded(startTime, true);
            endTime = adjustTimeIfNeeded(endTime, false);
            
            byte[] excelData = statisticsService.exportStatisticsExcel(startTime, endTime, reportType);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"));
            // 使用英文文件名，避免中文编码问题
            String filename = String.format("Statistics_Report_%s_%s.xlsx",
                    startTime.toLocalDate().toString().replace("-", ""),
                    endTime.toLocalDate().toString().replace("-", ""));

            headers.add(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=" + filename);
            headers.setCacheControl("must-revalidate, post-check=0, pre-check=0");

            return new ResponseEntity<>(excelData, headers, HttpStatus.OK);
        } catch (Exception e) {
            e.printStackTrace();
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
    
    /**
     * 调整时间
     * 当只有日期没有时间时，为起始时间添加00:00:00，为结束时间添加23:59:59
     *
     * @param dateTime 原始时间
     * @param isStartTime 是否为起始时间
     * @return 调整后的时间
     */
    private LocalDateTime adjustTimeIfNeeded(LocalDateTime dateTime, boolean isStartTime) {
        if (dateTime == null) {
            return null;
        }
        
        // 检查时间部分是否为00:00:00（即只有日期没有时间）
        if (dateTime.getHour() == 0 && dateTime.getMinute() == 0 && dateTime.getSecond() == 0) {
            if (isStartTime) {
                // 起始时间保持00:00:00
                return dateTime;
            } else {
                // 结束时间设置为23:59:59
                return dateTime.withHour(23).withMinute(59).withSecond(59);
            }
        }
        
        return dateTime;
    }
}
