<template>
  <div class="login-view">
    <div class="login-form">
      <h2>用户登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">邮箱或用户名:</label>
          <input type="text" id="email" v-model="identifier" required autocomplete="username"/>
        </div>
        <div class="form-group">
          <label for="password">密码:</label>
          <input type="password" id="password" v-model="password" required autocomplete="current-password"/>
        </div>
        <button type="submit" class="form-button" :disabled="isLoading">
          {{ isLoading ? '登录中...' : '登录' }}
        </button>
        <p v-if="error" class="message error">{{ error }}</p>
      </form>
      <div class="form-links">
        <RouterLink v-if="settingsStore.isRegistrationEnabled" to="/register">
          还没有账户？立即注册
        </RouterLink>
        <br/>
        <RouterLink to="/request-password-reset">忘记密码？</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref} from 'vue';

import {useSettingsStore} from '@/stores/settings';

const settingsStore = useSettingsStore();

// 【核心修改】从 'vue-router' 中导入 useRoute
import {useRouter, RouterLink, useRoute} from 'vue-router'; // <--- 添加 useRoute
import {useAuthStore} from '@/stores/auth';

const router = useRouter();
const route = useRoute(); // <--- 正确定义 route 变量
const authStore = useAuthStore();

const identifier = ref('');
const password = ref('');
const isLoading = ref(false);
const error = ref('');

async function handleLogin() {
  isLoading.value = true;
  error.value = '';

  try {
    const formData = new URLSearchParams();
    formData.append('username', identifier.value);
    formData.append('password', password.value);

    const response = await fetch(`${settingsStore.apiBaseUrl}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    const data = await response.json();

    if (response.ok) {
      await authStore.login(data);

      // 检查 URL 中是否有 redirect 参数
      const redirectPath = route.query.redirect; // 使用已定义的 route 变量
      if (redirectPath) {
        await router.push(redirectPath);
      } else {
        await router.push('/');
      }
    } else {
      error.value = data.detail || '登录失败，请检查您的凭据。';
    }
  } catch (err) {
    console.error('登录请求失败:', err);
    error.value = '网络错误或服务器无响应，请稍后重试。';
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
/* 样式保持不变，因为它们不是导致 ReferenceError 的原因 */
.login-view {
  display: flex;
  justify-content: center;
  align-items: center; /* 居中对齐表单 */
  padding: 50px 20px; /* 上下多一些 padding，左右根据 #app 已经有了 */
  min-height: calc(100vh - 160px); /* 减去大致的页眉页脚高度，确保内容区域足够 */
  box-sizing: border-box;
}



.login-form h2 {
  text-align: center;
  color: var(--main-text-color);
  margin-bottom: 30px; /* 增加标题下间距 */
  font-size: 1.8em; /* 调整字体大小 */
  font-weight: normal; /* 配合像素或手绘字体，normal 可能更好看 */
  /* font-family: var(--font-pixel, var(--font-main)); /* 标题可以尝试特定字体 */
}


.login-form {
    background-color: var(--main-bg-color); /* 使用主背景色，使其与内容区融为一体 */
    border: 2px solid var(--border-color);
    box-shadow: none; /* 移除阴影 */
    padding: 2rem;
}

.form-group label {
    font-family: var(--font-special), cursive; /* 标签使用特殊字体 */
    color: var(--link-color);
}

.form-group input, .form-group textarea {
    background-color: rgba(0,0,0,0.2); /* 输入框有半透明的深色背景 */
    font-family: var(--font-main); /* 输入内容使用正文字体 */
    border-color: var(--border-color);
}


.form-group {
  margin-bottom: 25px; /* 增加组间距 */
}




/* 按钮样式主要继承自 main.css */
.form-button {
  width: 100%;
  background-color: #e589a0;
  border-color: #e589a0;
  color: var(--button-text-color);
}

.form-button:hover:not(:disabled) {
  background-color: #600000; /* 手动指定一个更深的红色 */
  border-color: #600000;
}

/* 错误消息样式已在 main.css 定义，这里无需重复，除非需要覆盖 */
/* .message.error { ... } */

.form-links {
  margin-top: 25px;
  text-align: center;
  font-size: 0.9em;
}

.form-links a {
  color: var(--link-color); /* 使用 main.css 定义的链接颜色 */
  text-decoration: underline; /* 游戏风格中下划线可能更常见 */
  margin: 0 8px;
}

.form-links a:hover {
  color: var(--link-hover-color);
}
</style>