package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.itextpdf.text.*;
import com.itextpdf.text.pdf.PdfPCell;
import com.itextpdf.text.pdf.PdfPTable;
import com.itextpdf.text.pdf.PdfWriter;
import com.zzy.sms.stationmonitoringbanckend.entity.Camera;
import com.zzy.sms.stationmonitoringbanckend.entity.Task;
import com.zzy.sms.stationmonitoringbanckend.mapper.*;
import com.zzy.sms.stationmonitoringbanckend.service.StatisticsService;
import lombok.extern.slf4j.Slf4j;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.FillPatternType;
import org.apache.poi.ss.usermodel.IndexedColors;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.xssf.usermodel.XSSFCellStyle;
import org.apache.poi.xssf.usermodel.XSSFFont;
import org.apache.poi.xssf.usermodel.XSSFSheet;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;


import java.io.ByteArrayOutputStream;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import com.itextpdf.text.Document;
import com.itextpdf.text.Element;
import com.itextpdf.text.Font;
import com.itextpdf.text.PageSize;
import com.itextpdf.text.Paragraph;
import com.itextpdf.text.Phrase;
import com.itextpdf.text.pdf.BaseFont;
import com.itextpdf.text.pdf.PdfPCell;
import com.itextpdf.text.pdf.PdfPTable;
import com.itextpdf.text.pdf.PdfWriter;
import com.itextpdf.text.BaseColor;

/**
 * @description:
 * @author: zzy
 * @create: 2025-04-07 17:38
 **/
@Service
@Slf4j
public class StatisticsServiceImpl implements StatisticsService {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Autowired
    private CameraMapper cameraMapper;

    @Autowired
    private AlarmInfoMapper alarmInfoMapper;

    @Autowired
    private CameraAlarmMapper cameraAlarmMapper;

    @Autowired
    private TaskMapper taskMapper;


    // Redis key前缀
    private static final String DEVICE_STATS_KEY = "stats:device:";
    private static final String ALARM_STATS_KEY = "stats:alarm:";
    private static final String TASK_STATS_KEY = "stats:task:";

    // 缓存过期时间（1小时）
    private static final long CACHE_EXPIRE_TIME = 3600;
    @Override
    public Map<String, Object> getDeviceRunningStats(LocalDateTime startTime, LocalDateTime endTime) {
        // 尝试从Redis获取数据
        String key = DEVICE_STATS_KEY + startTime + ":" + endTime;
        Object cachedData = redisTemplate.opsForValue().get(key);

        if (cachedData == null) {
            // Redis中没有数据，从数据库计算
            Map<String, Object> stats = calculateDeviceRunningStats(startTime, endTime);
            // 存入Redis
            redisTemplate.opsForValue().set(key, stats, CACHE_EXPIRE_TIME, TimeUnit.SECONDS);
            return stats;
        }

        // 直接返回缓存的数据
        return (Map<String, Object>) cachedData;
    }

    private Map<String, Object> calculateDeviceRunningStats(LocalDateTime startTime, LocalDateTime endTime) {
        Map<String, Object> result = new HashMap<>();
        List<Map<String, Object>> deviceStats = new ArrayList<>();

        // 获取所有摄像头
        List<Camera> cameras = cameraMapper.getAllCameras();

        for (Camera camera : cameras) {
            Map<String, Object> deviceStat = new HashMap<>();
            deviceStat.put("deviceName", camera.getName());

            // 计算运行时间（小时）
            LocalDateTime createTime = camera.getCreateTime().toInstant()
                    .atZone(ZoneId.systemDefault())
                    .toLocalDateTime();
            long runningTime = ChronoUnit.HOURS.between(createTime, LocalDateTime.now());
            deviceStat.put("runningTime", runningTime);

            // 获取指定时间范围内的故障次数
            int failureCount = cameraAlarmMapper.failureCount(camera.getId(), startTime, endTime);
            deviceStat.put("failureCount", failureCount);

            // 计算故障率
            double failureRate = runningTime > 0 ? (failureCount * 100.0 / runningTime) : 0;
            deviceStat.put("failureRate", String.format("%.2f%%", failureRate));

            // 当前状态
            deviceStat.put("status", camera.getStatus());

            deviceStats.add(deviceStat);
        }
        result.put("deviceRunningData", deviceStats);
        return result;
    }

    @Override
    public Map<String, Object> getAlarmStats(LocalDateTime startTime, LocalDateTime endTime) {
        String key = ALARM_STATS_KEY + startTime + ":" + endTime;
        Object cachedData = redisTemplate.opsForValue().get(key);

        if (cachedData == null) {
            Map<String, Object> stats = calculateAlarmStats(startTime, endTime);
            redisTemplate.opsForValue().set(key, stats, CACHE_EXPIRE_TIME, TimeUnit.SECONDS);
            return stats;
        }

        return (Map<String, Object>) cachedData;
    }

    private Map<String, Object> calculateAlarmStats(LocalDateTime startTime, LocalDateTime endTime) {
        Map<String, Object> result = new HashMap<>();
        List<Map<String, Object>> alarmStats = new ArrayList<>();

        // 1. 统计危险报警（alarm_info表）
        Map<String, Object> dangerAlarmStat = new HashMap<>();
        dangerAlarmStat.put("alarmType", "危险报警");

        // 获取时间范围内的总报警次数（dealFlag为null表示查询所有）
        int dangerTotalCount = alarmInfoMapper.countAlarmsByTimeRangeAndStatus(startTime, endTime, null);
        dangerAlarmStat.put("alarmCount", dangerTotalCount);

        // 获取已处理的报警次数（deal_flag = 1）
        int dangerHandledCount = alarmInfoMapper.countAlarmsByTimeRangeAndStatus(startTime, endTime, "1");
        dangerAlarmStat.put("handledCount", dangerHandledCount);

        // 计算未处理的报警次数（deal_flag = 0）
        int dangerUnhandledCount = dangerTotalCount - dangerHandledCount;
        dangerAlarmStat.put("unhandledCount", dangerUnhandledCount);

        // 计算处理率
        double dangerHandlingRate = dangerTotalCount > 0 ?
                (dangerHandledCount * 100.0 / dangerTotalCount) : 0;
        dangerAlarmStat.put("handlingRate", String.format("%.1f%%", dangerHandlingRate));

        alarmStats.add(dangerAlarmStat);

        // 2. 统计摄像头警告（camera_alarm表）
        Map<String, Object> cameraAlarmStat = new HashMap<>();
        cameraAlarmStat.put("alarmType", "摄像头警告");

        // 获取时间范围内的总报警次数（dealFlag为null表示查询所有）
        int cameraTotalCount = cameraAlarmMapper.countAlarmsByTimeRangeAndStatus(startTime, endTime, null);
        cameraAlarmStat.put("alarmCount", cameraTotalCount);

        // 获取已处理的报警次数（deal_flag = '1'）
        int cameraHandledCount = cameraAlarmMapper.countAlarmsByTimeRangeAndStatus(startTime, endTime, "1");
        cameraAlarmStat.put("handledCount", cameraHandledCount);

        // 计算未处理的报警次数（deal_flag = '0'）
        int cameraUnhandledCount = cameraTotalCount - cameraHandledCount;
        cameraAlarmStat.put("unhandledCount", cameraUnhandledCount);

        // 计算处理率
        double cameraHandlingRate = cameraTotalCount > 0 ?
                (cameraHandledCount * 100.0 / cameraTotalCount) : 0;
        cameraAlarmStat.put("handlingRate", String.format("%.1f%%", cameraHandlingRate));

        alarmStats.add(cameraAlarmStat);

        // 添加近7天报警趋势数据
        List<Map<String, Object>> trendData = calculateAlarmTrend();
        result.put("alarmStatsData", alarmStats);
        result.put("alarmTrendData", trendData);

        return result;
    }

    // 计算报警趋势
    private List<Map<String, Object>> calculateAlarmTrend() {
        List<Map<String, Object>> trendData = new ArrayList<>();
        LocalDate today = LocalDate.now();

        // 获取最近7天的日期
        for (int i = 6; i >= 0; i--) {
            LocalDate date = today.minusDays(i);
            String dateStr = date.format(DateTimeFormatter.ofPattern("M/d"));

            Map<String, Object> dailyStats = new HashMap<>();
            dailyStats.put("date", dateStr);

            // 统计当天的危险报警数量
            int dangerAlarmCount = alarmInfoMapper.countByDate(date);
            dailyStats.put("dangerAlarmCount", dangerAlarmCount);

            // 统计当天的摄像头警告数量
            int cameraAlarmCount = cameraAlarmMapper.countByDate(date);
            dailyStats.put("cameraAlarmCount", cameraAlarmCount);

            trendData.add(dailyStats);
        }

        return trendData;
    }

    @Override
    public Map<String, Object> getTaskStats(LocalDateTime startTime, LocalDateTime endTime) {
        String key = TASK_STATS_KEY + startTime + ":" + endTime;
        Object cachedData = redisTemplate.opsForValue().get(key);

        if (cachedData == null) {
            Map<String, Object> stats = calculateTaskStats(startTime, endTime);
            redisTemplate.opsForValue().set(key, stats, CACHE_EXPIRE_TIME, TimeUnit.SECONDS);
            return stats;
        }

        return (Map<String, Object>) cachedData;
    }

    private Map<String, Object> calculateTaskStats(LocalDateTime startTime, LocalDateTime endTime) {
        Map<String, Object> result = new HashMap<>();
        List<Map<String, Object>> taskStats = new ArrayList<>();

        // 定义所有任务类型
        String[] taskTypes = {"0", "1", "2", "3"}; // 日常巡检、维修任务、异常处理、设备安装

        // 获取指定时间范围内的所有任务（基于create_time）
        List<Task> tasks = taskMapper.getTasksByCreateTimeRange(startTime, endTime);
        Map<String, List<Task>> tasksByType = tasks.stream()
                .collect(Collectors.groupingBy(Task::getType));

        // 统计每种类型的任务
        for (String type : taskTypes) {
            Map<String, Object> stat = new HashMap<>();
            stat.put("taskType", getTaskTypeName(type));

            // 获取当前类型的任务列表，如果不存在则使用空列表
            List<Task> typeTasks = tasksByType.getOrDefault(type, new ArrayList<>());

            // 设置总任务数
            stat.put("totalTasks", typeTasks.size());

            // 计算已完成任务数（status = 4）
            long completedTasks = typeTasks.stream()
                    .filter(task -> "4".equals(task.getStatus()))
                    .count();
            stat.put("completedTasks", completedTasks);

            // 计算完成率
            double completionRate = typeTasks.size() > 0 ?
                    (completedTasks * 100.0 / typeTasks.size()) : 0;
            stat.put("completionRate", String.format("%.1f%%", completionRate));

            // 计算平均耗时（使用start_time和finish_time）
            double avgDuration = typeTasks.stream()
                    .filter(task -> task.getStartTime() != null && task.getFinishTime() != null)
                    .mapToLong(task -> {
                        LocalDateTime start = task.getStartTime().toInstant()
                                .atZone(ZoneId.systemDefault())
                                .toLocalDateTime();
                        LocalDateTime finish = task.getFinishTime().toInstant()
                                .atZone(ZoneId.systemDefault())
                                .toLocalDateTime();
                        return ChronoUnit.MINUTES.between(start, finish);
                    })
                    .average()
                    .orElse(0);
            stat.put("avgDuration", String.format("%.1f", avgDuration));

            taskStats.add(stat);
        }

        result.put("taskStatsData", taskStats);
        return result;
    }

    private String getTaskTypeName(String type) {
        switch (type) {
            case "0": return "日常巡检";
            case "1": return "维修任务";
            case "2": return "异常处理";
            case "3": return "设备安装";
            default: return "未知类型";
        }
    }

    @Override
    public byte[] exportStatisticsPDF(LocalDateTime startTime, LocalDateTime endTime, String reportType) throws Exception {
        // 根据报表类型获取相应的统计数据
        Map<String, Object> data = getReportDataByType(startTime, endTime, reportType);

        // 加载中文字体
        BaseFont baseFont;
        try {
            // 首先尝试从resources/fonts目录加载字体
            // 注意：需要确保在resources/fonts目录下放置simsun.ttf文件
            baseFont = BaseFont.createFont("fonts/simsun.ttf", BaseFont.IDENTITY_H, BaseFont.EMBEDDED);
            log.info("成功从classpath加载中文字体");
        } catch (Exception e) {
            log.error("无法从classpath加载字体: {}", e.getMessage());
            try {
                // 尝试使用Windows系统字体
                baseFont = BaseFont.createFont("C:/Windows/Fonts/simsun.ttc,0", BaseFont.IDENTITY_H, BaseFont.EMBEDDED);
                log.info("成功从系统字体目录加载中文字体");
            } catch (Exception e2) {
                log.error("无法加载Windows系统字体: {}", e2.getMessage());
                try {
                    // 尝试直接使用字体名称
                    baseFont = BaseFont.createFont("STSong-Light", "UniGB-UCS2-H", BaseFont.NOT_EMBEDDED);
                    log.info("成功使用预定义字体名称加载中文字体");
                } catch (Exception e3) {
                    log.error("无法加载预定义字体: {}", e3.getMessage());
                    // 最后使用默认字体
                    baseFont = BaseFont.createFont(BaseFont.HELVETICA, BaseFont.WINANSI, BaseFont.NOT_EMBEDDED);
                    log.warn("所有中文字体加载尝试失败，使用默认字体，中文可能无法正确显示");
                }
            }
        }
        
        Font titleFont = new Font(baseFont, 18, Font.BOLD);
        Font normalFont = new Font(baseFont, 12);
        Font headerFont = new Font(baseFont, 12, Font.BOLD);

        // 创建一个Document对象
        Document document = new Document(PageSize.A4);
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        PdfWriter writer = PdfWriter.getInstance(document, baos);

        document.open();

        // 添加标题
        String title = getReportTitle(reportType);
        Paragraph titleParagraph = new Paragraph(title, titleFont);
        titleParagraph.setAlignment(Element.ALIGN_CENTER);
        document.add(titleParagraph);

        // 添加日期范围信息
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        String dateInfo = "统计时间范围: " + startTime.format(formatter) + " 至 " + endTime.format(formatter);
        Paragraph dateInfoParagraph = new Paragraph(dateInfo, normalFont);
        dateInfoParagraph.setAlignment(Element.ALIGN_CENTER);
        document.add(dateInfoParagraph);

        document.add(new Paragraph(" ", normalFont)); // 空行

        // 根据报表类型生成不同的内容
        if ("1".equals(reportType)) {
            // 设备运行报表
            addDeviceRunningReportContent(document, data, normalFont, headerFont);
        } else if ("2".equals(reportType)) {
            // 报警信息报表
            addAlarmStatsReportContent(document, data, normalFont, headerFont);
        } else if ("3".equals(reportType)) {
            // 任务完成报表
            addTaskStatsReportContent(document, data, normalFont, headerFont);
        } else if ("4".equals(reportType)) {
            // 综合统计报表
            addComprehensiveReportContent(document, startTime, endTime, normalFont, headerFont, titleFont);
        }

        document.close();
        return baos.toByteArray();
    }

    @Override
    public byte[] exportStatisticsExcel(LocalDateTime startTime, LocalDateTime endTime, String reportType) throws Exception {
        // 根据报表类型获取相应的统计数据
        Map<String, Object> data = getReportDataByType(startTime, endTime, reportType);

        // 创建Excel工作簿
        XSSFWorkbook workbook = new XSSFWorkbook();

        // 创建工作表
        String sheetName = getReportTitle(reportType);
        XSSFSheet sheet = workbook.createSheet(sheetName);

        // 设置表头样式
        XSSFCellStyle headerStyle = workbook.createCellStyle();
        headerStyle.setFillForegroundColor(IndexedColors.GREY_25_PERCENT.getIndex());
        headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
        XSSFFont font = workbook.createFont();
        font.setBold(true);
        headerStyle.setFont(font);

        // 创建标题行
        Row titleRow = sheet.createRow(0);
        Cell titleCell = titleRow.createCell(0);
        titleCell.setCellValue(getReportTitle(reportType));

        // 创建日期信息行
        Row dateRow = sheet.createRow(1);
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        String dateInfo = "统计时间范围: " + startTime.format(formatter) + " 至 " + endTime.format(formatter);
        Cell dateCell = dateRow.createCell(0);
        dateCell.setCellValue(dateInfo);

        // 空行
        sheet.createRow(2);

        // 根据报表类型生成不同的内容
        if ("1".equals(reportType)) {
            // 设备运行报表
            addDeviceRunningExcelContent(sheet, headerStyle, data, 3);
        } else if ("2".equals(reportType)) {
            // 报警信息报表
            addAlarmStatsExcelContent(sheet, headerStyle, data, 3);
        } else if ("3".equals(reportType)) {
            // 任务完成报表
            addTaskStatsExcelContent(sheet, headerStyle, data, 3);
        } else if ("4".equals(reportType)) {
            // 综合统计报表
            addComprehensiveExcelContent(sheet, headerStyle, startTime, endTime, 3);
        }

        // 自动调整列宽
        for (int i = 0; i < 10; i++) {
            sheet.autoSizeColumn(i);
        }

        // 输出到字节数组
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        workbook.write(baos);
        workbook.close();

        return baos.toByteArray();
    }

    // 根据报表类型获取相应的数据
    private Map<String, Object> getReportDataByType(LocalDateTime startTime, LocalDateTime endTime, String reportType) {
        switch (reportType) {
            case "1": // 设备运行报表
                return getDeviceRunningStats(startTime, endTime);
            case "2": // 报警信息报表
                return getAlarmStats(startTime, endTime);
            case "3": // 任务完成报表
                return getTaskStats(startTime, endTime);
            case "4": // 综合统计报表
                // 综合所有统计数据
                Map<String, Object> comprehensiveData = new HashMap<>();
                comprehensiveData.putAll(getDeviceRunningStats(startTime, endTime));
                comprehensiveData.putAll(getAlarmStats(startTime, endTime));
                comprehensiveData.putAll(getTaskStats(startTime, endTime));
                return comprehensiveData;
            default:
                return new HashMap<>();
        }
    }

    // 获取报表标题
    private String getReportTitle(String reportType) {
        switch (reportType) {
            case "1": return "设备运行统计报表";
            case "2": return "报警信息统计报表";
            case "3": return "任务完成统计报表";
            case "4": return "综合统计报表";
            default: return "统计报表";
        }
    }

    // 添加设备运行报表内容到PDF
    private void addDeviceRunningReportContent(Document document, Map<String, Object> data, Font normalFont, Font headerFont) throws DocumentException {
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> deviceRunningData = (List<Map<String, Object>>) data.get("deviceRunningData");

        if (deviceRunningData != null && !deviceRunningData.isEmpty()) {
            PdfPTable table = new PdfPTable(5);
            table.setWidthPercentage(100);
            table.setWidths(new float[]{3, 2, 2, 2, 2});
            addTableHeader(table, new String[]{"设备名称", "运行时间(小时)", "故障次数", "故障率", "当前状态"}, headerFont);
            for (Map<String, Object> deviceData : deviceRunningData) {
                table.addCell(new PdfPCell(new Phrase(deviceData.get("deviceName").toString(), normalFont)));
                table.addCell(new PdfPCell(new Phrase(deviceData.get("runningTime").toString(), normalFont)));
                table.addCell(new PdfPCell(new Phrase(deviceData.get("failureCount").toString(), normalFont)));
                table.addCell(new PdfPCell(new Phrase(deviceData.get("failureRate").toString(), normalFont)));
                table.addCell(new PdfPCell(new Phrase(deviceData.get("status").toString(), normalFont)));
            }
            document.add(table);
        } else {
            document.add(new Paragraph("没有设备运行数据", normalFont));
        }
    }

    // 添加报警信息报表内容到PDF
    private void addAlarmStatsReportContent(Document document, Map<String, Object> data, Font normalFont, Font headerFont) throws DocumentException {
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> alarmStatsData = (List<Map<String, Object>>) data.get("alarmStatsData");
        if (alarmStatsData != null && !alarmStatsData.isEmpty()) {
            PdfPTable table = new PdfPTable(5);
            table.setWidthPercentage(100);
            table.setWidths(new float[]{3, 2, 2, 2, 2});
            addTableHeader(table, new String[]{"报警类型", "报警次数", "已处理", "未处理", "处理率"}, headerFont);
            for (Map<String, Object> alarmData : alarmStatsData) {
                table.addCell(new PdfPCell(new Phrase(alarmData.get("alarmType").toString(), normalFont)));
                table.addCell(new PdfPCell(new Phrase(alarmData.get("alarmCount").toString(), normalFont)));
                table.addCell(new PdfPCell(new Phrase(alarmData.get("handledCount").toString(), normalFont)));
                table.addCell(new PdfPCell(new Phrase(alarmData.get("unhandledCount").toString(), normalFont)));
                table.addCell(new PdfPCell(new Phrase(alarmData.get("handlingRate").toString(), normalFont)));
            }
            document.add(table);
            document.add(new Paragraph(" ", normalFont)); // 空行
            document.add(new Paragraph("报警趋势(近7天)", headerFont));
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> trendData = (List<Map<String, Object>>) data.get("alarmTrendData");
            if (trendData != null && !trendData.isEmpty()) {
                PdfPTable trendTable = new PdfPTable(3);
                trendTable.setWidthPercentage(100);
                addTableHeader(trendTable, new String[]{"日期", "危险报警", "摄像头警告"}, headerFont);
                for (Map<String, Object> trendItem : trendData) {
                    trendTable.addCell(new PdfPCell(new Phrase(trendItem.get("date").toString(), normalFont)));
                    trendTable.addCell(new PdfPCell(new Phrase(trendItem.get("dangerAlarmCount").toString(), normalFont)));
                    trendTable.addCell(new PdfPCell(new Phrase(trendItem.get("cameraAlarmCount").toString(), normalFont)));
                }
                document.add(trendTable);
            }
        } else {
            document.add(new Paragraph("没有报警统计数据", normalFont));
        }
    }

    // 添加任务完成报表内容到PDF
    private void addTaskStatsReportContent(Document document, Map<String, Object> data, Font normalFont, Font headerFont) throws DocumentException {
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> taskStatsData = (List<Map<String, Object>>) data.get("taskStatsData");
        if (taskStatsData != null && !taskStatsData.isEmpty()) {
            PdfPTable table = new PdfPTable(5);
            table.setWidthPercentage(100);
            table.setWidths(new float[]{3, 2, 2, 2, 2});
            addTableHeader(table, new String[]{"任务类型", "总任务数", "已完成", "完成率", "平均耗时(分钟)"}, headerFont);
            for (Map<String, Object> taskData : taskStatsData) {
                table.addCell(new PdfPCell(new Phrase(taskData.get("taskType").toString(), normalFont)));
                table.addCell(new PdfPCell(new Phrase(taskData.get("totalTasks").toString(), normalFont)));
                table.addCell(new PdfPCell(new Phrase(taskData.get("completedTasks").toString(), normalFont)));
                table.addCell(new PdfPCell(new Phrase(taskData.get("completionRate").toString(), normalFont)));
                table.addCell(new PdfPCell(new Phrase(taskData.get("avgDuration").toString(), normalFont)));
            }
            document.add(table);
        } else {
            document.add(new Paragraph("没有任务统计数据", normalFont));
        }
    }

    // 添加综合统计报表内容到PDF
    private void addComprehensiveReportContent(Document document, LocalDateTime startTime, LocalDateTime endTime, Font normalFont, Font headerFont, Font titleFont) throws DocumentException {
        document.add(new Paragraph("一、设备运行统计", headerFont));
        addDeviceRunningReportContent(document, getDeviceRunningStats(startTime, endTime), normalFont, headerFont);
        document.add(new Paragraph(" ", normalFont)); // 空行
        document.add(new Paragraph("二、报警信息统计", headerFont));
        addAlarmStatsReportContent(document, getAlarmStats(startTime, endTime), normalFont, headerFont);
        document.add(new Paragraph(" ", normalFont)); // 空行
        document.add(new Paragraph("三、任务完成统计", headerFont));
        addTaskStatsReportContent(document, getTaskStats(startTime, endTime), normalFont, headerFont);
    }

    // 辅助方法：添加PDF表格表头，使用中文字体
    private void addTableHeader(PdfPTable table, String[] headers, Font headerFont) {
        for (String header : headers) {
            PdfPCell cell = new PdfPCell(new Phrase(header, headerFont));
            cell.setHorizontalAlignment(Element.ALIGN_CENTER);
            cell.setBackgroundColor(BaseColor.LIGHT_GRAY);
            cell.setPadding(5);
            table.addCell(cell);
        }
    }

    // 添加设备运行报表内容到Excel
    private void addDeviceRunningExcelContent(XSSFSheet sheet, XSSFCellStyle headerStyle, Map<String, Object> data, int startRow) {
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> deviceRunningData = (List<Map<String, Object>>) data.get("deviceRunningData");

        if (deviceRunningData != null && !deviceRunningData.isEmpty()) {
            // 添加表头
            Row headerRow = sheet.createRow(startRow);
            String[] headers = {"设备名称", "运行时间(小时)", "故障次数", "故障率", "当前状态"};
            for (int i = 0; i < headers.length; i++) {
                Cell cell = headerRow.createCell(i);
                cell.setCellValue(headers[i]);
                cell.setCellStyle(headerStyle);
            }

            // 添加数据行
            int rowNum = startRow + 1;
            for (Map<String, Object> deviceData : deviceRunningData) {
                Row row = sheet.createRow(rowNum++);
                row.createCell(0).setCellValue(deviceData.get("deviceName").toString());
                row.createCell(1).setCellValue(deviceData.get("runningTime").toString());
                row.createCell(2).setCellValue(deviceData.get("failureCount").toString());
                row.createCell(3).setCellValue(deviceData.get("failureRate").toString());
                row.createCell(4).setCellValue(deviceData.get("status").toString());
            }
        } else {
            Row row = sheet.createRow(startRow);
            row.createCell(0).setCellValue("没有设备运行数据");
        }
    }

    // 添加报警信息报表内容到Excel
    private void addAlarmStatsExcelContent(XSSFSheet sheet, XSSFCellStyle headerStyle, Map<String, Object> data, int startRow) {
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> alarmStatsData = (List<Map<String, Object>>) data.get("alarmStatsData");

        if (alarmStatsData != null && !alarmStatsData.isEmpty()) {
            // 添加表头
            Row headerRow = sheet.createRow(startRow);
            String[] headers = {"报警类型", "报警次数", "已处理", "未处理", "处理率"};
            for (int i = 0; i < headers.length; i++) {
                Cell cell = headerRow.createCell(i);
                cell.setCellValue(headers[i]);
                cell.setCellStyle(headerStyle);
            }

            // 添加数据行
            int rowNum = startRow + 1;
            for (Map<String, Object> alarmData : alarmStatsData) {
                Row row = sheet.createRow(rowNum++);
                row.createCell(0).setCellValue(alarmData.get("alarmType").toString());
                row.createCell(1).setCellValue(alarmData.get("alarmCount").toString());
                row.createCell(2).setCellValue(alarmData.get("handledCount").toString());
                row.createCell(3).setCellValue(alarmData.get("unhandledCount").toString());
                row.createCell(4).setCellValue(alarmData.get("handlingRate").toString());
            }

            // 添加报警趋势数据
            rowNum += 2; // 空两行

            Row titleRow = sheet.createRow(rowNum++);
            titleRow.createCell(0).setCellValue("报警趋势(近7天)");

            @SuppressWarnings("unchecked")
            List<Map<String, Object>> trendData = (List<Map<String, Object>>) data.get("alarmTrendData");

            if (trendData != null && !trendData.isEmpty()) {
                // 添加表头
                Row trendHeaderRow = sheet.createRow(rowNum++);
                String[] trendHeaders = {"日期", "危险报警", "摄像头警告"};
                for (int i = 0; i < trendHeaders.length; i++) {
                    Cell cell = trendHeaderRow.createCell(i);
                    cell.setCellValue(trendHeaders[i]);
                    cell.setCellStyle(headerStyle);
                }

                // 添加数据行
                for (Map<String, Object> trendItem : trendData) {
                    Row row = sheet.createRow(rowNum++);
                    row.createCell(0).setCellValue(trendItem.get("date").toString());
                    row.createCell(1).setCellValue(trendItem.get("dangerAlarmCount").toString());
                    row.createCell(2).setCellValue(trendItem.get("cameraAlarmCount").toString());
                }
            }
        } else {
            Row row = sheet.createRow(startRow);
            row.createCell(0).setCellValue("没有报警统计数据");
        }
    }

    // 添加任务完成报表内容到Excel
    private void addTaskStatsExcelContent(XSSFSheet sheet, XSSFCellStyle headerStyle, Map<String, Object> data, int startRow) {
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> taskStatsData = (List<Map<String, Object>>) data.get("taskStatsData");

        if (taskStatsData != null && !taskStatsData.isEmpty()) {
            // 添加表头
            Row headerRow = sheet.createRow(startRow);
            String[] headers = {"任务类型", "总任务数", "已完成", "完成率", "平均耗时(分钟)"};
            for (int i = 0; i < headers.length; i++) {
                Cell cell = headerRow.createCell(i);
                cell.setCellValue(headers[i]);
                cell.setCellStyle(headerStyle);
            }

            // 添加数据行
            int rowNum = startRow + 1;
            for (Map<String, Object> taskData : taskStatsData) {
                Row row = sheet.createRow(rowNum++);
                row.createCell(0).setCellValue(taskData.get("taskType").toString());
                row.createCell(1).setCellValue(taskData.get("totalTasks").toString());
                row.createCell(2).setCellValue(taskData.get("completedTasks").toString());
                row.createCell(3).setCellValue(taskData.get("completionRate").toString());
                row.createCell(4).setCellValue(taskData.get("avgDuration").toString());
            }
        } else {
            Row row = sheet.createRow(startRow);
            row.createCell(0).setCellValue("没有任务统计数据");
        }
    }

    // 添加综合统计报表内容到Excel
    private void addComprehensiveExcelContent(XSSFSheet sheet, XSSFCellStyle headerStyle, LocalDateTime startTime, LocalDateTime endTime, int startRow) {
        // 设备运行统计
        Row titleRow1 = sheet.createRow(startRow);
        titleRow1.createCell(0).setCellValue("一、设备运行统计");
        Map<String, Object> deviceData = getDeviceRunningStats(startTime, endTime);
        addDeviceRunningExcelContent(sheet, headerStyle, deviceData, startRow + 1);

        // 计算设备运行数据的行数
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> deviceRunningData = (List<Map<String, Object>>) deviceData.get("deviceRunningData");
        int deviceRowsCount = deviceRunningData != null ? deviceRunningData.size() + 3 : 3;

        // 报警信息统计
        int alarmStartRow = startRow + deviceRowsCount + 2;
        Row titleRow2 = sheet.createRow(alarmStartRow);
        titleRow2.createCell(0).setCellValue("二、报警信息统计");
        Map<String, Object> alarmData = getAlarmStats(startTime, endTime);
        addAlarmStatsExcelContent(sheet, headerStyle, alarmData, alarmStartRow + 1);

        // 计算报警数据的行数
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> alarmStatsData = (List<Map<String, Object>>) alarmData.get("alarmStatsData");
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> trendData = (List<Map<String, Object>>) alarmData.get("alarmTrendData");
        int alarmRowsCount = (alarmStatsData != null ? alarmStatsData.size() + 3 : 3) +
                (trendData != null ? trendData.size() + 3 : 3);

        // 任务完成统计
        int taskStartRow = alarmStartRow + alarmRowsCount + 2;
        Row titleRow3 = sheet.createRow(taskStartRow);
        titleRow3.createCell(0).setCellValue("三、任务完成统计");
        addTaskStatsExcelContent(sheet, headerStyle, getTaskStats(startTime, endTime), taskStartRow + 1);
    }

}
