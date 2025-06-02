// src/stores/settings.js
import { defineStore } from 'pinia';
import { ref, watch, onMounted } from 'vue'; // 导入 onMounted

const DEFAULT_API_BASE_URL = 'http://localhost:8000';

// 定义两套颜色主题的变量值
const lightThemeColors = { // "安迪和莉莉的棺材" 风格的日间模式
  '--main-bg-color': '#e8e3d9',        // 米白色/亚麻色背景 (取代之前的 #f0f0f0)
  '--secondary-bg-color': '#d1ccc0',   // 稍深一点的米色/浅褐色背景 (取代之前的 #ffffff)
  '--main-text-color': '#4a3f35',      // 深棕色/暗褐色文字 (取代之前的 #2c3e50)
  '--border-color': '#a8a092',         // 较深的米色/灰褐色边框 (取代之前的 #dcdcdc)
  '--link-color': '#6e5f50',           // 暗哑的棕色链接 (取代之前的 #3498db)
  '--link-hover-color': '#8a7a6a',     // 链接悬停时稍亮一些 (取代之前的 #2980b9)
  '--primary-accent-color': '#8c4343', // 更加不饱和/暗沉的红色作为强调色 (取代之前的 #e74c3c)
  // 您可以根据需要为日间模式定义或调整更多变量
  // 例如，按钮的特定背景色、文字颜色等，如果它们与暗色模式下有显著不同的话
};

const darkThemeColors = { // 我们之前为“安迪和莉莉的棺材”风格定义的暗色主题
  '--main-bg-color': '#1a1a1a',
  '--secondary-bg-color': '#2b2b2b',
  '--main-text-color': '#e0e0e0',
  '--border-color': '#444',
  '--link-color': '#c0c0c0',
  '--link-hover-color': '#ffffff',
  '--primary-accent-color': '#7f0000', // 暗红色
};

// ... (useSettingsStore 的其余部分保持不变) ...
export const useSettingsStore = defineStore('settings', () => {
    // ... (API URL State 和 Theme State 不变) ...
    const apiBaseUrl = ref(localStorage.getItem('api_base_url') || DEFAULT_API_BASE_URL);
    const availableThemes = ['light', 'dark', 'system'];
    const theme = ref(localStorage.getItem('theme_preference') || 'system');
    const currentAppliedTheme = ref('light'); // 初始值会被 initializeTheme 覆盖

    // ... (API URL Actions 不变) ...
    function setApiBaseUrl(newUrl) {
        if (newUrl && typeof newUrl === 'string' && newUrl.trim() !== '') {
            const sanitizedUrl = newUrl.trim().replace(/\/+$/, '');
            apiBaseUrl.value = sanitizedUrl;
        } else {
            apiBaseUrl.value = DEFAULT_API_BASE_URL;
        }
    }
    watch(apiBaseUrl, (newUrlValue) => {
        localStorage.setItem('api_base_url', newUrlValue);
    });

    // --- Theme Actions (这里的逻辑保持不变，它会根据传入的主题名称选择对应的颜色对象) ---
    function applyThemeVariables(themeToApply) {
        const root = document.documentElement;
        // 根据 themeToApply 选择正确的颜色集
        const colors = themeToApply === 'dark' ? darkThemeColors : lightThemeColors;
        for (const [variable, value] of Object.entries(colors)) {
            root.style.setProperty(variable, value);
        }
        currentAppliedTheme.value = themeToApply;
        root.className = `theme-${themeToApply}`; // 确保类名也正确设置
        console.log(`Theme applied: ${themeToApply}`);
    }

    function determineEffectiveTheme() {
        if (theme.value === 'system') {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                return 'dark';
            }
            return 'light';
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
        const effectiveTheme = determineEffectiveTheme();
        applyThemeVariables(effectiveTheme);
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
                if (theme.value === 'system') {
                    applyThemeVariables(event.matches ? 'dark' : 'light');
                }
            });
        }
    }

    return {
        apiBaseUrl,
        setApiBaseUrl,
        DEFAULT_API_BASE_URL,
        theme,
        currentAppliedTheme,
        availableThemes,
        setTheme,
        initializeTheme,
    };
});