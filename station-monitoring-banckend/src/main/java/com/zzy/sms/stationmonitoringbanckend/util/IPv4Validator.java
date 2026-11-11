package com.zzy.sms.stationmonitoringbanckend.util;

import org.springframework.stereotype.Component;

/**
 * @description:
 * @author: zzy
 * @create: 2025-02-09 22:19
 **/
@Component
public class IPv4Validator {
    private static final String IPV4_REGEX =
            "^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\." +
                    "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\." +
                    "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\." +
                    "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$";

    public boolean isValidIPv4(String ip) {
        return ip != null && ip.matches(IPV4_REGEX);
    }
}

