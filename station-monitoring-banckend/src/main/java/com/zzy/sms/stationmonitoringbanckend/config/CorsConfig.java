package com.zzy.sms.stationmonitoringbanckend.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * @author : zzy
 * @description :
 * @create : 2025-02-19 22:15
 **/
@Configuration

public class CorsConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")

                //                .allowedOriginPatterns("*")
                .allowedOrigins("http://localhost:3001") // 允许的前端地址
                .allowedMethods("GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS")
                .allowCredentials(true)
                //            .allowedHeaders("sa-token","cookie")
                .maxAge(3600)
                .allowedHeaders("Content-Type, Authorization, X-Requested-With");
    }
}

