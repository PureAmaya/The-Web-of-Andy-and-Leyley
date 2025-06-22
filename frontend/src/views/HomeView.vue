<template>
  <div class="home-container">
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">{{ animatedTitle }}<span class="cursor" v-if="isTyping">_</span></h1>
        <p class="hero-subtitle">{{ animatedSubtitle }}</p>
      </div>
    </section>


    <section class="content-section gallery-preview">
      <h2 class="section-title">最新作品</h2>
      <!-- 使用 v-if 控制加载状态的显示 -->
      <div v-if="isLoading" class="loading-message">加载中...</div>
      <div v-if="galleryError" class="error-message">{{ galleryError }}</div>

      <div v-if="!isLoading && galleryItems.length > 0" class="preview-grid">
        <div v-for="item in galleryItems" :key="item.id" class="preview-item">
          <img :src="getFullImageUrl(item.thumbnail_url || item.image_url)" :alt="item.title" class="preview-image" />
          <div class="preview-overlay">
            <p>{{ item.title }}</p>
          </div>
        </div>
      </div>
      <div class="section-link">
        <RouterLink to="/gallery" class="cta-button">查看完整画廊</RouterLink>
      </div>
    </section>

    <section class="content-section team-section">
      <h2 class="section-title">核心成员</h2>
      <div class="team-grid">
        <div v-for="member in teamMembers" :key="member.id" class="team-member-card" @click="openMemberModal(member)">
          <img :src="getFullImageUrl(member.avatar_url, member.name)" :alt="member.name" class="team-avatar" />
          <h3 class="team-member-name">{{ member.name }}</h3>
          <p class="team-member-role">{{ member.role }}</p>
        </div>
      </div>
    </section>

    <section class="content-section contact-section">
      <h2 v-if="settingsStore.contactInfo.title" class="section-title">
        {{ settingsStore.contactInfo.title }}
      </h2>
      <div class="contact-info">
        <p v-if="settingsStore.contactInfo.description">
          {{ settingsStore.contactInfo.description }}
        </p>
        <p v-for="(item, index) in settingsStore.contactInfo.items" :key="index">
          <strong>{{ item.label }}:</strong>
          <a v-if="item.url" :href="item.url" target="_blank" rel="noopener noreferrer">
            {{ item.value }}
          </a>
          <span v-else>{{ item.value }}</span>
        </p>
      </div>
    </section>

    <div v-if="isModalOpen" class="modal-backdrop" @click="closeMemberModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close-button" @click="closeMemberModal">&times;</button>
        <div v-if="selectedMember">
          <img :src="getFullImageUrl(selectedMember.avatar_url, selectedMember.name)" :alt="selectedMember.name" class="modal-avatar" />
          <h2>{{ selectedMember.name }}</h2>
          <h4>{{ selectedMember.role }}</h4>
          <p class="modal-bio">{{ selectedMember.bio }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { RouterLink } from 'vue-router';
import { useSettingsStore } from '@/stores/settings';
import apiClient from '@/api';

const settingsStore = useSettingsStore();

// --- 状态定义 ---
const teamMembers = ref([]);
const galleryItems = ref([]);
const isLoading = ref(true);
const galleryError = ref(null);
const selectedMember = ref(null);
const isModalOpen = ref(false);

const animatedTitle = ref('');
const animatedSubtitle = ref('');
const isTyping = ref(false);
let animationStarted = false; // 动画执行锁

// --- 动画函数 ---
function typeWriter(text, elementRef, speed) {
  return new Promise((resolve) => {
    let i = 0;
    elementRef.value = '';

    function typing() {
      if (i < text.length) {
        elementRef.value += text.charAt(i);
        i++;
        setTimeout(typing, speed);
      } else {
        resolve();
      }
    }
    typing();
  });
}

// --- 【核心修正】使用 watch 响应式地启动动画 ---
watch(
  () => settingsStore.heroSection,
  (newConfig) => {
    // 检查：1. 配置对象和标题是否存在  2. 动画是否尚未开始
    if (newConfig && newConfig.title && !animationStarted) {
      // 立刻上锁，防止重复执行
      animationStarted = true;
      isTyping.value = true;

      // 使用 Promise 链确保动画按顺序执行
      typeWriter(newConfig.title, animatedTitle, 150)
        .then(() => {
          if (newConfig.subtitle) {
            return typeWriter(newConfig.subtitle, animatedSubtitle, 50);
          }
        })
        .finally(() => {
          // 所有动画结束后隐藏光标
          isTyping.value = false;
        });
    }
  },
  { deep: true } // deep: true 确保能监听到对象内部属性的变化
);

// --- onMounted 只负责获取本组件需要的数据 ---
onMounted(async () => {
  const fetchGallery = async () => {
    try {
      const data = await apiClient.get('/gallery/items?page=1&page_size=4');
      galleryItems.value = data.items;
    } catch (err) {
      console.error("获取画廊预览失败:", err);
      galleryError.value = "无法加载最新作品。";
    } finally {
      isLoading.value = false;
    }
  };

  const fetchMembers = async () => {
    try {
      teamMembers.value = await apiClient.get('/members');
    } catch (err) {
      console.error('获取成员信息失败:', err);
    }
  };

  await Promise.all([
    fetchGallery(),
    fetchMembers()
  ]);
});

// --- 辅助函数 ---
const getFullImageUrl = (relativeUrl, mcName = null) => {
  if (relativeUrl) {
    if (relativeUrl.startsWith('http')) return relativeUrl;
    return `${settingsStore.apiBaseUrl}${relativeUrl}`;
  }
  if (mcName) {
    return `${settingsStore.apiBaseUrl}/avatars/mc/${mcName}`;
  }
  return 'https://via.placeholder.com/100.png?text=No+Avatar';
};

const openMemberModal = (member) => {
  selectedMember.value = member;
  isModalOpen.value = true;
};

const closeMemberModal = () => {
  isModalOpen.value = false;
  selectedMember.value = null;
};
</script>


<style scoped>
.home-container {
  width: 100%;
}
.content-section {
  padding: 4rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}
.section-title {
  font-size: 2.5rem;
  color: var(--main-text-color);
  margin-bottom: 2rem;
  font-weight: 300;
  font-family: var(--font-special), cursive;
}
.hero-section {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
  background: var(--secondary-bg-color);
  padding: 2rem;
}
.hero-title {
  font-size: clamp(2.5rem, 8vw, 4rem);
  font-weight: bold;
  margin: 0;
  color: var(--main-text-color);
  font-family: var(--font-special), cursive;
  min-height: 1.2em;
}
.hero-subtitle {
  font-size: clamp(1.2rem, 4vw, 1.5rem);
  margin-top: 1rem;
  color: var(--link-color);
  min-height: 1.2em;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
.cursor {
  animation: blink 1s step-end infinite;
  font-weight: bold;
}
.gallery-preview .preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}
.preview-item {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-color);
  cursor: pointer;
  aspect-ratio: 1 / 1;
}
.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.preview-item:hover .preview-image {
  transform: scale(1.05);
}
.preview-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7) 0%, rgba(0, 0, 0, 0.7) 50%, transparent 100%);
  color: white;
  padding: 1rem;
  transform: translateY(100%);
  transition: transform 0.3s ease;
  font-size: 0.9em;
  text-align: center;
}
.preview-item:hover .preview-overlay {
  transform: translateY(0);
}
.section-link {
  margin-top: 3rem;
}
.cta-button {
  padding: 12px 30px;
  border: 2px solid var(--border-color);
  background-color: transparent;
  color: var(--main-text-color);
  text-decoration: none;
  font-weight: bold;
  transition: all 0.2s;
}
.cta-button:hover {
  background-color: var(--primary-accent-color);
  border-color: var(--primary-accent-color);
  color: #fff;
}
.team-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
}
.team-member-card {
    background: transparent;
    border: 2px solid var(--border-color);
    padding: 1.5rem;
    cursor: pointer;
    transition: background-color 0.2s, border-color 0.2s, box-shadow 0.2s;
    box-shadow: 5px 5px 0 0 var(--border-color);
}
.team-member-card:hover {
    background-color: var(--secondary-bg-color);
    border-color: var(--primary-accent-color);
    box-shadow: 5px 5px 0 0 var(--primary-accent-color);
}
.team-avatar {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    margin-bottom: 1rem;
    border: 2px solid var(--primary-accent-color);
}
.team-member-name {
    margin: 0.5rem 0;
    font-size: 1.2rem;
    color: var(--main-text-color);
}
.team-member-role {
    font-size: 0.9rem;
    color: var(--link-color);
}
.contact-info {
    margin-top: 1.5rem;
    font-size: 1.1rem;
    line-height: 1.8;
    color: var(--main-text-color);
}

.contact-info strong {
    color: var(--link-color);
    font-weight: 700;
    margin-right: 8px; /* 修复：为标签和链接之间添加间距 */
}


.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
  box-sizing: border-box;
}
.modal-content {
  background-color: var(--main-bg-color);
  padding: 2rem 3rem;
  border: 1px solid var(--border-color);
  width: 90%;
  max-width: 500px;
  position: relative;
  text-align: center;
}
.modal-close-button {
  position: absolute;
  top: 10px;
  right: 15px;
  background: none;
  border: none;
  font-size: 2rem;
  color: var(--link-color);
  cursor: pointer;
}
.modal-avatar {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    margin-bottom: 1rem;
}
.modal-bio {
    margin: 1.5rem 0;
    text-align: left;
    line-height: 1.7;
    color: var(--main-text-color);
}
.loading-message, .error-message {
    margin-top: 2rem;
    font-size: 1.1rem;
}
.error-message {
    color: var(--primary-accent-color);
}
</style>
