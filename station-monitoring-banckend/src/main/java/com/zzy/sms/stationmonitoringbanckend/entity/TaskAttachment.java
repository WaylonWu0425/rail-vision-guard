package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;

import java.util.Date;

/**
 * @description: 任务附件
 * @author: zzy
 * @create: 2025-04-27 22:31
 **/
@Data
public class TaskAttachment {
    private Long id;

    private Long taskId;

    private String name;

    private String filePath;

    private Date uploadTime;
}
