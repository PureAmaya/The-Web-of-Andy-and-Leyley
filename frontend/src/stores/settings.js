import { defineStore } from 'pinia';
import { ref } from 'vue';

// 定义两套颜色主题的变量值
const lightThemeColors = { // 复古/羊皮纸风格
    '--main-bg-color': '#f4f1e9',        // 灰白色/米色背景
    '--secondary-bg-color': '#e8e3d9',   // 稍深的米色
    '--main-text-color': '#3d352e',      // 深褐色文字
    '--border-color': '#c5bbae',         // 灰褐色边框
    '--link-color': '#5a4f45',           // 暗哑的棕色链接
    '--link-hover-color': '#8c4343',     // 链接悬停时使用强调色
    '--primary-accent-color': '#8c4343', // 不饱和的暗红色作为强调色
    '--button-text-color': '#f4f1e9',    // 按钮文字用浅色
};

const darkThemeColors = {
    '--main-bg-color': '#121212',          // 非常深的木炭色背景
    '--secondary-bg-color': '#1E1E1E',   // 稍亮的深灰色
    '--main-text-color': '#E0E0E0',       // 柔和的白色文字，避免刺眼
    '--border-color': '#333333',         // 更清晰的边框颜色
    '--link-color': '#BBBBBB',           // 链接颜色，比正文亮
    '--link-hover-color': '#FFFFFF',     // 链接悬停 - 纯白
    '--primary-accent-color': '#B71C1C', // 保持一个深邃的红色作为强调色 (例如，Material Design的深红色)
    '--button-text-color': '#FFFFFF',
};


export const useSettingsStore = defineStore('settings', () => {
    // --- State ---
    // 使用 import.meta.env 读取环境变量，并提供一个备用值
    const apiBaseUrl = ref(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000');

    const contactInfo = ref({}); // 联系信息
    const beian = ref({}); // 备案信息

    const availableThemes = ['light', 'dark', 'system'];
    const theme = ref(localStorage.getItem('theme_preference') || 'system');
    const currentAppliedTheme = ref('light');

    // --- Actions ---

    function applyThemeVariables(themeToApply) {
        const root = document.documentElement;
        // 这里的逻辑会自动使用我们上面定义的新颜色对象
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

    // 初始化函数，用于应用启动时加载配置
    async function initialize() {
        try {
            const response = await fetch('/site-config.json'); // 从public目录加载配置文件
            if (!response.ok) throw new Error("Config not found");
            const config = await response.json();

            // 注意这里的逻辑：环境变量提供了初始值，但 site-config.json 中的值可以覆盖它
            // 这提供了双重灵活性
            apiBaseUrl.value = config.apiBaseUrl || apiBaseUrl.value;
            contactInfo.value = config.contactInfo || {};
            beian.value = config.beian || {};

        } catch (error) {
            console.error('无法加载站点配置 (site-config.json):', error);
            console.info('将使用默认配置。');
        }

        // 加载完配置后，初始化主题
        initializeTheme();
    }

    return {
        apiBaseUrl,
        contactInfo,
        beian,
        theme,
        currentAppliedTheme,
        availableThemes,
        initialize, // 导出初始化函数
        setTheme,
    };
});