import http from "../index.js"

// 上传录制的视频文件到后端，供视频回放页面（video.vue）管理
export const uploadRecording = (blob, filename, metadata = {}) => {
    const formData = new FormData();
    formData.append("file", blob, filename);
    if (metadata.cameraId != null) formData.append("cameraId", String(metadata.cameraId));
    if (metadata.startedAt) formData.append("startedAt", metadata.startedAt);
    if (metadata.endedAt) formData.append("endedAt", metadata.endedAt);
    formData.append("source", metadata.source || 'manual');
    return http({
        url: "/recording/upload",
        method: "post",
        data: formData,
        timeout: 300000 // 视频文件较大，放宽超时到 5 分钟
    })
}

// 录像列表
export const getRecordingList = () => http.get("/recording/list");

// 查找覆盖告警发生时刻的同摄像头录像；无匹配录像时 success 为 false。
export const getRecordingMatch = (cameraId, at) => http.get("/recording/match", {
    params: { cameraId, at }
});

// 删除录像文件
export const deleteRecording = (filename) => http({
    url: `/recording/${encodeURIComponent(filename)}`,
    method: "delete"
});
