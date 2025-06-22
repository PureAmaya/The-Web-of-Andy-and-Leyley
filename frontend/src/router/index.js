// src/router/index.js
import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '../stores/auth'

import HomeView from '../views/HomeView.vue'
import GalleryView from '../views/GalleryView.vue'
import ResetPasswordView from '../views/ResetPasswordView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import UserProfileView from '../views/UserProfileView.vue'
import UploadView from '../views/UploadView.vue'
import RequestPasswordResetView from '../views/RequestPasswordResetView.vue'
import AdminView from '../views/AdminView.vue'
import VerifyEmailView from '../views/VerifyEmailView.vue'; // <--- 新增：导入 VerifyEmailView

import {useSettingsStore} from "@/stores/settings.js"


const routes = [
    {
        path: '/',
        name: 'home',
        component: HomeView
    },
    {
        path: '/gallery',
        name: 'gallery',
        component: GalleryView
    },
    {
        path: '/reset-password',
        name: 'reset-password',
        component: ResetPasswordView,
        meta: {guestOnly: true}
    },
    // <--- 新增：邮箱验证路由
    {
        path: '/verify-email',
        name: 'verify-email',
        component: VerifyEmailView,
        meta: {guestOnly: true} // 邮件验证通常是未登录用户访问
    },
    {
        path: '/login',
        name: 'login',
        component: LoginView,
        meta: {guestOnly: true}
    },
    {
        path: '/register',
        name: 'register',
        component: RegisterView,
        meta: {guestOnly: true}
    },
    {
        path: '/request-password-reset',
        name: 'request-password-reset',
        component: RequestPasswordResetView,
        meta: {guestOnly: true}
    },
    {
        path: '/profile',
        name: 'profile',
        component: UserProfileView,
        meta: {requiresAuth: true}
    },
    {
        path: '/upload',
        name: 'upload',
        component: UploadView,
        meta: {requiresAuth: true}
    },
    {
        path: '/admin-dashboard',
        name: 'admin-dashboard',
        component: AdminView,
        meta: { requiresAuth: true, requiresAdmin: true }
    }
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
});

router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
    const settingsStore = useSettingsStore();

    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const guestOnly = to.matched.some(record => record.meta.guestOnly);
    const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin);

    if (to.name === 'register' && !settingsStore.isRegistrationEnabled) {
        return next({ name: 'home' });
    }

    if (requiresAuth && !authStore.isLoggedIn) {
        return next({ name: 'login', query: { redirect: to.fullPath } });
    }

    if (requiresAdmin && authStore.user?.role !== 'admin') {
        return next({ name: 'home' });
    }

    if (guestOnly && authStore.isLoggedIn) {
        return next({ name: 'home' });
    }

    next();
});

export default router;