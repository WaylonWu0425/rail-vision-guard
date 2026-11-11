package com.zzy.sms.stationmonitoringbanckend.dto;

import lombok.Data;

import java.util.List;

/**
 * @description:
 * @author: zzy
 * @create: 2025-03-09 23:04
 **/

@Data
public class SwitchDTO {
    private Long id;
    private Integer field;
    private Long trackId;
    private String throat;
    private Long switchPresetPointId;
    private Integer panPosition;
    private Integer tiltPosition;
    private Integer zoom;
    private List<String> switchNumber;
}
