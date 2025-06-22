<template>
  <div class="gallery-view-component">
    <div v-if="isLoading" class="loading">正在加载画廊项目...</div>

    <div v-if="error" class="error-message">
      加载画廊项目失败: {{ error }}
    </div>

    <div v-if="!isLoading && !error && galleryItems.length > 0">
      <div class="gallery-grid">
        <div
          v-for="item in galleryItems"
          :key="item.id"
          class="gallery-item"
          @click="showFullImage(item)"
          @keydown.enter="showFullImage(item)"
          tabindex="0"
          role="button"
          :aria-label="`查看作品 ${item.title}`"
        >
          <img
            :src="item.thumbnail_url ? `${settingsStore.apiBaseUrl}${item.thumbnail_url}` : 'https://via.placeholder.com/400x300.png?text=Image+Not+Found'"
            :alt="item.title"
            class="gallery-image"
          />
          <div class="item-title-bar">
            <h3 class="item-title">{{ item.title }}</h3>
          </div>
          <div class="item-info-overlay">
            <h3 class="item-title-hover">{{ item.title }}</h3>
            <p v-if="item.builder" class="item-author">
              —— {{ item.builder.name }}
            </p>
          </div>
        </div>
      </div>

      <div class="pagination">
        <button @click="changePage(currentPage - 1)" :disabled="currentPage <= 1">
          上一页
        </button>
        <span>第 {{ currentPage }} 页 / 共 {{ totalPages }} 页 ({{ totalItems }} 项)</span>
        <button @click="changePage(currentPage + 1)" :disabled="currentPage >= totalPages">
          下一页
        </button>
      </div>
    </div>

    <div v-if="!isLoading && !error && galleryItems.length === 0" class="no-items">
      目前还没有画廊项目。
    </div>

    <div v-if="selectedItemForLightbox" class="lightbox-overlay" @click.self="closeLightbox">
      <div class="lightbox-content">
        <img
          :src="`${settingsStore.apiBaseUrl}${selectedItemForLightbox.image_url}`"
          :alt="selectedItemForLightbox.title"
          class="lightbox-image"
        />
        <div class="lightbox-details">
            <h2>{{ selectedItemForLightbox.title }}</h2>
            <p v-if="selectedItemForLightbox.description" class="lightbox-description">
              {{ selectedItemForLightbox.description }}
            </p>
            <div class="lightbox-meta">
              <p v-if="selectedItemForLightbox.builder">
                <strong>创作者:</strong> {{ selectedItemForLightbox.builder.name }}
              </p>
              <p v-if="selectedItemForLightbox.uploader">
                <strong>上传者:</strong> {{ selectedItemForLightbox.uploader.username }}
              </p>
            </div>
            <a
              :href="`${settingsStore.apiBaseUrl}${selectedItemForLightbox.image_url}`"
              :download="`${selectedItemForLightbox.title}.png`"
              class="download-button"
              target="_blank"
              rel="noopener noreferrer"
            >
              下载原图
            </a>
        </div>
        <button @click="closeLightbox" class="close-button" aria-label="关闭">&times;</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/api';
import { useSettingsStore } from '@/stores/settings';

const settingsStore = useSettingsStore();

const galleryItems = ref([]);
const currentPage = ref(1);
const pageSize = ref(12);
const totalItems = ref(0);
const totalPages = ref(0);
const isLoading = ref(true);
const error = ref(null);
const selectedItemForLightbox = ref(null);

async function fetchGalleryItems(page = 1, limit = pageSize.value) {
  isLoading.value = true;
  error.value = null;
  try {
    const data = await apiClient.get('/gallery/items', {
      params: { page, page_size: limit },
    });
    galleryItems.value = data.items;
    totalItems.value = data.total_items;
    totalPages.value = data.total_pages;
    currentPage.value = data.page;
  } catch (err) {
    console.error("获取画廊项目失败:", err);
    error.value = err.response?.data?.detail || err.message || '加载画廊时发生未知错误';
  } finally {
    isLoading.value = false;
  }
}

function changePage(newPage) {
  if (newPage >= 1 && newPage <= totalPages.value && newPage !== currentPage.value) {
    fetchGalleryItems(newPage, pageSize.value);
  }
}

function showFullImage(item) {
  selectedItemForLightbox.value = item;
}

function closeLightbox() {
  selectedItemForLightbox.value = null;
}

onMounted(() => {
  fetchGalleryItems(currentPage.value, pageSize.value);
});
</script>

<style scoped>
/* 画廊网格布局 */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
}

/* 画廊项目卡片 */
.gallery-item {
  position: relative;
  aspect-ratio: 4 / 3;
  background-color: var(--secondary-bg-color);
  overflow: hidden;
  border: 2px solid var(--border-color);
  transition: all 0.3s ease;
  cursor: pointer;
}

/* 为奇数和偶数项应用不同的、轻微的旋转角度 */
.gallery-item:nth-child(odd) {
  transform: rotate(-2deg);
}
.gallery-item:nth-child(even) {
  transform: rotate(2deg);
}
.gallery-item:nth-child(3n) {
  transform: rotate(1deg);
}

/* 鼠标悬浮时，图片回正并放大 */
.gallery-item:hover {
  transform: rotate(0deg) scale(1.1);
  z-index: 10; /* 确保它在最上层显示 */
  border-color: var(--primary-accent-color);
}


.gallery-item:focus {
  outline: 2px solid var(--primary-accent-color);
  outline-offset: 2px;
}

.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

/* --- 新交互的核心样式 --- */
/* 默认只显示标题的底部栏 */
.item-title-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 0.75rem 1rem;
  box-sizing: border-box;
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
  color: #fff;
  transition: opacity 0.3s ease;
}
.item-title {
  font-family: var(--font-main);
  font-weight: 700;
  font-size: 1rem;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
}

/* 悬浮时才完整显示的信息层 */
.item-info-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end; /* 内容从底部开始 */
  padding: 1.5rem;
  box-sizing: border-box;
  color: #fff;
  background: linear-gradient(to top, rgba(0,0,0,0.85), rgba(0,0,0,0.1));
  opacity: 0; /* 默认完全透明 */
  transition: opacity 0.4s ease;
}

/* 鼠标悬浮时的变化 */
.gallery-item:hover .item-info-overlay {
  opacity: 1; /* 浮现 */
}
.gallery-item:hover .item-title-bar {
  opacity: 0; /* 隐藏默认标题栏 */
}
.gallery-item:hover .gallery-image {
  transform: scale(1.05); /* 图片放大 */
}
.item-title-hover {
  font-family: var(--font-special), cursive;
  font-size: 1.5rem;
  margin: 0;
}
.item-author {
  font-size: 1rem;
  margin: 0.5rem 0 0;
  font-style: italic;
}


/* 灯箱 (大图预览) - 样式与之前相同，但包含了新的下载按钮 */
.lightbox-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(31, 29, 27, 0.95);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 1rem;
  box-sizing: border-box;
  animation: fadeIn 0.3s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.lightbox-content {
  display: flex;
  flex-direction: column;
  max-width: 95vw;
  max-height: 95vh;
  position: relative;
  background-color: var(--secondary-bg-color);
  border: 2px solid var(--border-color);
}
@media (min-width: 1024px) {
  .lightbox-content { flex-direction: row; max-width: 90vw; }
}

.lightbox-image {
  flex-shrink: 1;
  object-fit: contain;
  min-width: 0;
  min-height: 0;
  background-color: #000;
}
@media (min-width: 1024px) {
  .lightbox-image { border-right: 2px solid var(--border-color); }
}

.lightbox-details {
  padding: 1.5rem;
  box-sizing: border-box;
  text-align: left;
  overflow-y: auto;
  flex-shrink: 0;
  width: 100%;
  max-height: 40vh;
}
@media (min-width: 1024px) {
  .lightbox-details { width: 350px; max-height: none; }
}

.lightbox-details h2 {
  font-family: var(--font-special), cursive;
  font-size: 1.8rem;
  margin: 0 0 1rem;
  color: var(--main-text-color);
}
.lightbox-description {
  font-size: 1rem;
  line-height: 1.7;
  color: var(--main-text-color);
  opacity: 0.9;
  margin-bottom: 2rem;
}
.lightbox-meta {
  font-size: 0.9rem;
  opacity: 0.7;
  border-top: 1px solid var(--border-color);
  padding-top: 1rem;
  margin-bottom: 2rem;
}

/* 下载按钮样式 */
.download-button {
  display: block; /* 改为块级元素，占满整行 */
  width: 100%;
  padding: 12px 20px;
  box-sizing: border-box;
  background-color: var(--primary-accent-color);
  color: var(--button-text-color);
  text-align: center;
  text-decoration: none;
  font-family: var(--font-main);
  font-weight: 700;
  font-size: 1.1rem;
  border: 2px solid var(--border-color);
  transition: background-color 0.2s;
}
.download-button:hover {
  background-color: #6e3636;
}

.close-button {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 40px;
  height: 40px;
  background: var(--main-bg-color);
  border: 2px solid var(--border-color);
  border-radius: 50%;
  color: var(--main-text-color);
  font-size: 2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: all 0.2s;
}
.close-button:hover {
  transform: rotate(90deg) scale(1.1);
  color: var(--primary-accent-color);
}

/* 分页组件样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 3rem;
  padding: 1rem;
}
</style>