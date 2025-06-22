import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '../stores/auth' // 调整为你的实际路径

import HomeView from '../views/HomeView.vue'
import GalleryView from '../views/GalleryView.vue'
import ResetPasswordView from '../views/ResetPasswordView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import UserProfileView from '../views/UserProfileView.vue'
import UploadView from '../views/UploadView.vue'
import RequestPasswordResetView from '../views/RequestPasswordResetView.vue';
import {useSettingsStore} from "@/stores/settings.js"
import AdminView from '../views/AdminView.vue';


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
        meta: {guestOnly: true} // 未登录用户访问
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
        meta: {requiresAuth: true} // 需要认证
    },
    // 2. 添加 /upload 路由
    {
        path: '/upload',
        name: 'upload',
        component: UploadView,
        meta: {requiresAuth: true} // 标记此路由需要认证
    },

    // 管理员路由
     {
        path: '/admin-dashboard', // 使用一个和后端不冲突的路径
        name: 'admin-dashboard',
        component: AdminView,
        // 添加 meta 字段来标记需要管理员权限
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
    const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin); // 新增

    if (to.name === 'register' && !settingsStore.isRegistrationEnabled) {
        return next({ name: 'home' });
    }

    if (requiresAuth && !authStore.isLoggedIn) {
        return next({ name: 'login', query: { redirect: to.fullPath } });
    }

    // --- 新增的管理员权限检查 ---
    // 如果路由需要管理员权限，但当前用户不是管理员
    if (requiresAdmin && authStore.user?.role !== 'admin') {
        // 重定向到首页或一个“无权限”页面
        return next({ name: 'home' });
    }

    if (guestOnly && authStore.isLoggedIn) {
        return next({ name: 'home' });
    }

    next();
});

export default router;