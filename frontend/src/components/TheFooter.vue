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
        <p>Copyright © {{ new Date().getFullYear() }} {{ settingsStore.siteName }}. All Rights Reserved.</p>
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
import { ref, onMounted } from 'vue';
import { useSettingsStore } from '@/stores/settings';

const settingsStore = useSettingsStore();
const links = ref([]);

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
  // 当Logo图片加载失败时，隐藏它以避免显示一个损坏的图片图标
  event.target.style.display = 'none';
}

onMounted(() => {
  fetchFriendLinks();
});
</script>

<style scoped>
.site-footer {
  background-color: #1a1a1a; /* 比主背景色更深 */
  color: var(--secondary-text-color);
  padding: 30px 40px;
  border-top: 2px solid var(--border-color);
  margin-top: auto; /* 关键：使其在内容不足时也能推到底部 */
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
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
  border-top: 1px solid #333;
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