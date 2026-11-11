package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;

import java.util.Date;
import java.io.Serializable;

/**
 * (AlarmInfo)实体类
 *
 * @author makejava
 * @since 2025-04-12 00:00:41
 */

@Data
public class AlarmInfo implements Serializable {
    private static final long serialVersionUID = 546872091183346636L;
    /**
     * id
     */
    private Long id;
    /**
     * 报警信息
     */
    private String content;
    /**
     * 外键，报警设备id
     */
    private Long cameraId;

    private String cameraName;


    private Byte type;
    /**
     * 0未处理 1已处理
     */
    private Byte dealFlag;
    /**
     * 报警时间
     */
    private Date createTime;
    /**
     * 处理时间
     */
    private Date dealTime;
    /**
     * 外键，处理人id
     */
    private Long dealUserId;

    private String dealUserName;

    /**
     * 0轻度  1中度  2重度
     */
    private Byte level;


}

