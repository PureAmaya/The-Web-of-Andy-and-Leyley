<template>
  <div class="register-view">
    <div class="register-form">
      <h2>创建您的账户</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">用户名:</label>
          <input type="text" id="username" v-model="formData.username" required />
          <p v-if="formErrors.username" class="validation-error">{{ formErrors.username }}</p>
        </div>

        <div class="form-group">
          <label for="email">邮箱:</label>
          <input type="email" id="email" v-model="formData.email" required />
          <p v-if="formErrors.email" class="validation-error">{{ formErrors.email }}</p>
        </div>

        <div class="form-group">
          <label for="password">密码 (至少8位):</label>
          <input type="password" id="password" v-model="formData.password" required minlength="8" />
          <p v-if="formErrors.password" class="validation-error">{{ formErrors.password }}</p>
        </div>

        <div class="form-group">
          <label for="confirm-password">确认密码:</label>
          <input type="password" id="confirm-password" v-model="formData.confirmPassword" required />
          <p v-if="formErrors.confirmPassword" class="validation-error">{{ formErrors.confirmPassword }}</p>
        </div>

        <div class="form-group">
          <label for="full-name">全名 (可选):</label>
          <input type="text" id="full-name" v-model="formData.full_name" />
        </div>

        <div class="form-group">
          <label for="bio">简介 (可选):</label>
          <textarea id="bio" v-model="formData.bio" rows="3"></textarea>
        </div>

        <button type="submit" class="form-button" :disabled="isLoading">
          {{ isLoading ? '注册中...' : '注册' }}
        </button>

        <p v-if="message" :class="['message', messageType]">{{ message }}</p>
      </form>
      <div class="form-links">
        <RouterLink to="/login">已有账户？直接登录</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue';
import { useRouter, RouterLink } from 'vue-router';

import { useSettingsStore } from '@/stores/settings';
const settingsStore = useSettingsStore();

const router = useRouter();

const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  full_name: '', // 对应 UserCreate 模型的 full_name
  bio: '',       // 对应 UserCreate 模型的 bio
});

const formErrors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
});

const isLoading = ref(false);
const message = ref('');
const messageType = ref(''); // 'success' or 'error'

// 简单的前端验证逻辑
watch(() => formData.password, (newVal) => {
  if (newVal && newVal.length < 8) {
    formErrors.password = '密码至少需要8位。';
  } else {
    formErrors.password = '';
  }
  if (formData.confirmPassword && newVal !== formData.confirmPassword) {
    formErrors.confirmPassword = '两次输入的密码不匹配。';
  } else if (formData.confirmPassword) {
    formErrors.confirmPassword = '';
  }
});

watch(() => formData.confirmPassword, (newVal) => {
  if (formData.password && newVal !== formData.password) {
    formErrors.confirmPassword = '两次输入的密码不匹配。';
  } else {
    formErrors.confirmPassword = '';
  }
});

function validateForm() {
  let isValid = true;
  // 清空之前的错误
  Object.keys(formErrors).forEach(key => formErrors[key] = '');

  if (!formData.username) {
    formErrors.username = '用户名为必填项。';
    isValid = false;
  }
  if (!formData.email) {
    formErrors.email = '邮箱为必填项。';
    isValid = false;
  } else if (!/^\S+@\S+\.\S+$/.test(formData.email)) {
    formErrors.email = '请输入有效的邮箱地址。';
    isValid = false;
  }
  if (!formData.password) {
    formErrors.password = '密码为必填项。';
    isValid = false;
  } else if (formData.password.length < 8) {
    formErrors.password = '密码至少需要8位。';
    isValid = false;
  }
  if (formData.password !== formData.confirmPassword) {
    formErrors.confirmPassword = '两次输入的密码不匹配。';
    isValid = false;
  }
  return isValid;
}

async function handleRegister() {
  message.value = '';
  messageType.value = '';

  if (!validateForm()) {
    return;
  }

  isLoading.value = true;

  // 准备发送到后端的数据，确保字段名与 UserCreate Pydantic 模型匹配
  const payload = {
    username: formData.username,
    email: formData.email,
    password: formData.password,
    full_name: formData.full_name || null, // 可选字段，如果为空则发送 null
    bio: formData.bio || null,             // 可选字段，如果为空则发送 null
    // avatar_url, is_active, is_verified 由后端处理
  };

  try {
    const response = await fetch(`${settingsStore.apiBaseUrl}/auth/register`, { //
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (response.ok) { // Status 201 Created
      message.value = `注册成功！ ${data.username}，请检查您的邮箱 ${data.email} 以完成验证。`;
      messageType.value = 'success';
      // 清空表单或部分清空
      formData.username = '';
      formData.email = '';
      formData.password = '';
      formData.confirmPassword = '';
      formData.full_name = '';
      formData.bio = '';
      // 可以在几秒后跳转到登录页或显示更详细的提示
      setTimeout(() => {
        // router.push('/login'); // 例如，跳转到登录页
      }, 5000);
    } else {
      // 处理后端返回的错误信息 (例如用户名或邮箱已存在)
      if (data.detail) {
         // FastAPI 通常会将验证错误放在 detail 中，可能是一个字符串或一个包含多个错误的列表
        if (typeof data.detail === 'string') {
            message.value = data.detail;
        } else if (Array.isArray(data.detail)) {
            // 如果是 FastAPI 的 ValidationError，detail 是一个错误对象列表
            // 这里简化处理，只显示第一个错误，或者您可以选择更复杂的错误展示方式
            message.value = data.detail.map(err => `${err.loc.join('.')} - ${err.msg}`).join('; ');
        } else {
            message.value = '注册失败，请检查您输入的信息。';
        }
      } else {
        message.value = '注册失败，未知错误。';
      }
      messageType.value = 'error';
    }
  } catch (err) {
    console.error('注册请求失败:', err);
    message.value = '网络错误或服务器无响应，请稍后重试。';
    messageType.value = 'error';
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.register-view {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 30px 20px;
  min-height: calc(100vh - 160px);
  box-sizing: border-box;
}


.register-form h2 {
  text-align: center;
  color: var(--main-text-color);
  margin-bottom: 30px;
  font-size: 1.8em;
  font-weight: normal;
  /* font-family: var(--font-pixel, var(--font-main)); */
}

 .register-form {
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
  margin-bottom: 20px; /* 注册表单字段多，间距可以稍小 */
}


/* 按钮样式主要继承自 main.css */
.form-button {
  width: 100%;
  /* 注册按钮颜色可以与登录按钮不同，或者也使用强调色 */
  background-color: #b1d185; /* 示例：深一点的绿色 */
  border-color: #b1d185;
  color: var(--button-text-color); /* 确保文字颜色高对比 */
}

.form-button:hover:not(:disabled) {
  background-color: #2a5c2a; /* 深一点的绿色悬停 */
  border-color: #2a5c2a;
}

.validation-error { /* 确保验证错误信息样式存在且清晰 */
    color: var(--primary-accent-color); /* 用强调色显示错误 */
    font-size: 0.85em;
    margin-top: 5px;
    min-height: 1em; /* 避免没有错误时布局跳动 */
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