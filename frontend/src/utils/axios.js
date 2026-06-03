// src/utils/axios.js
import axios from 'axios'
import {useUserStore} from "../stores/user.js";

// 创建axios实例
const instance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
    timeout: 10000,
})

// 请求拦截器
instance.interceptors.request.use(config => {
    // 从localStorage获取token
    const token = localStorage.getItem('authToken')
    if (token) {
        config.headers.Authorization = `Token ${token}`
    }
    return config
}, error => {
    return Promise.reject(error)
})

// 响应拦截器
instance.interceptors.response.use(response => {
    return response
}, error => {
    // 统一处理错误
    if (error.response && error.response.status === 401) {
        // Token过期，跳转到登录页
        const userStore = useUserStore()
        userStore.logout()
        window.location.href = '/login'
    }
    return Promise.reject(error)
})

export default instance