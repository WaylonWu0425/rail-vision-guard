package com.zzy.sms.stationmonitoringbanckend.service;


import javax.mail.MessagingException;

/**
 * @description: 邮箱验证
 * @author: zzy
 * @create: 2025-01-21 00:43
 **/
public interface EmailService {
    String sendVerificationCode(String toEmail, String requesterIp) throws MessagingException;
}
