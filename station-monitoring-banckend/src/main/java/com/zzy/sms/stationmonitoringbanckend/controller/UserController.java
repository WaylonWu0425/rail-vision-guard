package com.zzy.sms.stationmonitoringbanckend.controller;

import cn.dev33.satoken.annotation.SaCheckLogin;
import cn.dev33.satoken.secure.SaBase64Util;
import cn.dev33.satoken.stp.StpUtil;
import cn.dev33.satoken.util.SaResult;
import com.zzy.sms.stationmonitoringbanckend.entity.User;
import com.zzy.sms.stationmonitoringbanckend.service.EmailService;
import com.zzy.sms.stationmonitoringbanckend.service.UserService;
import com.zzy.sms.stationmonitoringbanckend.util.DateTimeUtil;
import com.zzy.sms.stationmonitoringbanckend.util.Validator;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


import javax.mail.MessagingException;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
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
    private RedisTemplate<String, Object> redisTemplate;

    @PostMapping("/send-code")
    public ResponseEntity sendCode(@RequestParam("email") String email) throws MessagingException {
        Map<String, Object> response = new HashMap<>();
        if (emailService.sendVerificationCode(email) != null) {
            response.put("message", "验证码发送成功");
            response.put("success", true);
            return ResponseEntity.ok(response);
        } else {
            response.put("message", "验证码发送失败");
            response.put("success", false);
            return ResponseEntity.ok(response);
        }
    }

    @SaCheckLogin   // 登录验证
    @PostMapping("/doLogin/account")
    public SaResult doLoginWithAccount(@RequestParam("account") String account, @RequestParam("password") String password) {
        if (!Validator.isValidAccount(account)) return SaResult.error("账户格式不正确");
        if (!Validator.isValidPassword(password)) return SaResult.error("密码格式不正确");
        User user = new User(null, null, account, null, null, null, null, null, null, null, null, null, null, null);
        User user1 = userService.queryAllByLimit(user);
        if (user1 == null) return SaResult.error("用户不存在");
        if (SaBase64Util.decode(user1.getPassword()).equals(password)) {
            StpUtil.login(user1.getId());
            user1.setPassword(null);
            return SaResult.ok().setData(user1).setMsg("登录成功");
        }
        // / 添加详细日志
        System.out.println("密码不匹配！");
        System.out.println("DB密码解码后: " + SaBase64Util.decode(user1.getPassword()));
        System.out.println("前端密码: " + password);
        return SaResult.error("登录失败");
    }

    @PostMapping("/doLogin/email")
    public SaResult doLoginWithEmail(@RequestParam("email") String email, @RequestParam("code") String code) {
        if (!Validator.isValidEmail(email)) return SaResult.error("邮件格式不正确");
        User user = new User(null, null, null, null, email, null, null, null, null, null, null, null, null, null);
        User user1 = userService.queryAllByLimit(user);
        if (user1 == null) return SaResult.error("用户不存在");
        String key = "email:code:" + email;
        String storedCode = (String) redisTemplate.opsForValue().get(key);
        if (storedCode == null) {
            return SaResult.error("验证码已过期，请重新获取！");
        }
        if (!storedCode.equals(code)) {
            return SaResult.error("验证码错误！");
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
            // 使用Base64编码
            String base64Text = SaBase64Util.encode(password);
            String accountDefault = "user_" + account;
            User user = new User(null, accountDefault, account, base64Text, null, "defaultPicture.jpg", null, null, null, dateTime, Byte.valueOf("0"), "0", Byte.valueOf("0"), dateTime);
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
        Date dateTime = dateTimeUtil.getCurrentTime();
        String key = "email:code:" + email;
        String storedCode = (String) redisTemplate.opsForValue().get(key);
        if (storedCode == null) {
            return ResponseEntity.ok("验证码已过期");
        }
        if (!storedCode.equals(code)) {
            return ResponseEntity.badRequest().body("验证码错误");
        }
        String accountDefault = "user_" + email.indexOf("@");
        User user = new User(null, accountDefault, null, null, email, null, null, null, null, dateTime, Byte.valueOf("0"), null, Byte.valueOf("0"), dateTime);
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
        if (oldPassword.equals(SaBase64Util.decode(userService.getUserById(id).getPassword()))) {
            if (user.getPassword() != null) {
                user.setPassword(SaBase64Util.encode(user.getPassword()));
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
