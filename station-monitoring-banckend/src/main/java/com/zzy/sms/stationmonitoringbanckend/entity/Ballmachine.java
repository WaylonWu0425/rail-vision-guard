package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;

import java.io.Serializable;

/**
 * (Ballmachine)实体类
 *
 * @author makejava
 * @since 2025-03-05 15:47:19
 */
@Data
public class Ballmachine implements Serializable {
    private static final long serialVersionUID = 876631541198672741L;

    private Long id;
/**
     * 股道id
     */
    private Long trackId;
/**
     * 摄像头id
     */
    private Long cameraId;
/**
     * 预置点id
     */
    private Long presetPointId;


}

