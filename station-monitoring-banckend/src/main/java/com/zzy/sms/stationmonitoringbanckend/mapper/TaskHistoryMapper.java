package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.entity.Task;
import com.zzy.sms.stationmonitoringbanckend.entity.TaskHistory;

import java.util.List;

public interface TaskHistoryMapper {
    int insertTaskHistory(TaskHistory taskHistory);     //插入任务的历史状态
    List<TaskHistory> selectTaskStepById(Long id);
}
