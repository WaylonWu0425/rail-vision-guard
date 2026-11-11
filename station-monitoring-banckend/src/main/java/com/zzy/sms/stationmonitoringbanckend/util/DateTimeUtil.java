package com.zzy.sms.stationmonitoringbanckend.util;

import org.springframework.stereotype.Component;

import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Date;

/**
 * @description: 时间格式化
 * @author: zzy
 * @create: 2025-01-20 23:39
 **/
@Component
public class DateTimeUtil {
    public Date getCurrentTime() {
        Date date = null;
        try {
            // 获取当前时间
            LocalDateTime currentTime = LocalDateTime.now();
            // 定义时间格式
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
            // 将 LocalDateTime 格式化为字符串
            String formattedTime = currentTime.format(formatter);
            // 将格式化后的时间字符串转换为 LocalDateTime 对象
            LocalDateTime parsedDateTime = LocalDateTime.parse(formattedTime, formatter);
            // 将 LocalDateTime 转换为 Date 类型
            date = Timestamp.valueOf(parsedDateTime);
        } catch (Exception e) {
            System.out.println("时间异常:" + e.getMessage());
        }
        return date;
    }
}
