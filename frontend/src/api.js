// 文件: frontend/src/api.js
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';

const apiClient = axios.create();

// 请求拦截器：自动附加认证头和API基础地址
apiClient.interceptors.request.use(
    (config) => {
        // 在 Pinia 插件注册后，可以在这里安全地使用 store
        const authStore = useAuthStore();
        const settingsStore = useSettingsStore();

        // --- 核心修正 ---
        // 不在创建时设置 baseURL，而是在每次请求时动态获取
        // 确保总是使用最新的 apiBaseUrl
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
        // 确保 useAuthStore 可以在这里被调用
        // 这通常是安全的，因为此时 Pinia 已经被安装
        try {
            const authStore = useAuthStore();
            if (error.response && error.response.status === 401) {
                authStore.logout();
            }
        } catch (e) {
            // 如果 store 还不可用，则只记录错误
            console.error("无法在响应拦截器中访问 auth store:", e);
        }
        return Promise.reject(error);
    }
);

export default apiClient;