package com.zzy.sms.stationmonitoringbanckend.dto;

import lombok.Data;

import java.io.Serializable;

/**
 * (Ballmachine)实体类
 *
 * @author makejava
 * @since 2025-03-04 18:19:12
 */
@Data
public class BallmachineDTO implements Serializable {
    private static final long serialVersionUID = 204355894321153766L;

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
    private String cameraName;
    private int panPosition;
    private int tiltPosition;
    private int zoom;
    private int smallRange;
    private int wideRange;


}

