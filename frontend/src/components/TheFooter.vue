<template>
  <footer class="site-footer">
    <div class="footer-content">
      <div v-if="links.length > 0" class="friend-links-section">
        <h4 class="footer-title">友情链接</h4>
        <ul class="links-list">
          <li v-for="link in links" :key="link.id">
            <a :href="link.url" target="_blank" rel="noopener noreferrer">
              <img v-if="link.logo_url" :src="link.logo_url" :alt="`${link.name} Logo`" class="link-logo" @error="onLogoError">
              <span>{{ link.name }}</span>
            </a>
          </li>
        </ul>
      </div>

      <div class="copyright-section">
        <!-- 使用 computed property 来动态生成版权信息 -->
        <p>{{ copyrightText }}</p>

        <p class="beian-info" v-if="settingsStore.beian.icp">
          <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">{{ settingsStore.beian.icp }}</a>
          <template v-if="settingsStore.beian.gongan && settingsStore.beian.gongan.text">
            <span class="separator">|</span>
            <a :href="settingsStore.beian.gongan.link" target="_blank" rel="noopener">
              {{ settingsStore.beian.gongan.text }}
            </a>
          </template>
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'; // 引入 computed
import { useSettingsStore } from '@/stores/settings';

const settingsStore = useSettingsStore();
const links = ref([]);

// --- 新增：使用计算属性动态生成版权字符串 ---
const copyrightText = computed(() => {
  const owner = settingsStore.footer.copyrightOwner || 'Your Name';
  const startYear = settingsStore.footer.startYear;
  const currentYear = new Date().getFullYear();

  if (!startYear || startYear >= currentYear) {
    return `Copyright © ${currentYear} ${owner}. All Rights Reserved.`;
  }
  return `Copyright © ${startYear}-${currentYear} ${owner}. All Rights Reserved.`;
});

async function fetchFriendLinks() {
  try {
    const response = await fetch(`${settingsStore.apiBaseUrl}/friend-links`);
    if (response.ok) {
      links.value = await response.json();
    }
  } catch (error) {
    console.error("获取友情链接失败:", error);
  }
}

function onLogoError(event) {
  event.target.style.display = 'none';
}

onMounted(() => {
  fetchFriendLinks();
});
</script>


<style scoped>
.site-footer {
  background-color: var(--secondary-bg-color); /* 使用主题变量 */
  color: var(--link-color); /* 使用主题变量 */
  padding: 30px 0; /* 移除左右padding */
  border-top: 2px solid var(--border-color);
  margin-top: auto;
}

.footer-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 2rem; /* 在内容区内部添加padding */
  box-sizing: border-box;
}


.footer-title {
  color: #e0e0e0;
  font-size: 1.1em;
  font-weight: bold;
  margin-bottom: 15px;
  border-bottom: 1px solid #444;
  padding-bottom: 10px;
}

.friend-links-section {
  margin-bottom: 30px;
}

.links-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.links-list li a {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--link-color);
  text-decoration: none;
  transition: color 0.2s ease;
  padding: 5px;
}

.links-list li a:hover {
  color: var(--link-hover-color);
}

.link-logo {
  height: 20px; /* 控制Logo高度 */
  max-width: 80px;
  vertical-align: middle;
}

.copyright-section {
  text-align: center;
  font-size: 0.85em;
  color: #888;
  padding-top: 20px;
}

.copyright-section p {
  margin: 5px 0;
}

.beian-info a {
  color: #888;
  text-decoration: none;
}

.beian-info a:hover {
  text-decoration: underline;
  color: #aaa;
}

.beian-info .separator {
  margin: 0 10px;
}
</style>