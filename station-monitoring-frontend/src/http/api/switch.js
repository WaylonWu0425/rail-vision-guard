import http from "../index.js"

export const getSwitch = () => http.get("/switch/getSwitch");

export const getSwitchPresetPoint = (trackId, field, throat) => {
    return http({
        url: "/switch/getSwitchPresetPoint",
        method: "get",
        params: {
            trackId,
            field,
            throat
        }
    })
}

export const search = (trackId, field, throat) => {
    return http({
        url: "/switch/search",
        method: "get",
        params: {
            trackId,
            field,
            throat
        }
    })
}

export const insertSwitchPresetPoint = (switchPresetPoint) => {
    return http({
        url: "/switch/insertSwitchPresetPoint",
        method: "post",
        data: JSON.stringify(switchPresetPoint),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

export const insertSwitch = (switchPresetPoint) => {
    return http({
        url: "/switch/insertSwitch",
        method: "post",
        data: JSON.stringify(switchPresetPoint),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

export const updateSwitch = (switchData, switchPresetPointId) => {
    return http({
        url: "/switch/updateSwitch",
        method: "post",
        data: JSON.stringify(switchData),
        headers: {
            'Content-Type': 'application/json'
        },
        params: {
            switchPresetPointId
        }
    })
}

export const deleteSwitch = (switchPresetPoint) => {
    return http({
        url: "/switch/deleteSwitch",
        method: "delete",
        data: JSON.stringify(switchPresetPoint),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}