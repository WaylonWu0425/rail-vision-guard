package com.zzy.sms.stationmonitoringbanckend;

import com.zzy.sms.stationmonitoringbanckend.service.CameraLoginService;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import javax.annotation.Resource;

@SpringBootTest
class StationMonitoringBanckendApplicationTests {

    @Resource
    private CameraLoginService cameraLoginService;

    @Test
    public void test() {
        cameraLoginService.initCameraObject();
    }
}
