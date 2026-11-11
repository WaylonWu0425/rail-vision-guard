package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-21 23:47
 **/

@Data
public class BallCamera {
    private Long id;
    private String ip;
    private int port;
    private String username;
    private String password;
    private int bridgeType;
    private int initViewPoint;
}
