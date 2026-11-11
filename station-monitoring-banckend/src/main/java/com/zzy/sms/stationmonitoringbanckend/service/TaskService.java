package com.zzy.sms.stationmonitoringbanckend.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zzy.sms.stationmonitoringbanckend.entity.Task;
import com.zzy.sms.stationmonitoringbanckend.entity.TaskAttachment;
import com.zzy.sms.stationmonitoringbanckend.entity.TaskDetailHistory;
import com.zzy.sms.stationmonitoringbanckend.entity.TaskHistory;
import com.zzy.sms.stationmonitoringbanckend.mapper.TaskHistoryMapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

public interface TaskService {

    List<Task> getTaskList(Map<String, Object> params);
    int countTaskList(@Param("params") Map<String, Object> params, @Param("userId") Long userId);
    Long createTask(Task task);
    Task getTaskById(Long id);
    int updateTask(Task task);   //修改任务
    int insertTaskHistory(TaskHistory taskHistory);
    List<TaskHistory> selectTaskStepById(Long id);
    Long insertTaskAttachment(TaskAttachment attachment);
    TaskAttachment getAttachmentById(Long id);
    List<TaskAttachment> getAttachmentsByTaskId(Long taskId);
    List<TaskDetailHistory> getAllTaskDetailHistory(Map<String , Object> params);      //获取任务历史记录信息
    int countTaskHistoryList(Map<String , Object> params); //获取历史记录总条数
    List<Task> getEmployeeTask(@Param("params") Map<String, Object> params, @Param("userId") Long userId);
    int updateTaskStatus(Long taskId, String status);   //添加任务操作状态
    int updateOperationFeedback(String operationFeedback, Long taskId);  //添加任务操作反馈
    List<TaskDetailHistory> getAllTaskDetailHistoryByUserId(Map<String, Object> params);   //操作人员任务历史操作查看
    int countTaskHistoryListByUserId(Map<String, Object> params);   //操作人员任务历史操作查看

}