import http from "../index.js";

export const doLoginWithAccount = (account, password) => {
    return http({
        url: "/user/doLogin/account",
        method: "post",
        params: {
            account,
            password,
        }
    })
}

export const doLoginWithEmail = (email, code) => {
    return http({
        url: "/user/doLogin/email",
        method: "post",
        params: {
            email,
            code,
        }
    })
}

export const sendCode = (email) => {
    return http({
        url: "/user/send-code",
        method: "post",
        params: {
            email
        }
    })
}
export const registerWithAccount = (account, password) => {
    return http({
        url: "/user/register/account",
        method: "post",
        params: {
            account,
            password,
        }
    })
}

export const registerWithEmail = (email, code) => {
    return http({
        url: "/user/register/email",
        method: "post",
        params: {
            email,
            code,
        }
    })
}

export const logout = (id) => {
    return http({
        url: "/user/logout",
        method: "post",
        params: {
            id
        }
    })
}

export const uploadAvatar = (file) => {
    return http({
        url: "/upload/uploadAvatar",
        method: "post",
        data:file,
        headers: {
            'Content-Type': 'multipart/form-data', // 设置请求头
        },
    })
}

export const getAvatar = (filename) => {
    return http({
        url: "/upload/getAvatar",
        method: "get",
        params: {
            filename
        },
        responseType: 'blob', // 指定响应类型为 Blob
        // withCredentials: true, // 如果需要携带 Cookie
    })
}

export const updateUser = (formData, oldPassword) => {
    return http({
        url: "/user/updateUser",
        method: "put",
        data: JSON.stringify(formData),
        params:{
            oldPassword
        },
        headers: {
            'Content-Type': 'application/json', // 设置请求头
        },
        withCredentials:true
    })
}



export const forbiddenUser = (id) => {
    return http({
        url: "/user/forbiddenUser",
        method: "post", 
        params: {
            id
        }
    })
}

export const deleteUser = (id) => {
    return http({
        url: "/user/deleteUser",
        method: "delete", 
        params: {
            id
        }
    })
}

export const searchUser = (id) => {
    return http({
        url: "/user/searchUser",
        method: "get", 
        params: {
            id
        }
    })
}

export const getAllUser = () => {
    return http({
        url: "/user/getAllUser",
        method: "get",
    })
}