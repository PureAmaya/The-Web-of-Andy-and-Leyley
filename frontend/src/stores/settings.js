import { defineStore } from 'pinia';
import { ref } from 'vue';
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
    const apiBaseUrl = ref(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000');
    const contactInfo = ref({});
    const beian = ref({});
    const availableThemes = ['light', 'dark', 'system'];
    const theme = ref(localStorage.getItem('theme_preference') || 'system');
    const currentAppliedTheme = ref('light');
    const isRegistrationEnabled = ref(true);
    const heroSection = ref({});
    const footer = ref({});

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
        // 步骤 1: 首先，专门加载和处理 site-config.json
        try {
            // 注意：这里使用原生 fetch，因为它不依赖于 apiClient 的 baseURL
            const response = await fetch('/site-config.json');
            if (!response.ok) {
                throw new Error(`Failed to fetch site-config.json with status ${response.status}`);
            }
            const config = await response.json();

            // 步骤 2: 立刻更新 apiBaseUrl
            // 确保后续所有 apiClient 请求都使用正确的地址
            apiBaseUrl.value = config.apiBaseUrl || apiBaseUrl.value;

            // 更新其他非API依赖的配置
            contactInfo.value = config.contactInfo || {};
            beian.value = config.beian || {};
            heroSection.value = config.heroSection || {
                title: '安迪与莉莉的Minecraft',
                subtitle: '一个存放记忆与创造的角落'
            };
            footer.value = config.footer || {};

        } catch (error) {
            console.error('无法加载基础站点配置 (site-config.json):', error);
            console.info('将使用默认配置，部分功能可能无法使用。');
            // 加载基础配置失败，直接结束初始化，并初始化主题
            initializeTheme();
            return; // 提前返回，不再执行后续API调用
        }

        // 步骤 3: 在 apiBaseUrl 确保正确后，再进行依赖API的配置加载
        try {
            const publicConfig = await apiClient.get('/config/public');
            isRegistrationEnabled.value = publicConfig.enable_registration;
        } catch(error) {
            console.error("无法从后端加载公共配置:", error);
            // 这里可以设置一个默认值或显示错误信息，但不会影响 apiBaseUrl
        }

        // 步骤 4: 最后初始化主题
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
        initialize,
        setTheme,
    };
});