import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api';

export const useAuthStore = defineStore('auth', () => {
  // --- State ---
  const accessToken = ref(localStorage.getItem('access_token') || null);
  const refreshToken = ref(localStorage.getItem('refresh_token') || null);
  const user = ref(JSON.parse(localStorage.getItem('user_info')) || null);
  const isLoadingUser = ref(false);
  const userError = ref(null);

  // --- Getters ---
  const isLoggedIn = computed(() => !!accessToken.value);
  const isAdmin = computed(() => user.value?.role === 'admin');

  // --- Actions ---

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

  function logout() {
    // 【核心修正】: 在函数内部获取 router 实例
    const router = useRouter();

    setTokens(null, null);
    setUserInfo(null);

    // 现在 router 实例是有效的
    router.push('/login').catch(err => {
        if (err.name !== 'NavigationDuplicated') { console.error(err); }
    });
  }

  async function fetchAndSetUser() {
    if (!accessToken.value) return null;

    isLoadingUser.value = true;
    userError.value = null;
    try {
      const userData = await apiClient.get('/users/me');
      setUserInfo(userData);
      return userData;
    } catch (error) {
      console.error('获取用户信息失败:', error);
      userError.value = '无法获取用户信息。';
      return null;
    } finally {
      isLoadingUser.value = false;
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
    isAdmin,
    isLoadingUser,
    userError,
    login,
    logout,
    fetchAndSetUser,
    initAuth,
  };
});