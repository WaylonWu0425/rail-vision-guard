package com.zzy.sms.stationmonitoringbanckend.controller;

import cn.dev33.satoken.stp.StpUtil;
import com.zzy.sms.stationmonitoringbanckend.entity.Task;
import com.zzy.sms.stationmonitoringbanckend.entity.TaskAttachment;
import com.zzy.sms.stationmonitoringbanckend.entity.TaskHistory;
import com.zzy.sms.stationmonitoringbanckend.service.TaskService;
import com.zzy.sms.stationmonitoringbanckend.util.DateTimeUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.FileSystemResource;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;


import org.springframework.core.io.Resource;
import java.io.File;
import java.net.URLEncoder;
import java.util.*;

/**
 * @description:
 * @author: zzy
 * @create: 2025-04-22 17:26
 **/
@RestController
@RequestMapping("/task")
public class TaskController {

    private static final Logger log = LoggerFactory.getLogger(TaskController.class);

    @Autowired
    private TaskService taskService;

    @Autowired
    private DateTimeUtil dateTimeUtil;


    @GetMapping("/getTaskList")
    public ResponseEntity getTaskList(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String type,
            @RequestParam(required = false)
            @DateTimeFormat(pattern = "yyyy-MM-dd") Date createDate,
            @RequestParam(required = false)
            @DateTimeFormat(pattern = "yyyy-MM-dd") Date endDate) {
        Map<String, Object> params = new HashMap<>();
        params.put("page", (page - 1)*size);
        params.put("size", size);
        params.put("search", search);
        params.put("status", status);
        params.put("type", type);
        params.put("startDate", createDate);
        params.put("endDate", endDate);

        Map<String, Object> response = new HashMap<>();
        try {
            Map<String, Object> data = new HashMap<>();
            response.put("data", data);
            List<Task> taskList = taskService.getTaskList(params);
            int total = taskService.countTaskList(params, null);
            data.put("taskList", taskList);
            data.put("total", total);
            response.put("message", "查询成功");
            response.put("success", true);
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            e.printStackTrace();
            response.put("message", "查询失败");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
    }

    @PostMapping("/createTask")
    public ResponseEntity createTask(@RequestBody Task task) {
        Map<String, Object> response = new HashMap<>();
        Long userId = StpUtil.getLoginIdAsLong();
        task.setCreateById(userId);
        task.setCreateTime(dateTimeUtil.getCurrentTime());
        task.setStatus("0");
        TaskHistory taskHistory = new TaskHistory();
        taskHistory.setStatus("0");
        taskHistory.setStatusTime(dateTimeUtil.getCurrentTime());
        try {
            Long taskId = taskService.createTask(task);
            taskHistory.setTaskId(taskId);
            taskService.insertTaskHistory(taskHistory);
            response.put("data", Collections.singletonMap("taskId", taskId));
            response.put("success", true);
            response.put("message", "创建任务成功");
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            e.printStackTrace();
            response.put("success", false);
            response.put("message", "创建任务失败");
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/getTaskById")
    public ResponseEntity getTaskById(@RequestParam("id") Long id) {
        Map<String, Object> response = new HashMap<>();
        try {
            Task task = taskService.getTaskById(id);
            response.put("data", task);
            response.put("success", true);
            response.put("message", "查询任务详情成功");
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            e.printStackTrace();
            response.put("success", false);
            response.put("message", "查询任务详情失败");
            return ResponseEntity.badRequest().body(response);
        }
    }

    @PostMapping("/updateTask")
    public ResponseEntity updateTask(@RequestBody Task task) {
        Map<String, Object> response = new HashMap<>();
        try {
            int flag = taskService.updateTask(task);
            if(flag < 1) {
                response.put("success", false);
                response.put("message", "修改任务信息失败");
                return ResponseEntity.badRequest().body(response);
            }
            response.put("success", true);
            response.put("message", "修改任务信息成功");
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            e.printStackTrace();
            response.put("success", false);
            response.put("message", "修改任务信息失败");
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/getTaskStep")     //获取详细任务信息的步骤条
    public ResponseEntity getTaskStep(@RequestParam("id") Long id) {
        Map<String, Object> response = new HashMap<>();
        try {
            List<TaskHistory> taskHistories = taskService.selectTaskStepById(id);
            response.put("data", taskHistories);
            response.put("success", true);
            response.put("message", "获取任务进度成功");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            e.printStackTrace();
            response.put("success", false);
            response.put("message", "获取任务进度失败");
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/getTaskAttachmentList")
    public ResponseEntity getTaskAttachmentList(@RequestParam("taskId") Long taskId) {
        Map<String, Object> response = new HashMap<>();
        try {
            List<TaskAttachment> taskAttachmentList = taskService.getAttachmentsByTaskId(taskId);
            response.put("data", taskAttachmentList);
            response.put("success", true);
            response.put("message", "获取任务附件成功");
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            e.printStackTrace();
            response.put("success", false);
            response.put("message", "获取任务进附件失败");
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/downloadAttachment")
    public ResponseEntity downloadAttachment(@RequestParam("id") Long id) {
        try {
            TaskAttachment taskAttachment = taskService.getAttachmentById(id);
            if (taskAttachment == null) {
                return ResponseEntity.notFound().build();
            }
            String filePath = "uploads/" + taskAttachment.getFilePath();
            File file = new File(filePath);
            if (!file.exists()) {
                return ResponseEntity.notFound().build();
            }
            Resource resource = new FileSystemResource(file);
            String encodedFileName = URLEncoder.encode(file.getName(), "UTF-8").replaceAll("\\+", "%20");
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
            headers.setContentDisposition(ContentDisposition.attachment().filename(encodedFileName).build());
            return ResponseEntity.ok()
                    .headers(headers)
                    .body(resource);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @PostMapping("/uploadAttachment/{taskId}")
    public ResponseEntity<Map<String, Object>> uploadAttachment(@RequestParam("files") MultipartFile[] files,
                                                                @PathVariable Long taskId) {
        log.info("开始上传文件，taskId: {}, 文件数量: {}", taskId, files.length);
        Map<String, Object> response = new HashMap<>();
        List<Map<String, Object>> uploadedFiles = new ArrayList<>();
        try {
            // 检查任务是否存在
            Task task = taskService.getTaskById(taskId);
            if (task == null) {
                response.put("success", false);
                response.put("message", "任务不存在");
                return ResponseEntity.badRequest().body(response);
            }
            // 检查文件数量限制
            if (files.length > 5) {
                response.put("success", false);
                response.put("message", "一次最多只能上传5个文件");
                return ResponseEntity.badRequest().body(response);
            }
            // 逐个处理每个文件
            for (MultipartFile file : files) {
                // 获取原始文件名（包含后缀）
                String originalFilename = file.getOriginalFilename();
                if (originalFilename == null || originalFilename.isEmpty()) {
                    continue; // 跳过空文件名
                }
                // 文件大小检查（10MB）
                if (file.getSize() > 10 * 1024 * 1024) {
                    continue; // 跳过过大的文件
                }
                // 文件后缀
                String fileExtension = "";
                if (originalFilename.contains(".")) {
                    fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
                }

                // 生成随机的文件路径
                String randomFileName = UUID.randomUUID() + fileExtension;

                // 构建完整的文件路径
                String fullPath = "D:/桌面/2021081122/station-monitoring-banckend/uploads/" + randomFileName;

                // 保存文件到服务器
                File dest = new File(fullPath);
                file.transferTo(dest);

                // 保存附件信息到数据库
                TaskAttachment attachment = new TaskAttachment();
                attachment.setTaskId(taskId);
                attachment.setName(originalFilename); // 保存完整的原始文件名（包含后缀）
                attachment.setFilePath(randomFileName); // 保存随机生成的文件名
                attachment.setUploadTime(new Date());

                // 保存附件记录
                Long attachmentId = taskService.insertTaskAttachment(attachment);

                // 添加到上传成功列表
                Map<String, Object> fileInfo = new HashMap<>();
                fileInfo.put("id", attachmentId);
                fileInfo.put("name", originalFilename);
//                fileInfo.put("url", "/task/downloadAttachment?id=" + attachmentId);
                uploadedFiles.add(fileInfo);
            }
            response.put("success", true);
            response.put("data", uploadedFiles);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            e.printStackTrace();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    @PostMapping("/reviewFeedback")
    public ResponseEntity reviewFeedback(@RequestParam("taskId") Long taskId,
                                         @RequestParam("status") String status,
                                         @RequestParam(value = "reviewFeedback", required = false) String reviewFeedback) {
        Map<String, Object> response = new HashMap<>();
        TaskHistory taskHistory = new TaskHistory();
        taskHistory.setTaskId(taskId);
        taskHistory.setStatus(status);
        taskHistory.setStatusTime(dateTimeUtil.getCurrentTime());
        if(status.equals("5")) taskHistory.setFeedback(reviewFeedback);
        Task task = taskService.getTaskById(taskId);
        task.setStatus(status);
        try {
            if((taskService.insertTaskHistory(taskHistory) <1) || (taskService.updateTask(task) <1)) {
                response.put("success", false);
                response.put("message", "任务审核失败");
                return ResponseEntity.badRequest().body(response);
            }
            response.put("success", true);
            response.put("message", "任务审核成功");
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            e.printStackTrace();
            response.put("success", false);
            response.put("message", "任务审核失败");
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/getAllTaskDetailHistory")
    public ResponseEntity getAllTaskDetailHistory(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String type,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd") Date createDate,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd") Date endDate) {
        Map<String, Object> params = new HashMap<>();
        params.put("page", (page - 1)*size);
        params.put("size", size);
        params.put("search", search);
        params.put("status", status);
        params.put("type", type);
        params.put("startDate", createDate);
        params.put("endDate", endDate);
        Long userId = StpUtil.getLoginIdAsLong();
        Map<String, Object> response = new HashMap<>();
        try {
            Map<String, Object> data = new HashMap<>();
            data.put("taskDetailHistoryList", taskService.getAllTaskDetailHistory(params));
            data.put("taskDetailHistoryCount", taskService.countTaskHistoryList(params));
            response.put("data", data);
            log.error("任务历史记录数据", data);
            response.put("success", true);
            response.put("message", "查询任务历史记录成功");
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            e.printStackTrace();
            response.put("success", false);
            response.put("message", "查询任务历史记录失败");
            return ResponseEntity.badRequest().body(response);
        }
    }
    //获取个人任务列表
    @GetMapping("/getEmployeeTask")
    public ResponseEntity getEmployeeTask(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String type,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd") Date createDate,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd") Date endDate) {
        Map<String, Object> params = new HashMap<>();
        params.put("page", (page - 1)*size);
        params.put("size", size);
        params.put("search", search);
        params.put("status", status);
        params.put("type", type);
        params.put("startDate", createDate);
        params.put("endDate", endDate);
        Long userId = StpUtil.getLoginIdAsLong();
        Map<String, Object> response = new HashMap<>();
        try {
            Map<String, Object> data = new HashMap<>();
            response.put("data", data);
            List<Task> taskList = taskService.getEmployeeTask(params, userId);
            int total = taskService.countTaskList(params, userId);
            data.put("taskList", taskList);
            data.put("total", total);
            response.put("message", "查询成功");
            response.put("success", true);
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            e.printStackTrace();
            response.put("message", "查询失败");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
    }

    //添加任务操作状态
    @PostMapping("/updateTaskStatus")
    public ResponseEntity updateTaskStatus(@RequestParam("taskId") Long taskId, @RequestParam("status") String status) {
        Map<String, Object> response = new HashMap<>();
        TaskHistory taskHistory = new TaskHistory();
        taskHistory.setTaskId(taskId);
        taskHistory.setStatus(status);
        taskHistory.setStatusTime(dateTimeUtil.getCurrentTime());
        try {
            int flag = taskService.insertTaskHistory(taskHistory);
            if(flag < 1) {
                response.put("message", "添加任务状态失败");
                response.put("success", false);
                return ResponseEntity.badRequest().body(response);
            }
            taskService.updateTaskStatus(taskId, status);
            response.put("message", "添加任务状态成功");
            response.put("success", true);
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            e.printStackTrace();
            response.put("message", "添加任务状态失败");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/updateOperationFeedback")
    public ResponseEntity updateOperationFeedback(@RequestParam("operationFeedback") String operationFeedback, @RequestParam("taskId") Long taskId) {
        Map<String, Object> response = new HashMap<>();
        try {
            taskService.updateOperationFeedback(operationFeedback, taskId);
            response.put("message", "任务操作反馈添加成功");
            response.put("success", true);
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            e.printStackTrace();
            response.put("message", "任务操作反馈添加失败");
            response.put("success", false);
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/getAllTaskDetailHistoryByUserId")
    public ResponseEntity getAllTaskDetailHistoryByUserId(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String type,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd") Date createDate,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd") Date endDate) {
        Map<String, Object> params = new HashMap<>();
        params.put("page", (page - 1)*size);
        params.put("size", size);
        params.put("search", search);
        params.put("status", status);
        params.put("type", type);
        params.put("startDate", createDate);
        params.put("endDate", endDate);
        Long userId = StpUtil.getLoginIdAsLong();
        params.put("userId", userId);
        Map<String, Object> response = new HashMap<>();
        try {
            Map<String, Object> data = new HashMap<>();
            data.put("taskDetailHistoryList", taskService.getAllTaskDetailHistoryByUserId(params));
            data.put("taskDetailHistoryCount", taskService.countTaskHistoryListByUserId(params));
            response.put("data", data);
            response.put("success", true);
            response.put("message", "查询任务历史记录成功");
            return ResponseEntity.ok(response);
        }catch (Exception e) {
            e.printStackTrace();
            response.put("success", false);
            response.put("message", "查询任务历史记录失败");
            return ResponseEntity.badRequest().body(response);
        }
    }
}
