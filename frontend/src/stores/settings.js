﻿import {defineStore} from 'pinia';
import {ref} from 'vue';
import apiClient from "@/api.js";

// 定义一个默认的配置对象，作为备用方案
const DEFAULT_SITE_CONFIG = {
    "apiBaseUrl": "http://127.0.0.1:8000",
    "heroSection": {
        "title": "欢迎来到您的网站",
        "subtitle": "请在后台管理面板中修改此内容"
    },
    "contactInfo": {
        "title": "联系我们",
        "description": "",
        "items": []
    },
    "footer": {
        "copyrightOwner": "网站所有者",
        "startYear": new Date().getFullYear(),
        "customHtml": ""
    },
    "beian": {"icp": "", "gongan": {"text": "", "link": ""}},
    "aboutPageHtml": "<h1>关于</h1><p>请在后台管理面板中编辑此页面的内容。</p>",
    "trackingCode": ""
};

// 定义日间模式的颜色主题变量
const lightThemeColors = {
    '--main-bg-color': '#f4f1e9',
    '--secondary-bg-color': '#e8e3d9',
    '--main-text-color': '#3d352e',
    '--border-color': '#c5bbae',
    '--link-color': '#5a4f45',
    '--link-hover-color': '#8c4343',
    '--primary-accent-color': '#8c4343',
    '--button-text-color': '#f4f1e9', // 用于深色/彩色背景的按钮
    '--button-light-bg-text-color': '#3d352e', // 用于浅色背景的按钮
    '--secondary-accent-color': '#38761d',

    // 覆盖 base.css 的变量
    '--color-background': 'var(--main-bg-color)',
    '--color-background-soft': '#fdfbf5',
    '--color-background-mute': '#e8e3d9',
    '--color-border': 'var(--border-color)',
    '--color-border-hover': '#a99d91',
    '--color-heading': '#3d352e',
    '--color-text': 'var(--main-text-color)',
};

// 定义夜间模式的颜色主题变量
const darkThemeColors = {
    '--main-bg-color': '#1a1a1a',
    '--secondary-bg-color': '#2b2b2b',
    '--main-text-color': '#e0e0e0',
    '--border-color': '#444',
    '--link-color': '#c0c0c0',
    '--link-hover-color': '#ffffff',
    '--primary-accent-color': '#7f0000',
    '--button-text-color': '#f0f0f0', // 用于深色/彩色背景的按钮
    '--button-light-bg-text-color': '#e0e0e0', // 在夜间模式下，浅色背景按钮也使用浅色文字
    '--secondary-accent-color': '#38761d',

    // 覆盖 base.css 的变量
    '--color-background': 'var(--main-bg-color)',
    '--color-background-soft': '#222222',
    '--color-background-mute': '#282828',
    '--color-border': 'var(--border-color)',
    '--color-border-hover': '#545454',
    '--color-heading': '#ffffff',
    '--color-text': 'var(--main-text-color)',
};


export const useSettingsStore = defineStore('settings', () => {
    // --- State ---
    const trackingCode = ref('');
    const apiBaseUrl = ref(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000');
    const contactInfo = ref({});
    const beian = ref({});
    const availableThemes = ['light', 'dark', 'system'];
    const theme = ref(localStorage.getItem('theme_preference') || 'system');
    const currentAppliedTheme = ref('light');
    const isRegistrationEnabled = ref(true);
    const heroSection = ref({});
    const footer = ref({});
    const aboutPageHtml = ref(''); // <--- 新增的状态

    // --- Actions ---

    // 辅助函数，用于将配置对象加载到 store 中
    function loadConfig(config) {
        apiBaseUrl.value = config.apiBaseUrl || 'http://localhost:8000';
        contactInfo.value = config.contactInfo || {};
        beian.value = config.beian || {};
        heroSection.value = config.heroSection || {};
        footer.value = config.footer || {};
        aboutPageHtml.value = config.aboutPageHtml || '';
        trackingCode.value = config.trackingCode || '';
    }


    function applyThemeVariables(themeToApply) {
        const root = document.documentElement;
        const colors = themeToApply === 'dark' ? darkThemeColors : lightThemeColors;
        for (const [variable, value] of Object.entries(colors)) {
            root.style.setProperty(variable, value);
        }
        currentAppliedTheme.value = themeToApply;
        root.className = `theme-${themeToApply}`;
    }

    function determineEffectiveTheme() {
        if (theme.value === 'system') {
            return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return theme.value;
    }

    function setTheme(chosenTheme) {
        if (availableThemes.includes(chosenTheme)) {
            theme.value = chosenTheme;
            localStorage.setItem('theme_preference', chosenTheme);
            applyThemeVariables(determineEffectiveTheme());
        }
    }

    function initializeTheme() {
        applyThemeVariables(determineEffectiveTheme());
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
                if (theme.value === 'system') {
                    applyThemeVariables(event.matches ? 'dark' : 'light');
                }
            });
        }
    }

    async function initialize() {
        // 2. 尝试从 /public 目录加载远程配置
        try {
            const response = await fetch('/site-config.json');
            if (!response.ok) {
                // 如果文件不存在 (404)，则抛出错误，进入catch块
                throw new Error('Failed to fetch config, will use default.');
            }
            const config = await response.json();
            loadConfig(config);
        } catch (error) {
            // 3. 如果加载失败，则加载内置的默认配置
            console.warn('无法加载 site-config.json，已使用内置的默认配置。', error.message);
            loadConfig(DEFAULT_SITE_CONFIG);
        }

        // 4. 之后再加载依赖于 apiBaseUrl 的后端配置
        try {
            const publicConfig = await apiClient.get('/config/public');
            isRegistrationEnabled.value = publicConfig.enable_registration;
        } catch(error) {
            console.error("无法从后端加载公共配置:", error);
        }

        initializeTheme(); // 主题初始化保持不变
    }

    return {
        apiBaseUrl,
        contactInfo,
        beian,
        footer,
        heroSection,
        isRegistrationEnabled,
        theme,
        currentAppliedTheme,
        availableThemes,
        aboutPageHtml,
        trackingCode,
        initialize,
        setTheme,
    };
});