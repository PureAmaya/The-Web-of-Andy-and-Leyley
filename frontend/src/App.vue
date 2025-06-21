<template>
  <div id="app-layout">
    <header class="app-header">
      <div class="header-content">
        <div class="logo">
          <RouterLink to="/">莉莉和安迪的门户</RouterLink>
        </div>
        <nav class="main-nav">
          <RouterLink to="/gallery" class="nav-link">画廊</RouterLink>
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
      <RouterView/>
    </main>

    <TheFooter />
  </div>
</template>

<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router';
import { onMounted, ref, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';
import TheFooter from '@/components/TheFooter.vue'; // 导入页脚组件

const authStore = useAuthStore();
const settingsStore = useSettingsStore();
const router = useRouter();

const selectedTheme = ref(settingsStore.theme);

watch(() => settingsStore.theme, (newThemePreference) => {
    if (selectedTheme.value !== newThemePreference) {
        selectedTheme.value = newThemePreference;
    }
});

// onMounted 钩子负责初始化整个应用
onMounted(async () => {
  // 1. 初始化所有配置和主题
  await settingsStore.initialize();
  selectedTheme.value = settingsStore.theme;

  // 2. 检查认证状态并获取用户信息
  if (authStore.accessToken && !authStore.user) {
    await authStore.fetchAndSetUser();
  }
});

function handleLogout() {
  authStore.logout();
  router.push('/login'); // 登出后跳转到登录页
}

function onThemeChange() {
  settingsStore.setTheme(selectedTheme.value);
}
</script>

<style scoped>
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
  position: sticky; /* 使头部在滚动时固定在顶部 */
  top: 0;
  z-index: 999;
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

.main-nav {
  display: flex;
  align-items: center;
  gap: 8px; /* 可以调整链接间距 */
  margin-left: 20px; /* Logo和导航间的距离 */
  margin-right: auto; /* 关键：将导航推到左边，将右侧内容推到右边 */
  flex-wrap: wrap; /* 允许导航在空间不足时换行 */
}

.nav-link {
  color: var(--link-color);
  text-decoration: none;
  padding: 0.5rem 0.8rem;
  transition: background-color 0.2s, color 0.2s;
  font-size: 0.9rem;
  border: 1px solid transparent;
  white-space: nowrap;
}

.nav-link:hover,
.nav-link.router-link-exact-active {
  background-color: var(--border-color);
  color: var(--link-hover-color);
}

.nav-button.logout-button {
  background-color: transparent;
  color: var(--link-color);
  border: 1px solid var(--border-color);
  padding: 0.5rem 0.8rem;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
  font-size: 0.9rem;
  white-space: nowrap;
  font-family: inherit;
  text-transform: uppercase;
}

.nav-button.logout-button:hover {
  background-color: var(--primary-accent-color);
  color: var(--button-text-color);
  border-color: var(--primary-accent-color);
}

.theme-switcher {
  margin-left: 20px;
  display: flex;
  align-items: center;
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

.app-content {
  flex-grow: 1; /* 让主要内容区域占据剩余的所有空间 */
  padding: 20px;
  width: 100%;
  max-width: 1200px; /* 限制内容最大宽度 */
  margin: 0 auto; /* 水平居中 */
  box-sizing: border-box;
}
</style>