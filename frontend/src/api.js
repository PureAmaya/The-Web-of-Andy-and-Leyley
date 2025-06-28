import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';

const apiClient = axios.create();

// 请求拦截器：在每个请求发送前附加认证头
apiClient.interceptors.request.use(
  (config) => {
    // 拦截器内获取 store 实例，确保是激活的
    const authStore = useAuthStore();
    const settingsStore = useSettingsStore();

    config.baseURL = settingsStore.apiBaseUrl;

    // 【核心修正】: 使用正确的 `accessToken` 属性
    if (authStore.accessToken) {
      config.headers['Authorization'] = `Bearer ${authStore.accessToken}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理后端返回的错误，例如token失效时自动登出
apiClient.interceptors.response.use(
  // 对成功的响应直接返回 data
  (response) => response.data,

  (error) => {
    // 如果后端返回 401 (未认证) 错误
    if (error.response && error.response.status === 401) {
      const authStore = useAuthStore();
      authStore.logout(); // 调用登出 action，清除本地数据并跳转
    }
    return Promise.reject(error);
  }
);

export default apiClient;