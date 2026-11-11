package com.zzy.sms.stationmonitoringbanckend.dto;

import lombok.Data;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-06 21:58
 **/

@Data
public class GunmachineDTO {
    private Long id;
    private Long cameraId;
    private String cameraName;
    private Long trackId;
    private Integer smallRange;
    private Integer wideRange;
}
