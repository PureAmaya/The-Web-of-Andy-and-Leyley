<template>
  <div class="verify-email-view">
    <div class="verify-email-container">
      <h2>邮箱验证</h2>
      <p v-if="isLoading" class="message">正在验证您的邮箱...</p>
      <p v-else-if="message" :class="['message', messageType]">{{ message }}</p>
      <div v-else class="initial-check-message">
        <p v-if="!token">缺少验证令牌。请确保您使用了完整的验证链接。</p>
        <p v-else>
          如果您的邮箱尚未验证，请点击以下按钮完成验证。
          <button @click="handleVerification" :disabled="isVerifying" class="form-button">
            {{ isVerifying ? '验证中...' : '立即验证' }}
          </button>
        </p>
      </div>

      <div class="form-links" v-if="!isLoading">
        <RouterLink to="/login" class="nav-link">前往登录</RouterLink>
        <RouterLink to="/" class="nav-link">返回首页</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, RouterLink } from 'vue-router';
import apiClient from '@/api'; // 导入您的 apiClient
import { useSettingsStore } from '@/stores/settings';

const route = useRoute();
const settingsStore = useSettingsStore();

const token = ref('');
const isLoading = ref(true); // 初始加载状态
const isVerifying = ref(false); // 按钮的加载状态
const message = ref('');
const messageType = ref(''); // 'success' or 'error'

async function handleVerification() {
  if (!token.value) {
    message.value = '验证令牌缺失。';
    messageType.value = 'error';
    return;
  }

  isVerifying.value = true;
  isLoading.value = true; // 确保在验证过程中显示加载状态
  message.value = ''; // 清空之前的消息
  messageType.value = '';

  try {
    const response = await apiClient.get(`/auth/verify-email?token=${token.value}`); // <--- 调用后端 API
    // 假设 apiClient 自动返回 data，如果不是，需要 await response.json()
    message.value = response.message || '邮箱已成功验证！';
    messageType.value = 'success';
  } catch (err) {
    console.error('邮箱验证失败:', err);
    message.value = err.response?.data?.detail || '邮箱验证失败，请重试。';
    messageType.value = 'error';
  } finally {
    isVerifying.value = false;
    isLoading.value = false;
  }
}

onMounted(() => {
  token.value = route.query.token || '';
  if (token.value) {
    // 如果 URL 中有 token，直接触发验证
    handleVerification();
  } else {
    // 如果没有 token，立即停止加载并显示提示
    isLoading.value = false;
    message.value = '无法找到验证令牌。请检查您收到的链接。';
    messageType.value = 'error';
  }
});
</script>

<style scoped>
.verify-email-view {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 50px 20px;
  min-height: calc(100vh - 160px);
  box-sizing: border-box;
}

.verify-email-container {
  max-width: 450px;
  width: 100%;
  background-color: var(--main-bg-color);
  border: 2px solid var(--border-color);
  box-shadow: none;
  padding: 2.5rem;
  text-align: center;
}

.verify-email-container h2 {
  color: var(--main-text-color);
  margin-bottom: 20px;
  font-size: 1.8em;
  font-weight: normal;
}

.message {
  margin-top: 20px;
  padding: 10px;
  border: 1px dashed transparent;
  font-size: 1em;
}

.message.success {
  color: var(--secondary-accent-color);
  border-color: var(--secondary-accent-color);
}

.message.error {
  color: var(--primary-accent-color);
  border-color: var(--primary-accent-color);
}

.initial-check-message {
  margin-top: 20px;
  color: var(--link-color);
  font-size: 0.95em;
  line-height: 1.6;
}

.initial-check-message button {
  margin-top: 20px;
  width: auto;
  padding: 10px 20px;
}

.form-links {
  margin-top: 25px;
  text-align: center;
  font-size: 0.9em;
}

.form-links a {
  color: var(--link-color);
  text-decoration: underline;
  margin: 0 8px;
}

.form-links a:hover {
  color: var(--link-hover-color);
}
</style>