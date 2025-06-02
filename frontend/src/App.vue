<template>
  <div id="app-layout">
    <header class="app-header">
      <div class="header-content">
        <div class="logo">
          <RouterLink to="/">莉莉和安迪的门户</RouterLink>
        </div>
        <nav class="main-nav">
          <RouterLink to="/" class="nav-link">画廊</RouterLink>
          <RouterLink v-if="authStore.isLoggedIn" to="/upload" class="nav-link">上传作品</RouterLink>

          <template v-if="authStore.isLoggedIn">
            <RouterLink to="/profile" class="nav-link">
              {{ authStore.user?.username || '档案' }}
            </RouterLink>
            <button @click="handleLogout" class="nav-button logout-button">离去</button>
          </template>
          <template v-else>
            <RouterLink to="/login" class="nav-link">登录</RouterLink>
            <RouterLink to="/register" class="nav-link">注册</RouterLink>
          </template>
        </nav>

        <div class="theme-switcher">
          <label for="theme-select" class="visually-hidden">选择主题:</label>
          <select id="theme-select" v-model="selectedTheme" @change="onThemeChange" aria-label="选择颜色主题">
            <option value="system">跟随系统</option>
            <option value="light">日间模式</option>
            <option value="dark">夜间模式</option>
          </select>
        </div>
      </div>
    </header>

    <main class="app-content">
      <RouterView />
    </main>

    <footer class="app-footer">
      <div class="footer-content">
        <p>&copy; {{ new Date().getFullYear() }} L&A. All rights reserved.</p>
        <div class="api-config-section">
          <div class="api-url-input-group">
            <label for="api-url-input">后端 API 地址:</label>
            <input type="text" id="api-url-input" v-model="editableApiUrl" placeholder="例如: http://localhost:8000" />
            <button @click="saveApiUrl" class="api-button save-button">保存</button>
            <button @click="resetApiUrl" class="api-button reset-button" title="恢复默认值">重置</button>
          </div>
          <button @click="testApiConnection" class="api-button test-button" :disabled="isTestingConnection">
            {{ isTestingConnection ? '测试中...' : '测试连接' }}
          </button>
          <p v-if="testConnectionMessage" :class="['connection-status', testConnectionStatus]">
            {{ testConnectionMessage }}
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
// ... (script setup 部分大部分保持不变)
import { RouterLink, RouterView, useRouter } from 'vue-router';
import { onMounted, ref, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';

const authStore = useAuthStore();
const settingsStore = useSettingsStore();
const router = useRouter();

const editableApiUrl = ref(settingsStore.apiBaseUrl);
const isTestingConnection = ref(false);
const testConnectionMessage = ref('');
const testConnectionStatus = ref('');
const selectedTheme = ref(settingsStore.theme);

watch(() => settingsStore.apiBaseUrl, (newUrl) => {
  if (editableApiUrl.value !== newUrl) {
    editableApiUrl.value = newUrl;
  }
});
watch(() => settingsStore.theme, (newThemePreference) => {
    if (selectedTheme.value !== newThemePreference) {
        selectedTheme.value = newThemePreference;
    }
});

onMounted(async () => {
  if (authStore.accessToken && !authStore.user) {
    await authStore.fetchAndSetUser();
  }
  settingsStore.initializeTheme();
  selectedTheme.value = settingsStore.theme;
});

function handleLogout() {
  authStore.logout();
}
function saveApiUrl() {
  settingsStore.setApiBaseUrl(editableApiUrl.value);
  testConnectionMessage.value = 'API 地址已更新并保存！';
  testConnectionStatus.value = 'success';
  setTimeout(() => testConnectionMessage.value = '', 3000);
}
function resetApiUrl() {
    settingsStore.setApiBaseUrl(settingsStore.DEFAULT_API_BASE_URL);
    editableApiUrl.value = settingsStore.apiBaseUrl;
    testConnectionMessage.value = 'API 地址已重置为默认值！';
    testConnectionStatus.value = 'success';
    setTimeout(() => testConnectionMessage.value = '', 3000);
}
async function testApiConnection() {
  isTestingConnection.value = true;
  testConnectionMessage.value = '';
  testConnectionStatus.value = '';
  const urlToTest = settingsStore.apiBaseUrl;
  if (!urlToTest) {
    testConnectionMessage.value = 'API 地址不能为空。';
    testConnectionStatus.value = 'error';
    isTestingConnection.value = false;
    return;
  }
  try {
    const response = await fetch(urlToTest);
    if (response.ok) {
      testConnectionMessage.value = `连接成功！(状态码: ${response.status})`;
      testConnectionStatus.value = 'success';
    } else {
      testConnectionMessage.value = `连接失败。状态码: ${response.status}.`;
      testConnectionStatus.value = 'error';
    }
  } catch (error) {
    testConnectionMessage.value = `连接出错: ${error.message}.`;
    testConnectionStatus.value = 'error';
  } finally {
    isTestingConnection.value = false;
  }
}
function onThemeChange() {
  settingsStore.setTheme(selectedTheme.value);
}
</script>

<style scoped>
/* ... (App.vue 的样式保持不变) ... */
/* 确保 main-nav 的样式能容纳新的链接 */
.main-nav {
  display: flex;
  align-items: center;
  gap: 8px; /* 可以调整链接间距 */
  margin-right: auto;
  flex-wrap: wrap; /* 允许导航在空间不足时换行 */
}
/* 其他样式 ... */
#app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--main-bg-color);
}

.app-header {
  background-color: var(--secondary-bg-color);
  color: var(--main-text-color);
  padding: 0.8rem 1rem;
  border-bottom: 1px solid var(--border-color);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.logo a {
  color: var(--main-text-color);
  text-decoration: none;
  font-size: 1.6rem;
  font-weight: normal;
}

.nav-link {
  color: var(--link-color);
  text-decoration: none;
  padding: 0.5rem 0.8rem;
  border-radius: 0;
  transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out;
  font-size: 0.9rem;
  border: 1px solid transparent;
  white-space: nowrap; /* 防止链接文字换行 */
}

.nav-link:hover,
.nav-link.router-link-exact-active {
  background-color: var(--border-color);
  color: var(--link-hover-color);
  border-color: var(--primary-accent-color);
}

.nav-button.logout-button {
  background-color: transparent;
  color: var(--link-color);
  border: 1px solid var(--border-color);
  padding: 0.5rem 0.8rem;
  border-radius: 0;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out, border-color 0.2s ease-in-out;
  font-size: 0.9rem;
  white-space: nowrap;
}
.nav-button.logout-button:hover {
  background-color: var(--primary-accent-color);
  color: var(--main-text-color);
  border-color: var(--primary-accent-color);
}
.theme-switcher {
  margin-left: 20px;
  display: flex;
  align-items: center;
}
.theme-switcher label.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
.theme-switcher select {
  background-color: var(--secondary-bg-color);
  color: var(--main-text-color);
  border: 1px solid var(--border-color);
  padding: 0.4rem 0.6rem;
  border-radius: 0;
  font-size: 0.85rem;
  cursor: pointer;
  outline-color: var(--primary-accent-color);
}
.theme-switcher select:focus {
    border-color: var(--primary-accent-color);
}
.app-content {
  flex-grow: 1;
  padding: 20px;
}
.app-footer {
  background-color: var(--secondary-bg-color);
  color: #888;
  text-align: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  margin-top: auto;
  font-size: 0.8rem;
}
.footer-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}
.api-config-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.api-url-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}
.api-config-section label {
  font-size: 0.9em;
  color: var(--link-color);
}
.api-button.save-button {
  background-color: #1a6e1a;
}
.api-button.save-button:hover:not(:disabled) {
  background-color: #124e12;
}
.api-button.reset-button {
  background-color: #b8860b;
  color: var(--main-text-color);
}
.api-button.reset-button:hover:not(:disabled) {
  background-color: #8b6508;
}
.api-button.test-button {
  background-color: #0056b3;
}
.api-button.test-button:hover:not(:disabled) {
  background-color: #003f80;
}
.connection-status {
  font-size: 0.85em;
  margin-top: 5px;
  padding: 5px 10px;
  border-radius: 0;
  text-align: center;
  min-height: 1.5em;
  border: 1px solid transparent;
}
.connection-status.success {
  color: #a3d9b1;
  background-color: rgba(40, 167, 69, 0.2);
  border-color: #28a745;
}
.connection-status.error {
  color: #f8d7da;
  background-color: rgba(220, 53, 69, 0.2);
  border-color: #dc3545;
}
</style>