// src/stores/auth.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useSettingsStore } from './settings';

// API 基地址常量不再需要在这里定义
// const API_BASE_URL = 'http://localhost:8000'; // <--- 删除或注释掉这行

export const useAuthStore = defineStore('auth', () => {
    const settingsStore = useSettingsStore(); // 2. 获取 settingsStore 实例

    // --- State ---
    const accessToken = ref(localStorage.getItem('access_token') || null);
    const refreshToken = ref(localStorage.getItem('refresh_token') || null);
    const user = ref(JSON.parse(localStorage.getItem('user_info')) || null);


    const isLoadingUser = ref(false);
    const userError = ref(null);

    // --- Getters ---
    const isLoggedIn = computed(() => !!accessToken.value);

    // --- Actions ---
    const router = useRouter();

    function setTokens(newAccessToken, newRefreshToken) {
        accessToken.value = newAccessToken;
        refreshToken.value = newRefreshToken;
        if (newAccessToken) {
            localStorage.setItem('access_token', newAccessToken);
        } else {
            localStorage.removeItem('access_token');
        }
        if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken);
        } else {
            localStorage.removeItem('refresh_token');
        }
    }

    function setUserInfo(userInfo) {
        user.value = userInfo;
        if (userInfo) {
            localStorage.setItem('user_info', JSON.stringify(userInfo));
        } else {
            localStorage.removeItem('user_info');
        }
    }

    async function login(loginTokenData) {
        setTokens(loginTokenData.access_token, loginTokenData.refresh_token);
        if (accessToken.value) {
            await fetchAndSetUser();
        }
    }

    async function fetchAndSetUser() {
        if (!accessToken.value) {
            console.warn('尝试获取用户信息，但 access token 不存在。');
            setUserInfo(null);
            return null;
        }

        // ++ 修改此函数 ++
        isLoadingUser.value = true;
        userError.value = null;
        try {
            const response = await fetch(`${settingsStore.apiBaseUrl}/users/me`, {
                headers: { 'Authorization': `Bearer ${accessToken.value}` }
            });
            if (response.ok) {
                const userData = await response.json();
                setUserInfo(userData);
                return userData;
            } else {
                const errorData = await response.text();
                console.error('获取用户信息失败:', response.status, errorData);
                userError.value = `获取用户信息失败 (状态: ${response.status})。`;
                if (response.status === 401) {
                    logout(); // 令牌无效或过期，自动登出
                }
                setUserInfo(null);
                return null;
            }
        } catch (error) {
            console.error('获取用户信息时发生网络错误:', error);
            userError.value = '网络或服务器错误，无法获取用户信息。';
            setUserInfo(null);
            return null;
        } finally {
            isLoadingUser.value = false;
        }
    }


    function logout() {
        setTokens(null, null);
        setUserInfo(null);
        if (router) {
            router.push('/login').catch(err => {
                if (err.name !== 'NavigationDuplicated') { console.error(err); }
            });
        }
    }

    async function initAuth() {
        if (isLoggedIn.value && !user.value) {
            await fetchAndSetUser();
        }
    }

    return {
        accessToken,
        refreshToken,
        user,
        isLoggedIn,
        login,
        logout,
        fetchAndSetUser,
        setTokens,
        setUserInfo,
        initAuth,
    };
});