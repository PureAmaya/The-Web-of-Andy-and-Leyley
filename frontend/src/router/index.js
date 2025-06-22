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
    }
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
});

router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const guestOnly = to.matched.some(record => record.meta.guestOnly);
    const settingsStore = useSettingsStore();

    // 如果注册功能已关闭，且用户正要访问注册页，则重定向到首页
    if (to.name === 'register' && !settingsStore.isRegistrationEnabled) {
        next({name: 'home'});
    }


    if (requiresAuth && !authStore.isLoggedIn) {
        next({name: 'login', query: {redirect: to.fullPath}});
    } else if (guestOnly && authStore.isLoggedIn) {
        next({name: 'home'}); // 已登录用户访问访客页，跳转到首页
    } else {
        next();
    }
});

export default router;