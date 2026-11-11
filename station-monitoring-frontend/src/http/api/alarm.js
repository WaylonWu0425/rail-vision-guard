import http from "../index.js"

export const getAllAlarmInfo = () => http.get("/alarmInfo/getAllAlarmInfo");

export const getUndisposedAlarmInfo = () => http.get("/alarmInfo/getUndisposedAlarmInfo");

export const searchAlarmInfo = (cameraName, day, type, status) => {
    return http({
        url: "/alarmInfo/search",
        method: "get",
        params: {
            cameraName: cameraName,
            day: day,
            type: type,
            status: status
        }
    })
}

export const updateAlarmInfoById = (id) => {
    return http({
        url: "/alarmInfo/updateAlarmInfoById",
        method: "get",
        params: {
            id: id
        }   
    })
}