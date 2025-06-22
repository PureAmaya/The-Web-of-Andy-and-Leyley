<template>
  <div class="admin-view">
    <h1 class="page-title">Site Console</h1>
    <p class="page-description">
      管理员维护面板。在此处执行站点级的管理操作。
    </p>

    <div class="admin-actions-grid">
      <div class="action-card">
        <h2 class="card-title">Reload Configuration</h2>
        <p class="card-description">
          修改服务器 `.env` 文件后，点击此按钮使新配置生效，无需重启服务。
        </p>
        <button @click="handleReloadConfig" :disabled="isLoading" class="form-button">
          <span v-if="isLoading">正在执行...</span>
          <span v-else>重载应用配置</span>
        </button>
        <p v-if="reloadMessage" :class="['message', reloadMessageType]">
          {{ reloadMessage }}
        </p>
      </div>

      <div class="action-card">
        <h2 class="card-title">Database Panel</h2>
        <p class="card-description">
          在新标签页中打开 SQLAdmin 后台，对用户、画廊、成员等核心数据进行图形化管理。
        </p>
        <a :href="adminPanelUrl" target="_blank" rel="noopener noreferrer" class="form-button">
          打开 SQLAdmin 面板
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import apiClient from '@/api';
import { useSettingsStore } from '@/stores/settings';

const settingsStore = useSettingsStore();

const isLoading = ref(false);
const reloadMessage = ref('');
const reloadMessageType = ref(''); // 'success' or 'error'

const adminPanelUrl = computed(() => `${settingsStore.apiBaseUrl}/admin`);

async function handleReloadConfig() {
  isLoading.value = true;
  reloadMessage.value = '';

  try {
    const response = await apiClient.post('/admin/reload-config');
    reloadMessage.value = response.message || '配置已成功重载！';
    reloadMessageType.value = 'success';
  } catch (error) {
    if (error.response) {
      reloadMessage.value = `错误: ${error.response.data.detail || error.response.statusText}`;
    } else {
      reloadMessage.value = '网络错误或服务器无响应。';
    }
    reloadMessageType.value = 'error';
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
/* 整个视图的容器 */
.admin-view {
  padding: 2rem 4rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面主标题：使用特殊字体 */
.page-title {
  font-family: var(--font-special), cursive;
  font-size: 3rem;
  font-weight: normal;
  color: var(--main-text-color);
  text-align: center;
  margin-bottom: 1rem;
  text-shadow: 1px 1px 0px var(--border-color);
}

/* 页面描述文字 */
.page-description {
  text-align: center;
  color: var(--link-color);
  margin-bottom: 4rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  font-size: 1.1rem;
}

/* 网格布局 */
.admin-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2.5rem;
}

/* 卡片样式：核心主题化部分 */
.action-card {
  background-color: var(--main-bg-color); /* 使用主背景色，与登录框一致 */
  border: 2px solid var(--border-color); /* 使用更粗的边框 */
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease-in-out;

  /* 轻微旋转卡片，营造手绘/不稳定感 */
  transform: rotate(-1deg);
}

/* 让第二张卡片朝相反方向旋转，增加错落感 */
.action-card:nth-child(even) {
  transform: rotate(1deg);
}

/* 鼠标悬浮时，卡片回正并放大，边框变色 */
.action-card:hover {
  transform: rotate(0deg) scale(1.03);
  border-color: var(--primary-accent-color);
  z-index: 10;
}

/* 卡片标题：同样使用特殊字体 */
.card-title {
  font-family: var(--font-special), cursive;
  font-size: 1.8rem;
  font-weight: normal;
  color: var(--main-text-color);
  margin: 0 0 1rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
}

/* 卡片描述文字 */
.card-description {
  font-family: var(--font-main);
  color: var(--main-text-color);
  opacity: 0.9;
  line-height: 1.7;
  flex-grow: 1; /* 让描述占据多余空间，使按钮对齐到底部 */
  margin-top: 0.5rem;
  margin-bottom: 1.5rem;
}

/* 按钮样式 */
.form-button {
  width: 100%;
  text-align: center;
  text-decoration: none;
  background-color: transparent; /* 默认透明 */
  border: 2px solid var(--border-color); /* 统一边框 */
  color: var(--main-text-color);
  padding: 12px 20px;
  transition: all 0.2s;
}

/* 悬浮时使用主题强调色 */
.form-button:hover:not(:disabled) {
  background-color: var(--primary-accent-color);
  border-color: var(--primary-accent-color);
  color: var(--button-text-color, #fff);
}

/* 加载或禁用时的样式 */
.form-button:disabled {
  background-color: var(--secondary-bg-color);
  color: var(--link-color);
  cursor: not-allowed;
  opacity: 0.6;
}

/* 消息提示的样式 */
.message {
  margin-top: 1rem;
  padding: 0.75rem;
  text-align: center;
  font-size: 0.9em;
  border: 1px dashed transparent;
}

.message.success {
  color: var(--secondary-accent-color, #38761d);
  border-color: var(--secondary-accent-color, #38761d);
}

.message.error {
  color: var(--primary-accent-color);
  border-color: var(--primary-accent-color);
}
</style>