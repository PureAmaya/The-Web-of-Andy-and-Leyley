// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import GalleryView from '../views/GalleryView.vue'
import ResetPassword from '../views/ResetPassword.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: GalleryView // 默认主页显示画廊
    },
    {
      path: '/gallery', // 也可以定义一个独立的画廊路径
      name: 'gallery',
      component: GalleryView
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: ResetPassword
    }
    // ... 其他路由
  ]
})

export default router