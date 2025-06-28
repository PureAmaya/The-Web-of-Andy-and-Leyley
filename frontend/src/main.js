// 文件: frontend/src/main.js

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useSettingsStore } from './stores/settings'

import './assets/main.css'

async function initializeAndMountApp() {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)

  // ---  在挂载应用前，先执行异步初始化 ---
  // 这是关键步骤，它会暂停后续代码，直到配置加载完成。
  const settingsStore = useSettingsStore()
  await settingsStore.initialize()

  // ---  等所有配置都就绪后，再注册路由器和挂载应用 ---
  app.use(router)
  app.mount('#app')
}

initializeAndMountApp()