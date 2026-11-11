package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.entity.TaskAttachment;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface TaskAttachmentMapper {
    int insertTaskAttachment(TaskAttachment taskAttachment);
    TaskAttachment selectTaskAttachmentById(Long id);
    List<TaskAttachment> selectAll(Long taskId);
}
