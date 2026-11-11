package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;

import java.io.Serializable;

/**
 * (PresetPoint)实体类
 *
 * @author makejava
 * @since 2025-03-05 15:54:45
 */
@Data
public class PresetPoint implements Serializable {
    private static final long serialVersionUID = 874495807887596566L;
/**
     *  预置点id
     */
    private Long id;
/**
     * 水平坐标
     */
    private Integer panPosition;
/**
     * 垂直距离
     */
    private Integer tiltPosition;
/**
     * 变焦系数
     */
    private Integer zoom;
/**
     * 最小范围
     */
    private Integer smallRange;
/**
     * 最高范围
     */
    private Integer wideRange;

}

