package com.zzy.sms.stationmonitoringbanckend.util;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * @description: 格式检验
 * @author: zzy
 * @create: 2025-01-21 22:27
 **/
public class Validator {
    // 账户格式验证：长度在5-10位之间，只能包含字母和数字
    public static boolean isValidAccount(String account) {
        String regex = "^[a-zA-Z0-9]{5,10}$";
        Pattern pattern = Pattern.compile(regex);
        Matcher matcher = pattern.matcher(account);
        return matcher.matches();
    }

    // 密码格式验证：长度在6-15位之间，可以包含任意字符
    public static boolean isValidPassword(String password) {
        String regex = "^[\\S]{6,15}$";
        Pattern pattern = Pattern.compile(regex);
        Matcher matcher = pattern.matcher(password);
        return matcher.matches();
    }

    // 邮箱格式验证
    public static boolean isValidEmail(String email) {
        String regex = "^[a-zA-Z0-9_+&*-]+(?:\\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,7}$";
        Pattern pattern = Pattern.compile(regex);
        Matcher matcher = pattern.matcher(email);
        return matcher.matches();
    }
}
