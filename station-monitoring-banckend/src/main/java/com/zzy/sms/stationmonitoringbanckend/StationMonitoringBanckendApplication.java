package com.zzy.sms.stationmonitoringbanckend;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.scheduling.annotation.EnableScheduling;

@EnableScheduling
@SpringBootApplication
@MapperScan("com.zzy.sms.stationmonitoringbanckend.mapper")
public class StationMonitoringBanckendApplication {

    public static void main(String[] args) {
        SpringApplication.run(StationMonitoringBanckendApplication.class, args);
    }

}
