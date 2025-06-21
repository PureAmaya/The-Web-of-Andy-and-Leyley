// src/api.js
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';

const apiClient = axios.create();

// 请求拦截器：自动附加认证头和API基础地址
apiClient.interceptors.request.use(
    (config) => {
        const authStore = useAuthStore();
        const settingsStore = useSettingsStore();

        if (!config.baseURL) {
            config.baseURL = settingsStore.apiBaseUrl;
        }

        if (authStore.accessToken) {
            config.headers.Authorization = `Bearer ${authStore.accessToken}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// 响应拦截器：统一处理错误，例如401自动登出
apiClient.interceptors.response.use(
    (response) => response.data, // 直接返回 data，简化后续处理
    (error) => {
        const authStore = useAuthStore();
        if (error.response && error.response.status === 401) {
            authStore.logout();
        }
        return Promise.reject(error);
    }
);

export default apiClient;