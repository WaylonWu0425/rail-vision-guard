package com.zzy.sms.stationmonitoringbanckend.config;

import cn.dev33.satoken.context.SaHolder;
import cn.dev33.satoken.context.model.SaResponse;
import cn.dev33.satoken.filter.SaServletFilter;
import cn.dev33.satoken.router.SaHttpMethod;
import cn.dev33.satoken.router.SaRouter;
import cn.dev33.satoken.stp.StpUtil;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

/**
 * @description: Sa-Token 全局过滤器
 * @author: zzy
 * @create: 2025-01-18 00:31
 **/
@Order(0)
@Component
public class SaTokenFilter extends SaServletFilter {

    public SaTokenFilter() {
        // 拦截所有路径
        addInclude("/**");

        // 认证逻辑：排除 OPTIONS 请求，对其他请求检查登录状态
        setAuth(auth -> {
            SaRouter.notMatch(SaHttpMethod.OPTIONS)
                    .match("/**")
                    .check(r -> StpUtil.checkLogin());
        });

        // 排除无需认证的路径
        addExclude(
                "/user/doLogin/account",
                "/user/doLogin/email",
                "/user/register/account",
                "/user/register/email",
                "/user/send-code",
                "/task/updateTaskStatus",
                "/health"
        );

        // 在认证前设置 CORS 头
        setBeforeAuth(obj -> {
            SaResponse response = SaHolder.getResponse();
            // 动态获取请求来源，允许本地开发端口（8080 前端 / 3001 备用）
            String origin = SaHolder.getRequest().getHeader("Origin");
            if (origin != null && (origin.startsWith("http://localhost:") || origin.startsWith("http://127.0.0.1:"))) {
                response.setHeader("Access-Control-Allow-Origin", origin);
            } else {
                response.setHeader("Access-Control-Allow-Origin", "http://localhost:8080");
            }
            response.setHeader("Access-Control-Allow-Credentials", "true");
            response.setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS, DELETE, PUT");
            response.setHeader("Access-Control-Max-Age", "3600");
            // 允许 sa-token header 跨域传输
            response.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With, sa-token");
        });

        // 错误处理：自定义响应而不是抛出异常
        setError(e -> {
            SaResponse response = SaHolder.getResponse();
            response.setStatus(401); // 未登录返回 401 而不是 500
            response.setHeader("Content-Type", "application/json;charset=UTF-8");
            return "{\"code\": \"NOT_LOGIN\", \"msg\": \"" + e.getMessage() + "\"}";
        });
    }
}
