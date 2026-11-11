import http from "../index.js"

// 获取图像检测历史记录
export const getDetectionHistory = (params) => {
  return http({
    url: "/detection/history",
    method: "get",
    params
  });
};

// 获取特定检测记录的详情
export const getDetectionDetail = (id) => {
  return http({
    url: "/detection/detail",
    method: "get",
    params: { id }
  });
};

// 开始实时检测
export const startRealtimeDetection = (cameraId, settings) => {
  return http({
    url: "/detection/realtime/start",
    method: "post",
    data: {
      cameraId,
      ...settings
    },
    headers: {
      'Content-Type': 'application/json'
    }
  });
};

// 停止实时检测
export const stopRealtimeDetection = (detectionId) => {
  return http({
    url: "/detection/realtime/stop",
    method: "post",
    data: { detectionId },
    headers: {
      'Content-Type': 'application/json'
    }
  });
};

// 开始回放检测
export const startPlaybackDetection = (cameraId, startTime, endTime, settings) => {
  return http({
    url: "/detection/playback/start",
    method: "post",
    data: {
      cameraId,
      startTime,
      endTime,
      ...settings
    },
    headers: {
      'Content-Type': 'application/json'
    }
  });
};

// 上传图片进行检测
export const uploadImageForDetection = (formData) => {
  return http({
    url: "/detection/image",
    method: "post",
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

// 导出检测结果
export const exportDetectionResult = (id, format = 'pdf') => {
  return http({
    url: "/detection/export",
    method: "get",
    params: { id, format },
    responseType: 'blob' // 指定响应类型为blob
  });
};

// 删除检测记录
export const deleteDetectionRecord = (id) => {
  return http({
    url: "/detection/record",
    method: "delete",
    params: { id }
  });
};

// 获取检测统计数据
export const getDetectionStatistics = (timeRange) => {
  return http({
    url: "/detection/statistics",
    method: "get",
    params: timeRange
  });
}; 