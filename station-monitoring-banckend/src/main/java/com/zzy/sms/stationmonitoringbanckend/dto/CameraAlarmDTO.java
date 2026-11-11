package com.zzy.sms.stationmonitoringbanckend.dto;


import lombok.Data;

import java.util.Date;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-30 19:45
 **/

@Data
public class CameraAlarmDTO {
    private Long id;
    private String cameraName;
    private int productNumber;
    private int port;
    private String ip;
    private String username;
    private Date createTime;
    private String dealFlag;

    public CameraAlarmDTO(Long id, String cameraName, int productNumber, int port, String ip, String username, Date createTime, String dealFlag) {
        this.id = id;
        this.cameraName = cameraName;
        this.productNumber = productNumber;
        this.port = port;
        this.ip = ip;
        this.username = username;
        this.createTime = createTime;
        this.dealFlag = dealFlag;
    }
}
