// src/router/index.js
import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '../stores/auth'
import {useSettingsStore} from "@/stores/settings.js"


const routes = [
    {
        path: '/',
        name: 'home',
        component: () => import('../views/HomeView.vue')
    },
    {
        path: '/gallery',
        name: 'gallery',
        component: () => import('../views/GalleryView.vue')
    },
    {
        path: '/reset-password',
        name: 'reset-password',
        component: () => import('../views/ResetPasswordView.vue'),
        meta: {guestOnly: true}
    },
    {
        path: '/verify-email',
        name: 'verify-email',
        component: () => import('../views/VerifyEmailView.vue'),
        meta: {guestOnly: true}
    },
    {
        path: '/login',
        name: 'login',
        component: () => import('../views/LoginView.vue'),
        meta: {guestOnly: true}
    },
    {
        path: '/register',
        name: 'register',
        component: () => import('../views/RegisterView.vue'),
        meta: {guestOnly: true}
    },
    {
        path: '/request-password-reset',
        name: 'request-password-reset',
        component: () => import('../views/RequestPasswordResetView.vue'),
        meta: {guestOnly: true}
    },
    {
        path: '/profile',
        name: 'profile',
        component: () => import('../views/UserProfileView.vue'),
        meta: {requiresAuth: true}
    },
    {
        path: '/upload',
        name: 'upload',
        component: () => import('../views/UploadView.vue'),
        meta: {requiresAuth: true}
    },
    {
        path: '/admin-dashboard',
        name: 'admin-dashboard',
        component: () => import('../views/AdminView.vue'),
        meta: {requiresAuth: true, requiresAdmin: true}
    },
    {
        path: '/about',
        name: 'about',
        component: () => import('../views/AboutView.vue')
    },
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
});

// --- (路由守卫部分保持不变) ---
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
    const settingsStore = useSettingsStore();

    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const guestOnly = to.matched.some(record => record.meta.guestOnly);
    const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin);

    if (to.name === 'register' && !settingsStore.isRegistrationEnabled) {
        return next({name: 'home'});
    }

    if (requiresAuth && !authStore.isLoggedIn) {
        return next({name: 'login', query: {redirect: to.fullPath}});
    }

    if (requiresAdmin && authStore.user?.role !== 'admin') {
        return next({name: 'home'});
    }

    if (guestOnly && authStore.isLoggedIn) {
        return next({name: 'home'});
    }

    next();
});

export default router;