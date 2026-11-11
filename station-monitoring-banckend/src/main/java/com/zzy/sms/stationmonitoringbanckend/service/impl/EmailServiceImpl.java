package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.zzy.sms.stationmonitoringbanckend.service.EmailService;
import com.zzy.sms.stationmonitoringbanckend.service.VerificationCodeRateLimitException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

import javax.mail.MessagingException;
import javax.mail.internet.MimeMessage;
import java.security.SecureRandom;
import java.time.LocalDate;
import java.util.Locale;
import java.util.concurrent.TimeUnit;

/**
 * @description:
 * @author: zzy
 * @create: 2025-01-21 00:44
 **/
@Service
public class EmailServiceImpl implements EmailService {
    private static final int CODE_TTL_MINUTES = 5;
    private static final int RESEND_COOLDOWN_SECONDS = 60;
    private static final int EMAIL_DAILY_LIMIT = 10;
    private static final int IP_DAILY_LIMIT = 30;
    private static final SecureRandom SECURE_RANDOM = new SecureRandom();

    @Autowired
    private JavaMailSender mailSender;
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Override
    // 发送验证码邮件
    public String sendVerificationCode(String toEmail, String requesterIp) throws MessagingException {
        String normalizedEmail = toEmail.trim().toLowerCase(Locale.ROOT);
        String cooldownKey = "email:code:cooldown:" + normalizedEmail;
        Boolean acquired = redisTemplate.opsForValue().setIfAbsent(
                cooldownKey, "1", RESEND_COOLDOWN_SECONDS, TimeUnit.SECONDS);
        if (!Boolean.TRUE.equals(acquired)) {
            throw new VerificationCodeRateLimitException("验证码发送过于频繁，请稍后再试");
        }

        String code = generateVerificationCode();
        try {
            enforceDailyLimit("email:code:daily:email:" + normalizedEmail, EMAIL_DAILY_LIMIT);
            enforceDailyLimit("email:code:daily:ip:" + safeRequesterIp(requesterIp), IP_DAILY_LIMIT);
            sendEmail(normalizedEmail, "您的验证码", "您的验证码是：" + code + "，请在5分钟内完成验证。");
            redisTemplate.opsForValue().set(
                    "email:code:" + normalizedEmail, code, CODE_TTL_MINUTES, TimeUnit.MINUTES);
            return code;
        } catch (MessagingException | RuntimeException exception) {
            if (!(exception instanceof VerificationCodeRateLimitException)) {
                redisTemplate.delete(cooldownKey);
            }
            throw exception;
        }
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
        int code = SECURE_RANDOM.nextInt(1_000_000);
        return String.format("%06d", code);
    }

    private void enforceDailyLimit(String keyPrefix, int maximum) {
        String key = keyPrefix + ":" + LocalDate.now();
        Long count = redisTemplate.opsForValue().increment(key);
        if (count != null && count == 1L) {
            redisTemplate.expire(key, 1, TimeUnit.DAYS);
        }
        if (count != null && count > maximum) {
            throw new VerificationCodeRateLimitException("今日验证码发送次数已达上限，请明日再试");
        }
    }

    private String safeRequesterIp(String requesterIp) {
        return requesterIp == null || requesterIp.isBlank() ? "unknown" : requesterIp.replaceAll("[^0-9a-fA-F:.]", "_");
    }
}
