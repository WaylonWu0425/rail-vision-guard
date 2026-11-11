package com.zzy.sms.stationmonitoringbanckend.service;

import cn.dev33.satoken.secure.SaBase64Util;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class PasswordServiceTest {

    private final PasswordService passwordService = new PasswordService();

    @Test
    void bcryptPasswordsCanBeEncodedAndVerified() {
        String encoded = passwordService.encode("secure123");

        assertTrue(passwordService.matches("secure123", encoded));
        assertFalse(passwordService.matches("wrong123", encoded));
        assertFalse(passwordService.needsUpgrade(encoded));
    }

    @Test
    void legacyBase64PasswordsRemainUsableForMigration() {
        String legacy = SaBase64Util.encode("000000");

        assertTrue(passwordService.matches("000000", legacy));
        assertFalse(passwordService.matches("111111", legacy));
        assertTrue(passwordService.needsUpgrade(legacy));
    }
}
