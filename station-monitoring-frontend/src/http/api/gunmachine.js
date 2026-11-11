import http from "../index.js"

export const getAllGunmachine = () => http.get("/gunmachine/getAllGunmachine")


export const insertGunmachine = (gunmachine) => {
    return http({
        url: "/gunmachine/insertGunmachine",
        method: "post",
        data: JSON.stringify(gunmachine),
        headers: {
            'Content-Type':'application/json'
        }
    })
}

export const updateGunmachine = (form) => {
    return http({
        url: "/gunmachine/updateGunmachine",
        method: "post",
        data: JSON.stringify(form),
        headers: {
            'Content-Type':'application/json'
        }
    })
}

export const deleteById = (id) => {
    return http({
        url: "/gunmachine/deleteById",
        method: "post",
        params:{
            id
        }
    })
}

export const searchGunmachine = (cameraId, trackId) => {
    return http({
        url: "/gunmachine/search",
        method: "get",
        params:{
            cameraId,
            trackId,
        }
    })
}

