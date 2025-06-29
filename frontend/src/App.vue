<template>
  <div v-if="settingsStore.trackingCode" v-html="settingsStore.trackingCode"></div>

  <div id="app-layout">
    <header class="app-header">
      <div class="header-content">
        <div class="logo">
          <RouterLink to="/">
            <img src="/spiral-logo.png" alt="Logo" class="site-logo-icon"/>
            <span class="site-logo-text">莉莉和安迪的网站</span>
          </RouterLink>
        </div>
        <nav class="main-nav">
          <RouterLink to="/gallery" class="nav-link">画廊</RouterLink>
          <RouterLink to="/about" class="nav-link">关于</RouterLink>
          <RouterLink v-if="authStore.isLoggedIn" to="/upload" class="nav-link">上传作品</RouterLink>
          <RouterLink
              v-if="authStore.isLoggedIn && authStore.isAdmin"
              to="/admin-dashboard"
              class="nav-link"
          >
            管理
          </RouterLink>
          <template v-if="authStore.isLoggedIn">
            <RouterLink to="/profile" class="nav-link">
              {{ authStore.user?.username || '档案' }}
            </RouterLink>
            <button @click="handleLogout" class="nav-button logout-button">离去</button>
          </template>
          <template v-else>
            <RouterLink to="/login" class="nav-link">登录</RouterLink>
            <RouterLink v-if="settingsStore.isRegistrationEnabled" to="/register" class="nav-link">
              注册
            </RouterLink>
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
      <router-view v-slot="{ Component }">
        <transition name="glitch-fade" mode="out-in">
          <KeepAlive>
            <component :is="Component"/>
          </KeepAlive>
        </transition>
      </router-view>
    </main>

    <TheFooter/>

    <GlobalModal />
  </div>
</template>

<script setup>
import {RouterLink, RouterView, useRouter} from 'vue-router';
import {onMounted, ref, watch} from 'vue';
import {useAuthStore} from '@/stores/auth';
import {useSettingsStore} from '@/stores/settings';
import TheFooter from '@/components/TheFooter.vue';
import GlobalModal from '@/components/GlobalModal.vue'; // 导入全局弹窗组件

const authStore = useAuthStore();
const settingsStore = useSettingsStore();
const router = useRouter();
const selectedTheme = ref(settingsStore.theme);

watch(() => settingsStore.theme, (newThemePreference) => {
  if (selectedTheme.value !== newThemePreference) {
    selectedTheme.value = newThemePreference;
  }
});

onMounted(async () => {
  await settingsStore.initialize();
  selectedTheme.value = settingsStore.theme;
  if (authStore.isLoggedIn && !authStore.user) {
    await authStore.fetchAndSetUser();
  }
});

function handleLogout() {
  authStore.logout();
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
  padding: 0.5rem 0;
  border-bottom: 2px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 999;
}

.header-content {
  display: flex;
  align-items: center;
  width: 100%;
  margin: 0 auto;
  padding: 0 2rem;
  box-sizing: border-box;
}

.logo {
  flex-shrink: 0;
}

.logo a {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--main-text-color);
  text-decoration: none;
  font-family: var(--font-special), cursive;
  font-size: 1.4rem;
}

.site-logo-icon {
  height: 32px;
  width: 32px;
  transition: transform 0.5s ease-in-out;
}

.logo a:hover .site-logo-icon {
  transform: rotate(360deg);
}

.theme-switcher {
  display: flex;
  align-items: center;
  gap: 10px;
}

.app-content {
  flex-grow: 1;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
  box-sizing: border-box;
}

.main-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 40px;
  margin-right: auto;
}

.nav-link {
  color: var(--link-color);
  text-decoration: none;
  padding: 0.3rem 0.8rem;
  transition: all 0.2s;
  font-size: 1rem;
  font-family: var(--font-main);
  text-shadow: none;
}

.nav-link:hover, .nav-link.router-link-exact-active {
  color: var(--link-hover-color);
  text-shadow: 0 0 5px var(--primary-accent-color);
}

.nav-button.logout-button {
  background-color: transparent;
  color: var(--link-color);
  border: 2px solid var(--border-color);
  padding: 0.3rem 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 1rem;
  font-family: var(--font-special), cursive;
  text-transform: none;
}

.nav-button.logout-button:hover {
  background-color: var(--primary-accent-color);
  border-color: var(--primary-accent-color);
  color: var(--button-text-color);
}

.theme-switcher select {
  background-color: var(--secondary-bg-color);
  color: var(--main-text-color);
  border: 2px solid var(--border-color);
  padding: 0.4rem 0.6rem;
  font-family: var(--font-main);
  font-size: 0.9rem;
  cursor: pointer;
}

.theme-switcher select:focus {
  outline: 2px solid var(--primary-accent-color);
}

.glitch-fade-enter-active,
.glitch-fade-leave-active {
  transition: opacity 0.3s ease-in-out;
  position: relative;
}

.glitch-fade-enter-from,
.glitch-fade-leave-to {
  opacity: 0;
}

.glitch-fade-enter-active {
  animation: glitch-in 0.3s steps(3) forwards;
}

@keyframes glitch-in {
  0% { transform: translate(-1%, -2%); opacity: 0; }
  25% { transform: translate(2%, 1%); opacity: 0.25; }
  50% { transform: translate(-2%, 2%); opacity: 0.75; }
  100% { transform: translate(0, 0); opacity: 1; }
}


@media (max-width: 860px) {
  .header-content {
    padding: 0 1rem;
    flex-wrap: wrap;
    justify-content: space-between;
  }

  .logo {
    flex-basis: 100%;
    margin-bottom: 0.5rem;
    justify-content: center;
  }

  .site-logo-text {
    font-size: 1.2rem;
  }

  .main-nav {
    margin: 0;
    order: 3;
    flex-basis: 100%;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0;
  }

  .nav-link {
    font-size: 0.9rem;
    padding: 0.3rem 0.6rem;
  }

  .theme-switcher {
    order: 2;
  }

  .app-content {
    padding: 1rem;
  }
}
</style>