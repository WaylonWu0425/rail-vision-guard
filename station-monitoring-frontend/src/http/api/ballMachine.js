import http from "../index.js"

export const getAllBallmachine = () => http.get("/BallmachinePresetPoint/getAllBallmachine")


export const insertPresetPoint = (presetPoint) => {
    return http({
        url: "/BallmachinePresetPoint/insertPresetPoint",
        method: "post",
        data: JSON.stringify(presetPoint),
        headers: {
            'Content-Type':'application/json'
        }
    })
}

export const insertBallmachine = (form) => {
    return http({
        url: "/BallmachinePresetPoint/insertBallmachine",
        method: "post",
        data: JSON.stringify(form),
        headers: {
            'Content-Type':'application/json'
        }
    })
}

export const updateBallmachine = (form) => {
    return http({
        url: "/BallmachinePresetPoint/updateBallmachine",
        method: "post",
        data: JSON.stringify(form),
        headers: {
            'Content-Type':'application/json'
        }
    })
}

export const deleteBallmachine = (id) => {
    return http({
        url: "/BallmachinePresetPoint/deleteBallmachine",
        method: "delete",
        params:{
            id
        }
    })
}

export const searchBallmachine = (cameraId, trackId) => {
    return http({
        url: "/BallmachinePresetPoint/search",
        method: "post",
        params:{
            cameraId,
            trackId
        }
    })
}