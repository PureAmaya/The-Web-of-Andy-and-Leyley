import {defineStore} from 'pinia';
import {ref} from 'vue';
import apiClient from "@/api.js";

// 定义日间模式的颜色主题变量
const lightThemeColors = {
    '--main-bg-color': '#f4f1e9',
    '--secondary-bg-color': '#e8e3d9',
    '--main-text-color': '#3d352e',
    '--border-color': '#c5bbae',
    '--link-color': '#5a4f45',
    '--link-hover-color': '#8c4343',
    '--primary-accent-color': '#8c4343',
    '--button-text-color': '#f4f1e9',
    '--secondary-accent-color': '#38761d',
};

// 定义夜间模式的颜色主题变量
const darkThemeColors = {
    '--main-bg-color': '#121212',
    '--secondary-bg-color': '#1E1E1E',
    '--main-text-color': '#E0E0E0',
    '--border-color': '#333333',
    '--link-color': '#BBBBBB',
    '--link-hover-color': '#FFFFFF',
    '--primary-accent-color': '#B71C1C',
    '--button-text-color': '#FFFFFF',
    '--secondary-accent-color': '#38761d',
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
        try {
            const response = await fetch('/site-config.json');
            if (!response.ok) {
                throw new Error(`Failed to fetch site-config.json with status ${response.status}`);
            }
            const config = await response.json();
            trackingCode.value = config.trackingCode || '';
            apiBaseUrl.value = config.apiBaseUrl || apiBaseUrl.value;
            contactInfo.value = config.contactInfo || {};
            beian.value = config.beian || {};
            heroSection.value = config.heroSection || {};
            footer.value = config.footer || {};
            aboutPageHtml.value = config.aboutPageHtml || ''; // <--- 赋值

        } catch (error) {
            console.error('无法加载基础站点配置 (site-config.json):', error);
            initializeTheme();
            return;
        }

        try {
            const publicConfig = await apiClient.get('/config/public');
            isRegistrationEnabled.value = publicConfig.enable_registration;
        } catch (error) {
            console.error("无法从后端加载公共配置:", error);
        }

        initializeTheme();
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