package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;

import java.util.Date;

/**
 * @description: 任务操作历史记录实体
 * @author: zzy
 * @create: 2025-04-27 15:32
 **/
@Data
public class TaskHistory {
    private Long id;
    private Long taskId;
    private String status;
    private Date statusTime;
    private String feedback;
}
