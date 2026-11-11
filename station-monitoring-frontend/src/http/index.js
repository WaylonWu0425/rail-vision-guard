import axios from "axios";

// 设置默认请求头
axios.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";

const http = axios.create({
    // baseURL: "http://localhost:8081", // Java 后端地址
    baseURL: '/api',  // 部署时改成相对路径，通过 Nginx 代理
    // baseURL: isProduction ? 'http://8.156.67.132:8081' : 'http://localhost:8081',
    // baseURL: "http://8.156.67.132:8081", // Java 后端地址

    withCredentials: true, // 与后端 allowCredentials 保持一致
    timeout: 70000, // 请求超时时间
});

// 请求拦截器，添加 token
http.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token"); // 从本地存储获取 token
        if (token) {
            config.headers["Authorization"] = `Bearer ${token}`; // Sa-Token 默认使用 Authorization 头
            // 如果后端要求 token 在其他头中，改为：
            // config.headers["sa-token"] = token;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error); // 改为 reject，便于捕获错误
    }
);

// 响应拦截器，处理后端返回的错误
http.interceptors.response.use(
    (response) => {
        return response; // 直接返回数据部分
    },
    (error) => {
        if (error.response) {
            const status = error.response.status;
            const data = error.response.data || {};

            // 处理特定错误
            if (status === 500 && data.code === "NOT_LOGIN") {
                // token 无效或被顶下线
                localStorage.removeItem("token");
                window.location.href = "/login"; // 跳转到登录页
                return Promise.reject(new Error("未登录或 token 无效，请重新登录"));
            } else if (status === 401) {
                // 未授权
                localStorage.removeItem("token");
                window.location.href = "/login";
                return Promise.reject(new Error("未授权，请登录"));
            } else {
                // 其他 500 错误
                return Promise.reject(new Error(data.msg || "服务器错误"));
            }
        } else {
            // 网络错误
            return Promise.reject(new Error("网络错误，请检查连接"));
        }
    }
);

export default http;