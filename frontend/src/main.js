import { createApp } from 'vue'
import { createPinia } from 'pinia' // 1. 从 pinia 导入 createPinia

import App from './App.vue'
import router from './router'

import './assets/main.css'

const app = createApp(App)

// 2. 创建 Pinia 实例
const pinia = createPinia()

// 3. 将 Pinia 实例提供给应用
app.use(pinia) //确保在 app.use(router) 之前或之后都可以，但通常建议先注册核心插件
app.use(router)

app.mount('#app')