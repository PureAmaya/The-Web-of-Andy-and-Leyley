// 文件: frontend/src/main.js

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useSettingsStore } from './stores/settings' // 1. 导入 settings store

import './assets/main.css'

// 2. 将应用的创建和挂载过程包装在一个异步函数中
async function initializeAndMountApp() {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)

  // 3. 在挂载应用前，先执行异步初始化
  // 这一步是关键！
  const settingsStore = useSettingsStore()
  await settingsStore.initialize() // 等待 site-config.json 加载完毕

  // 4. 等所有配置都就绪后，再注册路由器和挂载应用
  app.use(router)
  app.mount('#app')
}

// 5. 调用这个异步函数来启动应用
initializeAndMountApp()