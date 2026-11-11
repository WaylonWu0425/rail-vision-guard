package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.zzy.sms.stationmonitoringbanckend.service.EmailService;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

import javax.mail.MessagingException;
import javax.mail.internet.MimeMessage;
import java.util.Random;
import java.util.concurrent.TimeUnit;

/**
 * @description:
 * @author: zzy
 * @create: 2025-01-21 00:44
 **/
@Service
public class EmailServiceImpl implements EmailService {
    @Autowired
    private JavaMailSender mailSender;
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Override
    // 发送验证码邮件
    public String sendVerificationCode(String toEmail) throws MessagingException {
        String code = generateVerificationCode();
        sendEmail(toEmail, "您的验证码", "您的验证码是：" + code + "，请在5分钟内完成验证。");
        redisTemplate.opsForValue().set("email:code:" + toEmail, code, 2, TimeUnit.MINUTES);
        return code;
    }

    // 实际发送邮件逻辑
    private void sendEmail(String toEmail, String subject, String text) throws MessagingException {
        MimeMessage message = mailSender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(message, true);
        helper.setFrom("3165741995@qq.com"); // 替换为您的QQ邮箱
        helper.setTo(toEmail);
        helper.setSubject(subject);
        helper.setText(text);
        mailSender.send(message);
    }

    // 生成六位随机验证码
    private String generateVerificationCode() {
        Random random = new Random();
        int code = random.nextInt(999999);
        return String.format("%06d", code);
    }
}
