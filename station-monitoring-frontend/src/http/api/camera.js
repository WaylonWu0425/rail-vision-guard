import http from "../index.js"

export const getAllCameras = () => http.get("/camera/getCameras");
export const getBallmachineCameras = () => http.get("/camera/getBallmachineCameras");
export const getGunmachineCameras = () => http.get("/camera/getGunmachineCameras");

export const insertCamera = (addForm) => {
    return http({
        url: "/camera/insertCamera",
        method: "post",
        data: JSON.stringify(addForm),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

export const updateCameraById = (editForm) => {
    return http({
        url: "/camera/updateCameraById",
        method: "post",
        data: JSON.stringify(editForm),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

export const deleteCameraById = (id) => {
    return http({
        url: "/camera/deleteCameraById",
        method: "delete",
        params: {
            id
        }
    })
}

export const searchCamera = (keyword) => {
    return http({
        url: "/camera/searchCamera",
        method: "get",
        params: {
            keyword
        }
    })
}

export const countOnlineCameras = () => http.get("/camera/countOnlineCameras");
export const countOfflineCameras = () => http.get("/camera/countOfflineCameras");

// 云台控制（PTZ）标准化接口
export const ptzControl = (ptzForm) => {
    return http({
        url: "/camera/ptzControl",
        method: "post",
        data: JSON.stringify(ptzForm),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

// 跳转预置点（回到初始位置）
export const gotoPreset = (cameraId, presetId, channel) => {
    const data = { cameraId, channel: channel || 0 };
    if (presetId != null) data.presetId = presetId;
    return http({
        url: "/camera/gotoPreset",
        method: "post",
        data: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

// 获取最近7天的警告统计数据
export const getWarningStatistics = () => {
    return http.get("/camera/warning/statistics");
}