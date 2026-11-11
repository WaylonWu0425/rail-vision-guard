package com.zzy.sms.stationmonitoringbanckend.entity;

import lombok.Data;

import java.util.List;

/**
 * @description:  列表分页结果类
 * @author: zzy
 * @create: 2025-04-22 23:38
 **/

@Data
public class PageResult<T> {
    private List<T> list;
    private int total;

    public PageResult(List<T> list, int total) {
        this.list = list;
        this.total = total;
    }
}
