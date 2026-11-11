package com.zzy.sms.stationmonitoringbanckend;

import com.zzy.sms.stationmonitoringbanckend.service.CameraLoginService;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import javax.annotation.Resource;

/**
 * @description: 1
 * @author: zzy
 * @create: 2025-03-27 16:22
 **/
@SpringBootTest
public class StationMonitoringBanckendApplicationTest {

    @Resource
    private CameraLoginService cameraLoginService;

    @Test
    public void test() {
        cameraLoginService.loginAllCameras();
    }
}
