package com.zzy.sms.stationmonitoringbanckend.service;

public class VerificationCodeRateLimitException extends RuntimeException {
    public VerificationCodeRateLimitException(String message) {
        super(message);
    }
}
