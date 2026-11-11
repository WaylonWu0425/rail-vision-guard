package com.zzy.sms.stationmonitoringbanckend.service;

import cn.dev33.satoken.secure.SaBase64Util;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class PasswordService {

    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);

    public String encode(String rawPassword) {
        return encoder.encode(rawPassword);
    }

    public boolean matches(String rawPassword, String storedPassword) {
        if (rawPassword == null || storedPassword == null || storedPassword.isBlank()) {
            return false;
        }
        if (isBcrypt(storedPassword)) {
            return encoder.matches(rawPassword, storedPassword);
        }
        try {
            return rawPassword.equals(SaBase64Util.decode(storedPassword));
        } catch (RuntimeException exception) {
            return false;
        }
    }

    public boolean needsUpgrade(String storedPassword) {
        return storedPassword != null && !storedPassword.isBlank() && !isBcrypt(storedPassword);
    }

    private boolean isBcrypt(String value) {
        return value.startsWith("$2a$") || value.startsWith("$2b$") || value.startsWith("$2y$");
    }
}
