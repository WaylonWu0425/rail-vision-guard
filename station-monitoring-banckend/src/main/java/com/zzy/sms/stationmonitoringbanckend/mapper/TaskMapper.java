package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.entity.Task;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Mapper
public interface TaskMapper {

    List<Task> getTaskList(Map<String, Object> params);
    int countTaskList(Map<String, Object> params, Long userId);
    Long createTask(Task task);
    Task getTaskById(Long id);   //通过id查询出编辑表的任务信息
    int updateTask(Task task);
    List<Task> getEmployeeTask(Map<String, Object> params, Long userId);
    int updateTaskStatus(Long taskId, String status);
    int updateOperationFeedback(String operationFeedback, Long taskId);
    //获取时间内的所有任务
    @Select("SELECT * FROM task WHERE create_time BETWEEN #{startTime} AND #{endTime}")
    List<Task> getTasksByCreateTimeRange(@Param("startTime") LocalDateTime startTime, @Param("endTime") LocalDateTime endTime);

}
