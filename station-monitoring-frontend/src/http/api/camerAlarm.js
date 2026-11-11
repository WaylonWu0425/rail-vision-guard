import http from "../index.js"

export const getAllCameraAlarm = () => http.get("/cameraAlarm/getAllCameraAlarm");
export const getUndisposedCameraAlarm = () => http.get("/cameraAlarm/getUndisposedCameraAlarm");

export const updateCameraAlarmById = (id) => {
    return http({
        url: "/cameraAlarm/updateCameraAlarmById",
        method: "post",
        params: {
            id
        }
    })
}
export const search = (cameraName, day, type) => {
    return http({
        url: "/cameraAlarm/search",
        method: "get",
        params: {
            cameraName,
            day,
            type
        }
    })
}

//获取近七天的摄像头警报数据
export const getCameraAlarmByDay = () => http.get("/Statistics/getCameraAlarmByDay");
