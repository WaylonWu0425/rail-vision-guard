package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zzy.sms.stationmonitoringbanckend.entity.Task;
import com.zzy.sms.stationmonitoringbanckend.entity.TaskDetailHistory;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface TaskDetailHistoryMapper {
    List<TaskDetailHistory> getAllTaskDetailHistory(Map<String , Object> params);   //管理员任务历史操作查看
    int countTaskHistoryList(Map<String, Object> params);   //管理员任务条数
    List<TaskDetailHistory> getAllTaskDetailHistoryByUserId(Map<String, Object> params);   //操作人员任务历史操作查看
    int countTaskHistoryListByUserId(Map<String, Object> params);   //操作人员任务历史操作查看

}
