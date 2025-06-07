<template>
  <div class="home-container">
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">{{ animatedTitle }}<span class="cursor">_</span></h1>
        <p class="hero-subtitle">{{ animatedSubtitle }}</p>
      </div>
    </section>

    <section class="content-section gallery-preview">
      <h2 class="section-title">最新作品</h2>
      <div class="preview-grid">
        <div v-for="item in galleryItems" :key="item.id" class="preview-item">
          <img :src="getFullImageUrl(item.thumbnail_url || item.image_url)" :alt="item.title" class="preview-image" />
          <div class="preview-overlay">
            <p>{{ item.title }}</p>
          </div>
        </div>
      </div>
      <div v-if="isLoading" class="loading-message">正在加载作品...</div>
      <div v-if="galleryError" class="error-message">{{ galleryError }}</div>
      <div class="section-link">
        <RouterLink to="/gallery" class="cta-button">查看完整画廊</RouterLink>
      </div>
    </section>

    <section class="content-section team-section">
      <h2 class="section-title">核心成员</h2>
      <div class="team-grid">
        <div v-for="member in teamMembers" :key="member.id" class="team-member-card" @click="openMemberModal(member)">
          <img :src="getFullImageUrl(member.avatar_url)" :alt="member.name" class="team-avatar" />
          <h3 class="team-member-name">{{ member.name }}</h3>
          <p class="team-member-role">{{ member.role }}</p>
        </div>
      </div>
    </section>

    <section class="content-section contact-section">
      <h2 class="section-title">联系我们</h2>
      <div class="contact-info">
        <p>如果您有任何问题或合作意向，请通过以下方式联系我们：</p>
        <p><strong>邮箱:</strong> {{ contactInfo.email }}</p>
        <p><strong>Discord:</strong> {{ contactInfo.discord }}</p>
      </div>
    </section>

    <section class="content-section footer-info-section" v-html="footerHtml"></section>

    <div v-if="isModalOpen" class="modal-backdrop" @click="closeMemberModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close-button" @click="closeMemberModal">&times;</button>
        <div v-if="selectedMember">
          <img :src="getFullImageUrl(selectedMember.avatar_url)" :alt="selectedMember.name" class="modal-avatar" />
          <h2>{{ selectedMember.name }}</h2>
          <h4>{{ selectedMember.role }}</h4>
          <p class="modal-bio">{{ selectedMember.bio }}</p>
          <div class="modal-socials">
            </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import { useSettingsStore } from '@/stores/settings';

const settingsStore = useSettingsStore();

// --- 内容数据 ---
const teamMembers = ref([]);
const contactInfo = {
    email: "contact@landaworld.com",
    discord: "L_and_A_Community"
};
const footerHtml = `<div class="legal-info"><p>京ICP备12345678号-1</p></div><div class="site-stats"><p>网站统计代码将会放在这里</p></div>`;

// --- 打字机动画 ---
const fullTitle = "莉莉与安迪的Minecraft";
const fullSubtitle = "一个存放记忆与创造的角落";
const animatedTitle = ref('');
const animatedSubtitle = ref('');

// --- 图库预览数据 ---
const galleryItems = ref([]);
const isLoading = ref(true);
const galleryError = ref(null);

const getFullImageUrl = (relativeUrl) => {
  if (!relativeUrl) return '';
  if (relativeUrl.startsWith('http')) {
    return relativeUrl;
  }
  return `${settingsStore.apiBaseUrl}${relativeUrl}`;
};

onMounted(async () => {
  // 定义获取图库的函数
  const fetchGallery = async () => {
    try {
      const response = await fetch(`${settingsStore.apiBaseUrl}/gallery/items?page=1&page_size=4`);
      if (!response.ok) throw new Error('获取图库作品失败');
      const data = await response.json();
      galleryItems.value = data.items;
    } catch (err) {
      galleryError.value = err.message;
    } finally {
      isLoading.value = false;
    }
  };

  // 定义获取成员信息的函数
  const fetchMembers = async () => {
    try {
      const response = await fetch(`${settingsStore.apiBaseUrl}/members`);
      if (!response.ok) throw new Error('获取成员列表失败');
      teamMembers.value = await response.json();
    } catch (err) {
      console.error('获取成员信息失败:', err);
    }
  };

  // 启动打字机动画
  let i = 0;
  const typeTitle = () => {
    if (i < fullTitle.length) {
      animatedTitle.value += fullTitle.charAt(i);
      i++;
      setTimeout(typeTitle, 150);
    } else {
      animatedSubtitle.value = fullSubtitle;
    }
  };
  typeTitle();

  // 并行执行API请求
  await Promise.all([fetchGallery(), fetchMembers()]);
});

// --- 弹窗 Modal 控制 ---
const isModalOpen = ref(false);
const selectedMember = ref(null);

function openMemberModal(member) {
  selectedMember.value = member;
  isModalOpen.value = true;
}

function closeMemberModal() {
  isModalOpen.value = false;
  selectedMember.value = null;
}
</script>

<style scoped>
/* 这里的样式与之前提供的一致，为确保完整性，您可以保留您已有的样式 */
/* ... (HomeView.vue 的全部样式) ... */
.home-container {
  width: 100%;
}

/* 通用板块样式 */
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
  font-family: var(--font-special);
}

/* Hero Section */
.hero-section {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60vh;
  text-align: center;
  background: var(--secondary-bg-color);
}
.hero-title {
  font-size: 4rem;
  font-weight: bold;
  margin: 0;
  color: var(--main-text-color);
  font-family: var(--font-special);
  min-height: 1.2em;
}
.hero-subtitle {
  font-size: 1.5rem;
  margin-top: 1rem;
  color: var(--link-color);
  opacity: 0;
  transition: opacity 1s ease-in-out 0.5s;
}
.hero-subtitle:not(:empty) {
    opacity: 1;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
.cursor {
  animation: blink 1s step-end infinite;
  font-weight: bold;
}

/* Gallery Preview */
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
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 1rem;
  transform: translateY(100%);
  transition: transform 0.3s ease;
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


/* Team Section */
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
    transition: background-color 0.2s, border-color 0.2s;
    box-shadow: 5px 5px 0px 0px var(--primary-accent-color);
}
.team-member-card:hover {
    background-color: var(--secondary-bg-color);
    border-color: var(--main-text-color);
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
}
.team-member-role {
    font-size: 0.9rem;
    color: var(--link-color);
}

/* Contact Section */
.contact-info {
    margin-top: 1.5rem;
    font-size: 1.1rem;
    line-height: 1.8;
}

/* Footer Info Section & v-html content */
.footer-info-section {
    background-color: var(--secondary-bg-color);
    color: var(--link-color);
    font-size: 0.9rem;
    padding-bottom: 2rem; /* Add some space at the very bottom */
}
:deep(.footer-info-section .legal-info) {
    margin-top: 1.5rem;
    font-size: 0.8rem;
    color: #888;
}
:deep(.footer-info-section .site-stats) {
    margin-top: 1rem;
}

/* Modal Styles */
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
}
.modal-socials {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin-top: 1.5rem;
}
.modal-socials a {
    color: var(--primary-accent-color);
    text-decoration: none;
    font-weight: bold;
}
.loading-message, .error-message {
    margin-top: 2rem;
    font-size: 1.1rem;
}
.error-message {
    color: var(--primary-accent-color);
}
</style>