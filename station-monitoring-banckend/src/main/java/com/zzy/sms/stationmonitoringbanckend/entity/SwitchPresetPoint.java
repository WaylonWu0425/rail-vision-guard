package com.zzy.sms.stationmonitoringbanckend.entity;

import java.io.Serializable;

/**
 * (SwitchPresetPoint)实体类
 *
 * @author makejava
 * @since 2025-03-09 12:58:53
 */
public class SwitchPresetPoint implements Serializable {
    private static final long serialVersionUID = -32315112969655675L;


    private Long id;

    public SwitchPresetPoint(Long id, Integer panPosition, Integer tiltPosition, Integer zoom, String switchNumber) {
        this.id = id;
        this.panPosition = panPosition;
        this.tiltPosition = tiltPosition;
        this.zoom = zoom;
        this.switchNumber = switchNumber;
    }

    /**
     * 水平坐标
     */
    private Integer panPosition;
/**
     * 垂直坐标
     */
    private Integer tiltPosition;
/**
     * 变焦系数
     */
    private Integer zoom;
/**
     * 道岔编号
     */
    private String switchNumber;


    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Integer getPanPosition() {
        return panPosition;
    }

    public void setPanPosition(Integer panPosition) {
        this.panPosition = panPosition;
    }

    public Integer getTiltPosition() {
        return tiltPosition;
    }

    public void setTiltPosition(Integer tiltPosition) {
        this.tiltPosition = tiltPosition;
    }

    public Integer getZoom() {
        return zoom;
    }

    public void setZoom(Integer zoom) {
        this.zoom = zoom;
    }

    public String getSwitchNumber() {
        return switchNumber;
    }

    public void setSwitchNumber(String switchNumber) {
        this.switchNumber = switchNumber;
    }

}

