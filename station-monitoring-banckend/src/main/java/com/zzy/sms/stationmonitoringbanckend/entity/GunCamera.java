package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-21 23:50
 **/

@Data
public class GunCamera {
    private Long id;
    private String ip;
    private int port;
    private String userName;
    private String password;
    private int bridgeType;
}
