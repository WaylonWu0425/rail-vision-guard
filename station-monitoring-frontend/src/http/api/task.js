import http from "../index.js"

//获取任务列表，搜索任务列表
export const getTaskList = (params) => http.get("/task/getTaskList", { params });

// 新增任务
export const createTask = (params) => {
    return http({
        url: "/task/createTask",
        method: "post", 
        data: params,
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

//通过id获取任务详情
export const getTaskById = (id) => {
    return http({
        url: "/task/getTaskById",
        method: "get",
        params: { id }
    })
}

// 编辑任务
export const updateTask = (params) => {
    return http({
        url: "/task/updateTask",
        method: "post",
        data: params,
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

// 获取任务进度详情
export const getTaskStep = (id) => {
    return http({
        url: "/task/getTaskStep",
        method: "get",
        params: { id }
    })
}

// 获取任务附件
export const getTaskAttachmentList = (taskId) => {
    return http({
        url: "/task/getTaskAttachmentList",
        method: "get",
        params: { taskId }
    })
}

// 下载任务附件
export const downloadAttachment = (id) => {
    return http({
        url: "/task/downloadAttachment",
        method: "get",
        params: { id },
        responseType: 'blob'
    })
}

// 上传任务附件
export const uploadAttachment = (files, taskId) => {
    const formData = new FormData();
    
    // 支持多文件上传
    if (Array.isArray(files)) {
        // 如果传入的是文件数组，添加多个文件
        files.forEach(file => {
            formData.append('files', file);
        });
    } else {
        // 如果传入的是单个文件，直接添加
        formData.append('files', files);
    }
    
    return http({
        url: `/task/uploadAttachment/${taskId}`,
        method: "post",
        data: formData,
        // headers: {
        //     'Content-Type': 'multipart/form-data'
        // },
        timeout: 60000 // 增加超时时间到60秒
    })
}

// 审核
export const reviewFeedback = (taskId, status, reviewFeedback) => {
    return http({
        url: "/task/reviewFeedback",
        method: "post",
        params: { 
            taskId,
            status,
            reviewFeedback
        }
    })
}

// 获取任务历史记录
export const getAllTaskDetailHistory = (params) => http.get("/task/getAllTaskDetailHistory", { params });

// 获取个人任务历史记录
export const getAllTaskDetailHistoryByUserId = (params) => http.get("/task/getAllTaskDetailHistoryByUserId", { params });


//获取个人任务列表
export const getEmployeeTask = (params) => http.get("/task/getEmployeeTask", { params });

//修改任务操作历史
export const updateTaskStatus = (taskId, status) => {
    return http({
        url: "/task/updateTaskStatus",
        method: "post",
        params: { 
            taskId,
            status
        }
    })
}

// 提交操作反馈
export const submitOperationFeedBack = (taskId, operationFeedback) => {
    return http({
        url: "/task/updateOperationFeedback",
        method: "get",
        params: {
            operationFeedback,
            taskId
        }
    })
}
