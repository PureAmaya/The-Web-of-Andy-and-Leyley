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
        <RouterLink to="/register">还没有账户？立即注册</RouterLink>
        <br/>
        <RouterLink to="/request-password-reset">忘记密码？</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref} from 'vue';

import { useSettingsStore } from '@/stores/settings';
const settingsStore = useSettingsStore();

import {useRouter, RouterLink} from 'vue-router';
import {useAuthStore} from '@/stores/auth'; // 1. 导入 authStore


const router = useRouter();
const authStore = useAuthStore(); // 2. 获取 authStore 实例

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
      const redirectPath = route.query.redirect;
      if (redirectPath) {
        await router.push(redirectPath); // 跳转到之前想访问的页面
      } else {
        await router.push('/'); // 否则跳转到主页
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
.login-view {
  display: flex;
  justify-content: center;
  align-items: center; /* 居中对齐表单 */
  padding: 50px 20px; /* 上下多一些 padding，左右根据 #app 已经有了 */
  min-height: calc(100vh - 160px); /* 减去大致的页眉页脚高度，确保内容区域足够 */
  box-sizing: border-box;
}

.login-form {
  max-width: 380px; /* 调整宽度 */
  width: 100%;
  padding: 30px 35px; /* 调整内边距 */
  background-color: var(--secondary-bg-color); /* 使用次级背景色 */
  border: 1px solid var(--border-color);
  box-shadow: 0 0 15px rgba(226, 138, 162, 0.3); /* 尝试用强调色做阴影，可选 */
  /* 设计风格参考：可以考虑使用类似游戏UI的边框图片或更粗糙的边框 */
}

.login-form h2 {
  text-align: center;
  color: var(--main-text-color);
  margin-bottom: 30px; /* 增加标题下间距 */
  font-size: 1.8em; /* 调整字体大小 */
  font-weight: normal; /* 配合像素或手绘字体，normal 可能更好看 */
  /* font-family: var(--font-pixel, var(--font-main)); /* 标题可以尝试特定字体 */
}

.form-group {
  margin-bottom: 25px; /* 增加组间距 */
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: normal; /* 调整字重 */
  color: var(--main-text-color);
  font-size: 0.95em;
}

/* 输入框样式主要继承自 main.css，这里可以进行微调 */
.form-group input {
  /* 如果 main.css 中定义的样式已满足，这里可以留空或只写差异部分 */
  /* 例如，确保高度和字体与设计一致 */
  padding: 12px 10px;
}


/* 按钮样式主要继承自 main.css */
.form-button {
  /* 继承了 main.css 的大部分样式 */
  width: 100%;
  background-color: #e589a0; /* 主要行动按钮使用强调色 */
  border-color: #e589a0; /* 比强调色稍暗的边框 */
  color: var(--button-text-color); /* 确保文字颜色高对比 */
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