package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;

import java.util.Date;
import java.io.Serializable;

/**
 * (User)实体类
 *
 * @author makejava
 * @since 2025-01-16 23:26:57
 */
@Data
public class User implements Serializable {
    private static final long serialVersionUID = -99974596537289561L;

    public User(Long id, String username, String account, String password, String email, String avatar, Byte sex, String phoneNumber, Date lastLoginTime, Date registerTime, Byte delFlag, String role, Byte state, Date updateTime) {
        this.id = id;
        this.username = username;
        this.account = account;
        this.password = password;
        this.email = email;
        this.avatar = avatar;
        this.sex = sex;
        this.phoneNumber = phoneNumber;
        this.lastLoginTime = lastLoginTime;
        this.registerTime = registerTime;
        this.delFlag = delFlag;
        this.role = role;
        this.state = state;
        this.updateTime = updateTime;
    }

    /**
     * id
     */
    private Long id;
/**
     * 用户名
     */
    private String username;
/**
     * 账户
     */
    private String account;
/**
     * 密码
     */
    private String password;
    private String email;
/**
     * 头像
     */
    private String avatar;
/**
     * 0女1男
     */
    private Byte sex;
/**
     * 电话
     */
    private String phoneNumber;
/**
     * 上次登录时间
     */
    private Date lastLoginTime;
/**
     * 注册时间
     */
    private Date registerTime;
/**
     * 0没删1已删除
     */
    private Byte delFlag;
/**
     * 角色
     */
    private String role;
/**
     * 0正常1异常
     */
    private Byte state;
/**
     * 修改时间
     */
    private Date updateTime;

}

