package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;

import java.util.Date;
import java.io.Serializable;

/**
 * (CameraAlarm)实体类
 *
 * @author makejava
 * @since 2025-03-30 21:14:52
 */

@Data
public class CameraAlarm implements Serializable {
    private static final long serialVersionUID = 843881543747168763L;
/**
     * id
     */
    private Long id;
/**
     * 摄像头id
     */
    private Long cameraId;
/**
     * 处理人id
     */
    private Long userId;
/**
     * 报警时间
     */
    private Date createTime;
    private Date dealTime;
/**
     * 处理状态，0未处理，1已处理
     */
    private String dealFlag;
    private String alarm_date;
    private int alarm_count;
    public CameraAlarm(){}


}

