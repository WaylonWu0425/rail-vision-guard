package com.zzy.sms.stationmonitoringbanckend.entity;

import java.io.Serializable;

/**
 * (Switch)实体类
 *
 * @author makejava
 * @since 2025-03-09 13:03:58
 */
public class Switch implements Serializable {
    private static final long serialVersionUID = -14337314427473181L;
/**
     * id
     */
    private Long id;
/**
     * 轨道id
     */
    private Long trackId;
/**
     * 场别
     */
    private Integer field;
/**
     * 0表示上，1表示下
     */
    private String throat;
/**
     * 道岔预置点id
     */
    private Long switchPresetPointId;


    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getTrackId() {
        return trackId;
    }

    public void setTrackId(Long trackId) {
        this.trackId = trackId;
    }

    public Integer getField() {
        return field;
    }

    public void setField(Integer field) {
        this.field = field;
    }

    public String getThroat() {
        return throat;
    }

    public void setThroat(String throat) {
        this.throat = throat;
    }

    public Long getSwitchPresetPointId() {
        return switchPresetPointId;
    }

    public void setSwitchPresetPointId(Long switchPresetPointId) {
        this.switchPresetPointId = switchPresetPointId;
    }

}

