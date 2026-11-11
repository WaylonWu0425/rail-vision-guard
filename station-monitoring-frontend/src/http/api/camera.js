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

// 获取最近7天的警告统计数据
export const getWarningStatistics = () => {
    return http.get("/camera/warning/statistics");
}