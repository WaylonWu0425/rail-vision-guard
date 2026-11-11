package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;

import java.io.Serializable;

/**
 * (Gunmachine)实体类
 *
 * @author makejava
 * @since 2025-03-06 20:47:42
 */

@Data
public class Gunmachine implements Serializable {
    private static final long serialVersionUID = -72284949617990772L;
/**
     * 预置点id
     */
    private Long id;
/**
     * 股道id
     */
    private Integer trackId;
/**
     * 摄像头id
     */
    private Long cameraId;
/**
     * 小范围
     */
    private Integer smallRange;
/**
     * 大范围
     */
    private Integer wideRange;

}

