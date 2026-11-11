package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zzy.sms.stationmonitoringbanckend.entity.Task;
import com.zzy.sms.stationmonitoringbanckend.entity.TaskAttachment;
import com.zzy.sms.stationmonitoringbanckend.entity.TaskDetailHistory;
import com.zzy.sms.stationmonitoringbanckend.entity.TaskHistory;
import com.zzy.sms.stationmonitoringbanckend.mapper.TaskAttachmentMapper;
import com.zzy.sms.stationmonitoringbanckend.mapper.TaskDetailHistoryMapper;
import com.zzy.sms.stationmonitoringbanckend.mapper.TaskHistoryMapper;
import com.zzy.sms.stationmonitoringbanckend.mapper.TaskMapper;
import com.zzy.sms.stationmonitoringbanckend.service.TaskService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @description:
 * @author: zzy
 * @create: 2025-04-22 23:11
 **/
@Service
public class TaskServiceImpl implements TaskService {

    @Autowired
    private TaskMapper taskMapper;
    @Autowired
    private TaskHistoryMapper taskHistoryMapper;
    @Autowired
    private TaskAttachmentMapper taskAttachmentMapper;
    @Autowired
    private TaskDetailHistoryMapper taskDetailHistoryMapper;

    public List<Task> getTaskList(Map<String, Object> params) {
        return taskMapper.getTaskList(params);
    }

    @Override
    public int countTaskList(Map<String, Object> params, Long userId) {
        return taskMapper.countTaskList(params, userId);
    }

    @Override
    public Long createTask(Task task) {
        taskMapper.createTask(task);
        return task.getId();
    }

    @Override
    public Task getTaskById(Long id) {
        return taskMapper.getTaskById(id);
    }

    @Override
    public int updateTask(Task task) {
        return taskMapper.updateTask(task);
    }

    @Override
    public int insertTaskHistory(TaskHistory taskHistory) {         //添加任务历史状态
        return taskHistoryMapper.insertTaskHistory(taskHistory);
    }

    @Override
    public List<TaskHistory> selectTaskStepById(Long id) {
        return taskHistoryMapper.selectTaskStepById(id);
    }

    @Override
    public Long insertTaskAttachment(TaskAttachment attachment) {
        taskAttachmentMapper.insertTaskAttachment(attachment);
        return attachment.getId();
    }

    @Override
    public TaskAttachment getAttachmentById(Long id) {
        return taskAttachmentMapper.selectTaskAttachmentById(id);
    }

    @Override
    public List<TaskAttachment> getAttachmentsByTaskId(Long taskId) {
        return taskAttachmentMapper.selectAll(taskId);
    }

    @Override
    public List<TaskDetailHistory> getAllTaskDetailHistory(Map<String , Object> params) {
        return taskDetailHistoryMapper.getAllTaskDetailHistory(params);
    }

    @Override
    public int countTaskHistoryList(Map<String , Object> params) {
        return taskDetailHistoryMapper.countTaskHistoryList(params);
    }

    @Override
    public List<Task> getEmployeeTask(Map<String, Object> params, Long userId) {
        return taskMapper.getEmployeeTask(params, userId);
    }

    @Override
    public int updateTaskStatus(Long taskId, String status) {
        return taskMapper.updateTaskStatus(taskId, status);
    }

    @Override
    public int updateOperationFeedback(String operationFeedback, Long taskId) {
        return taskMapper.updateOperationFeedback(operationFeedback, taskId);
    }

    @Override
    public List<TaskDetailHistory> getAllTaskDetailHistoryByUserId(Map<String, Object> params) {
        return taskDetailHistoryMapper.getAllTaskDetailHistoryByUserId(params);
    }

    @Override
    public int countTaskHistoryListByUserId(Map<String, Object> params) {
        return taskDetailHistoryMapper.countTaskHistoryListByUserId(params);
    }

}