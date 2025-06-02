<template>
  <div class="reset-password-view">
    <div class="reset-password-form">
      <h2>重置密码</h2>
      <p v-if="!token && !initialCheckDone" class="message">正在检查链接...</p>
      <p v-if="!token && initialCheckDone" class="message error">
        无效的密码重置链接。请确保您使用了完整的链接，或者重新请求密码重置。
      </p>
      <form @submit.prevent="handleResetPassword" v-if="token">
        <div class="form-group">
          <label for="new-password">新密码:</label>
          <input type="password" id="new-password" v-model="newPassword" required minlength="8" />
          <p v-if="newPasswordError" class="validation-error">{{ newPasswordError }}</p>
        </div>
        <div class="form-group">
          <label for="confirm-password">确认新密码:</label>
          <input type="password" id="confirm-password" v-model="confirmPassword" required />
          <p v-if="confirmPasswordError" class="validation-error">{{ confirmPasswordError }}</p>
        </div>
        <button type="submit" class="form-button" :disabled="isLoading || !!newPasswordError || !!confirmPasswordError">
          {{ isLoading ? '提交中...' : '重置密码' }}
        </button>

        <p v-if="message" :class="['message', messageType]">{{ message }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router'; // 导入 useRoute 和 useRouter

import { useSettingsStore } from '@/stores/settings'; // 导入设置存储
const settingsStore = useSettingsStore();

const route = useRoute(); // 获取当前路由信息
const router = useRouter(); // 获取路由器实例，用于导航

const token = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const isLoading = ref(false);
const message = ref('');
const messageType = ref(''); // 'success' or 'error'
const initialCheckDone = ref(false);


// 验证错误信息
const newPasswordError = ref('');
const confirmPasswordError = ref('');

// 客户端验证
watch(newPassword, (newValue) => {
  if (newValue.length > 0 && newValue.length < 8) {
    newPasswordError.value = '密码至少需要8位。';
  } else {
    newPasswordError.value = '';
  }
  // 重新验证确认密码
  if (confirmPassword.value && newValue !== confirmPassword.value) {
    confirmPasswordError.value = '新密码与确认密码不匹配。';
  } else if (confirmPassword.value) { // 如果确认密码有值，且新密码修改后匹配了，则清除错误
     confirmPasswordError.value = '';
  }
});

watch(confirmPassword, (newValue) => {
  if (newPassword.value !== newValue) {
    confirmPasswordError.value = '新密码与确认密码不匹配。';
  } else {
    confirmPasswordError.value = '';
  }
});


onMounted(() => {
  // 从 URL 查询参数中获取 token (使用 Vue Router 的方式)
  token.value = route.query.token || '';
  initialCheckDone.value = true;

  if (!token.value) {
    message.value = '密码重置令牌缺失或无效。请检查您的重置链接。';
    messageType.value = 'error';
  }
});

async function handleResetPassword() {
  message.value = '';
  messageType.value = '';

  // 触发一次最终的客户端验证
  if (newPassword.value.length < 8) {
    newPasswordError.value = '密码至少需要8位。';
    return;
  } else {
    newPasswordError.value = '';
  }

  if (newPassword.value !== confirmPassword.value) {
    confirmPasswordError.value = '新密码与确认密码不匹配。';
    return;
  } else {
    confirmPasswordError.value = '';
  }


  isLoading.value = true;
  try {
    const response = await fetch(`${settingsStore.apiBaseUrl}/auth/reset-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: token.value,
        new_password: newPassword.value,
        new_password_confirm: confirmPassword.value,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      message.value = data.message || '密码已成功重置。您现在可以尝试登录了。';
      messageType.value = 'success';
      newPassword.value = ''; // 清空表单
      confirmPassword.value = '';
      // 可选：几秒后跳转到登录页
      setTimeout(() => {
        router.push('/login'); // 假设您有一个 /login 路由
      }, 3000);
    } else {
      message.value = data.detail || '重置密码失败，请重试。';
      messageType.value = 'error';
    }
  } catch (err) {
    console.error('重置密码请求失败:', err);
    message.value = '网络错误或服务器无响应，请稍后重试。';
    messageType.value = 'error';
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.reset-password-view { /* 根元素类名不同 */
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 50px 20px;
  min-height: calc(100vh - 160px);
  box-sizing: border-box;
}

.reset-password-form { /* 表单类名也不同 */
  max-width: 380px;
  width: 100%;
  padding: 30px 35px;
  background-color: var(--secondary-bg-color);
  border: 1px solid var(--border-color);
}

.reset-password-form h2 {
  text-align: center;
  color: var(--main-text-color);
  margin-bottom: 30px;
  font-size: 1.8em;
  font-weight: normal;
  /* font-family: var(--font-pixel, var(--font-main)); */
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: normal;
  color: var(--main-text-color);
  font-size: 0.95em;
}

.form-group input {
  padding: 12px 10px;
}

.form-button {
  width: 100%;
  background-color: var(--primary-accent-color); /* 重置密码按钮也用强调色 */
  border-color: var(--primary-accent-color);
  color: var(--main-text-color);
}

.form-button:hover:not(:disabled) {
  background-color: #600000; /* 手动指定一个更深的红色 */
  border-color: #600000;
}

.validation-error {
    color: var(--primary-accent-color);
    font-size: 0.85em;
    margin-top: 5px;
    min-height: 1em;
}

/* message 样式继承自 main.css */
</style>