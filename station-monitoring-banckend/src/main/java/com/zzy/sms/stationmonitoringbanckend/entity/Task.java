package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;

import java.util.Date;

/**
 * @description: 任务实体类
 * @author: zzy
 * @create: 2025-04-23 16:52
 **/

@Data
public class Task {
    private Long id;
    private String title;
    private String description;
    private String type;
    private String priority;
    private String status;
    private Long createById;
    private Long assignedToId;
    private Date createTime;
    private Date endTime;
    private Date startTime;
    private Date finishTime;
    private String operationFeedback;
    private String reviewFeedback;
    private String createByUsername;
    private String assignedToUsername;
    private String dealByUsername;
}
