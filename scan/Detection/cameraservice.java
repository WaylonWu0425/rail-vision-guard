package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;
import java.util.Date;
import java.io.Serializable;

/**
 * (Camera) 实体类
 *
 * @author makejava
 * @since 2025-03-21 23:18:14
 */
@Data
public class Camera implements Serializable {
    private static final long serialVersionUID = -50150718065808040L;

    /**
     * 摄像头 ID (主键)
     */
    private Long id;

    /**
     * 摄像头名称
     */
    private String name;

    /**
     * 产品编号 (数据库是 INT，但如果有非数值内容可考虑 String)
     */
    private Integer productNumber;

    /**
     * 状态 (数据库是 VARCHAR(10)，应使用 String)
     */
    private String status;

    /**
     * IP 地址
     */
    private String ip;

    /**
     * 类型 (数据库是 INT)
     */
    private Integer type;

    /**
     * 创建时间 (数据库是 DATETIME)
     */
    private Date createTime;

    /**
     * 更新时间 (数据库是 DATETIME，支持自动更新时间)
     */
    private Date updateTime;

    /**
     * 端口号
     */
    private Integer port;

    /**
     * 用户名
     */
    private String username;

    /**
     * 密码
     */
    private String password;

    /**
     * 桥接类型
     */
    private Integer bridgeType;

    /**
     * 初始视角
     */
    private Integer initViewPoint;
}
