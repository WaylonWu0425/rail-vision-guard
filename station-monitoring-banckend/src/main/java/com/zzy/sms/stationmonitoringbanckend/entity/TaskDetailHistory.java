package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;

import java.util.Date;

/**
 * @description: 任务详细历史记录
 * @author: zzy
 * @create: 2025-04-28 16:04
 **/
@Data
public class TaskDetailHistory {
    private Long historyId;
    private Long taskId;
    private String title;
    private String type;
    private String priority;
    private String status;
    private Date statusTime;
    private String feedback;
}
