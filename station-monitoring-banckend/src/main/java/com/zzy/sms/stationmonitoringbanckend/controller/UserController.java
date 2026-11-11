package com.zzy.sms.stationmonitoringbanckend.controller;

import cn.dev33.satoken.stp.StpUtil;
import cn.dev33.satoken.util.SaResult;
import com.zzy.sms.stationmonitoringbanckend.entity.User;
import com.zzy.sms.stationmonitoringbanckend.service.EmailService;
import com.zzy.sms.stationmonitoringbanckend.service.PasswordService;
import com.zzy.sms.stationmonitoringbanckend.service.UserService;
import com.zzy.sms.stationmonitoringbanckend.service.VerificationCodeRateLimitException;
import com.zzy.sms.stationmonitoringbanckend.util.DateTimeUtil;
import com.zzy.sms.stationmonitoringbanckend.util.Validator;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


import javax.servlet.http.HttpServletRequest;
import javax.mail.MessagingException;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * @description:
 * @author: zzy
 * @create: 2025-01-17 11:24
 **/

@RestController
@RequestMapping("/user")
public class UserController {
    @Autowired
    private UserService userService;
    @Autowired
    private DateTimeUtil dateTimeUtil;
    @Autowired
    private EmailService emailService;
    @Autowired
    private PasswordService passwordService;
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @PostMapping("/send-code")
    public ResponseEntity sendCode(@RequestParam("email") String email, HttpServletRequest request) {
        Map<String, Object> response = new HashMap<>();
        if (!Validator.isValidEmail(email)) {
            response.put("message", "邮箱格式不正确");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
        try {
            emailService.sendVerificationCode(email, request.getRemoteAddr());
            response.put("message", "验证码发送成功");
            response.put("success", true);
            return ResponseEntity.ok(response);
        } catch (VerificationCodeRateLimitException exception) {
            response.put("message", exception.getMessage());
            response.put("success", false);
            return ResponseEntity.status(429).body(response);
        } catch (MessagingException exception) {
            response.put("message", "验证码发送失败");
            response.put("success", false);
            return ResponseEntity.status(503).body(response);
        }
    }

    @PostMapping("/doLogin/account")
    public SaResult doLoginWithAccount(@RequestParam("account") String account, @RequestParam("password") String password) {
        if (!Validator.isValidAccount(account)) return SaResult.error("账户格式不正确");
        if (!Validator.isValidPassword(password)) return SaResult.error("密码格式不正确");
        User user = new User(null, null, account, null, null, null, null, null, null, null, null, null, null, null);
        User user1 = userService.queryAllByLimit(user);
        if (user1 == null) return SaResult.error("账号或密码错误");
        String storedPassword = user1.getPassword();
        if (passwordService.matches(password, storedPassword)) {
            if (passwordService.needsUpgrade(storedPassword)) {
                user1.setPassword(passwordService.encode(password));
                userService.update(user1);
            }
            StpUtil.login(user1.getId());
            user1.setPassword(null);
            return SaResult.ok().setData(user1).setMsg("登录成功");
        }
        return SaResult.error("账号或密码错误");
    }

    @PostMapping("/doLogin/email")
    public SaResult doLoginWithEmail(@RequestParam("email") String email, @RequestParam("code") String code) {
        if (!Validator.isValidEmail(email)) return SaResult.error("邮件格式不正确");
        String normalizedEmail = email.trim().toLowerCase(Locale.ROOT);
        User user = new User(null, null, null, null, normalizedEmail, null, null, null, null, null, null, null, null, null);
        User user1 = userService.queryAllByLimit(user);
        if (user1 == null) return SaResult.error("邮箱或验证码错误");
        String key = "email:code:" + normalizedEmail;
        String storedCode = (String) redisTemplate.opsForValue().get(key);
        if (storedCode == null || !storedCode.equals(code)) {
            return SaResult.error("邮箱或验证码错误");
        }
        redisTemplate.delete(key);// 验证成功后删除Redis中的验证码
        StpUtil.login(user1.getId());
        user1.setPassword(null);
        return SaResult.ok().setData(user1).setMsg("登录成功");
    }

    @PostMapping("/register/account")
    public ResponseEntity registerWithAccount(@RequestParam("account") String account, @RequestParam("password") String password) {
        Map<String, Object> response = new HashMap<>();
        if (!Validator.isValidAccount(account)) {
            response.put("success", false);
            response.put("message", "账户格式不正确");
            return ResponseEntity.badRequest().body(response);
        }
        if (!Validator.isValidPassword(password)) {
            response.put("success", false);
            response.put("message", "密码格式不正确");
            return ResponseEntity.badRequest().body(response);
        }
        try {
            Date dateTime = dateTimeUtil.getCurrentTime();
            String encodedPassword = passwordService.encode(password);
            String accountDefault = "user_" + account;
            User user = new User(null, accountDefault, account, encodedPassword, null, "defaultPicture.jpg", null, null, null, dateTime, Byte.valueOf("0"), "0", Byte.valueOf("0"), dateTime);
            int rowsAffected = userService.insertUser(user);
            if (rowsAffected > 0) {
                response.put("message", "注册成功");
                response.put("success", true);
                return ResponseEntity.ok(response);
            } else {
                response.put("message", "注册失败");
                response.put("success", false);
                return ResponseEntity.badRequest().body(response);
            }
        } catch (RuntimeException e) {
            response.put("message", "注册失败");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
    }

    @PostMapping("/register/email")
    public ResponseEntity registerWithEmail(@RequestParam("email") String email, @RequestParam("code") String code) {
        Map<String, Object> response = new HashMap<>();
        if (!Validator.isValidEmail(email)) {
            response.put("message", "邮箱格式不正确");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
        String normalizedEmail = email.trim().toLowerCase(Locale.ROOT);
        Date dateTime = dateTimeUtil.getCurrentTime();
        String key = "email:code:" + normalizedEmail;
        String storedCode = (String) redisTemplate.opsForValue().get(key);
        if (storedCode == null || !storedCode.equals(code)) {
            response.put("message", "邮箱或验证码错误");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
        String accountDefault = "user_" + normalizedEmail.indexOf("@");
        User user = new User(null, accountDefault, null, null, normalizedEmail, null, null, null, null, dateTime, Byte.valueOf("0"), null, Byte.valueOf("0"), dateTime);
        try {
            userService.insertUser(user);
        } catch (RuntimeException e) {
            System.out.println(e);
            response.put("message", "注册失败");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
        redisTemplate.delete(key);// 验证成功后删除Redis中的验证码
        response.put("message", "注册成功");
        response.put("success", true);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/logout")
    public SaResult logout(@RequestParam("id") Long id) {
        // 清除当前用户的登录状态(token 和会话)
        StpUtil.kickout(id);
        return SaResult.ok("登出成功，token 已删除");
    }

    @PutMapping("/updateUser")
    public ResponseEntity updateUser(@RequestBody User user, @RequestParam(value = "oldPassword", required = false) String oldPassword) {
        Map<String, Object> response = new HashMap<>();
        Long id = StpUtil.getLoginIdAsLong();
        User existingUser = userService.getUserById(id);
        if (oldPassword != null && existingUser != null && passwordService.matches(oldPassword, existingUser.getPassword())) {
            if (user.getPassword() != null) {
                if (!Validator.isValidPassword(user.getPassword())) {
                    response.put("message", "新密码格式不正确");
                    response.put("success", false);
                    return ResponseEntity.badRequest().body(response);
                }
                user.setPassword(passwordService.encode(user.getPassword()));
            }
            user.setId(id);
            userService.update(user);
            response.put("message", "修改成功");
            response.put("success", true);
            return ResponseEntity.ok(response);

        } else {
            response.put("message", "密码不正确");
            response.put("success", false);
            return ResponseEntity.ok(response);
        }
    }

    // 获取所有操作人员
    @GetMapping("/getAllUser")
    public ResponseEntity getAllUser() {
        Map<String, Object> response = new HashMap<>();
        try {
            response.put("message", "获取成功");
            response.put("success", true);
            response.put("data", userService.getAllUser());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            response.put("message", "获取失败");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
    }

    @PostMapping("/forbiddenUser")
    public ResponseEntity forbiddenUser(@RequestParam("id") Long id) {
        Map<String, Object> response = new HashMap<>();
        try {
            if (userService.forbiddenUser(id)) {
                response.put("message", "禁用/解除禁用成功");
                response.put("success", true);
            } else {
                response.put("message", "禁用/解除禁用失败");
                response.put("success", false);
            }
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            System.out.println(e);
            response.put("message", "禁用/解除禁用失败");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
    }

    @DeleteMapping("/deleteUser")
    public ResponseEntity deleteUser(@RequestParam("id") Long id) {
        Map<String, Object> response = new HashMap<>();
        try {
            if (userService.deleteUser(id)) {
                response.put("message", "删除成功");
                response.put("success", true);
            } else {
                response.put("message", "删除失败");
                response.put("success", false);
            }
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            System.out.println(e);
            response.put("message", "删除失败");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/searchUser")
    public ResponseEntity searchUser(@RequestParam("id") Long id) {
        Map<String, Object> response = new HashMap<>();
        try {
            List<User> userList = userService.searchUser(id);
            response.put("data", userList);
            response.put("success", true);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
    }
}
