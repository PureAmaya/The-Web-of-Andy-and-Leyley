<template>
  <div class="request-reset-view">
    <div class="reset-form-container">
      <h2>请求密码重置</h2>
      <p class="description">请输入您注册时使用的邮箱地址。如果该邮箱存在于我们的系统中，我们将向其发送一封包含重置链接的邮件。</p>
      <form @submit.prevent="handleRequestReset">
        <div class="form-group">
          <label for="email">邮箱地址</label>
          <input type="email" id="email" v-model="email" required autocomplete="email" />
        </div>
        <button type="submit" class="form-button" :disabled="isLoading">
          {{ isLoading ? '发送中...' : '发送重置邮件' }}
        </button>
        <p v-if="message" :class="['message', messageType]">{{ message }}</p>
      </form>
      <div class="form-links">
        <RouterLink to="/login">返回登录</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { useSettingsStore } from '@/stores/settings';

const settingsStore = useSettingsStore();
const email = ref('');
const isLoading = ref(false);
const message = ref('');
const messageType = ref(''); // 'success' or 'error'

async function handleRequestReset() {
  isLoading.value = true;
  message.value = '';
  messageType.value = '';

  try {
    const response = await fetch(`${settingsStore.apiBaseUrl}/auth/request-password-reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value }),
    });

    const data = await response.json();

    if (response.ok) {
      message.value = data.message || "请求已发送。如果您的邮箱地址在我们系统中注册过，您将会收到一封邮件。";
      messageType.value = 'success';
      email.value = ''; // 清空输入框
    } else {
      message.value = data.detail || '请求失败，请稍后重试。';
      messageType.value = 'error';
    }
  } catch (err) {
    message.value = '网络错误或服务器无响应，请稍后重试。';
    messageType.value = 'error';
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.request-reset-view {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 50px 20px;
  min-height: calc(100vh - 160px); /* 视口高度减去页眉页脚大致高度 */
  box-sizing: border-box;
}

.reset-form-container {
  max-width: 450px; /* 可以稍微宽一点以容纳描述文字 */
  width: 100%;
  /* 容器样式与登录/注册页保持一致 */
  background-color: var(--main-bg-color);
  border: 2px solid var(--border-color);
  box-shadow: none; /* 移除阴影，保持扁平复古感 */
  padding: 2.5rem;
}

.reset-form-container h2 {
  text-align: center;
  color: var(--main-text-color);
  margin-bottom: 20px;
  font-size: 1.8em;
  font-weight: normal;
  /* 标题可以考虑使用特殊字体，如果希望和标签区分开，则保持现状 */
  /* font-family: var(--font-special), cursive; */
}

.description {
  text-align: center;
  margin-bottom: 30px;
  color: var(--link-color); /* 使用链接颜色，使其不那么突出 */
  font-size: 0.95em;
  line-height: 1.6;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  /* 使用特殊手写/打字机字体，契合主题 */
  font-family: var(--font-special), cursive;
  color: var(--link-color);
}

.form-group input {
  /* 输入框使用半透明深色背景，与登录/注册页保持一致 */
  background-color: rgba(0, 0, 0, 0.2);
  /* 输入的文字使用网站主字体 */
  font-family: var(--font-main);
  border-color: var(--border-color);
  /* 其他基础样式继承自 main.css */
}

.form-button {
  width: 100%;
  /* 按钮使用主题的强调色 */
  background-color: var(--primary-accent-color);
  border-color: #600000; /* 边框颜色可以比背景稍暗 */
  color: var(--button-text-color);
}

.form-button:hover:not(:disabled) {
  background-color: #600000;
  border-color: #400000;
}

.form-links {
  margin-top: 25px;
  text-align: center;
  font-size: 0.9em;
}

.form-links a {
  color: var(--link-color);
  text-decoration: underline;
}

.form-links a:hover {
  color: var(--link-hover-color);
}

.message {
  margin-top: 20px;
  text-align: center;
  padding: 10px;
  border: 1px dashed transparent;
}

.message.success {
  color: var(--secondary-accent-color, #2a5c2a); /* 使用一个备用绿色 */
  border-color: var(--secondary-accent-color, #2a5c2a);
}

.message.error {
  color: var(--primary-accent-color);
  border-color: var(--primary-accent-color);
}
</style>