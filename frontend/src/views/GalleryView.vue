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
            v-if="item.item_type === 'image'"
            :src="getFullImageUrl(item.thumbnail_url, item.title, settingsStore.apiBaseUrl)"
            :alt="item.title"
            class="gallery-media"
            loading="lazy"
          />
          <video
            v-else-if="item.item_type === 'video'"
            :poster="getFullImageUrl(item.thumbnail_url, item.title, settingsStore.apiBaseUrl)"
            class="gallery-media"
            muted
            preload="metadata"
          >
            <source :src="getFullImageUrl(item.image_url, item.title, settingsStore.apiBaseUrl)" type="video/mp4">
            您的浏览器不支持 Video 标签。
          </video>
          <div v-if="item.item_type === 'video'" class="video-play-icon">▶</div>

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

    <Lightbox
        :selectedItem="selectedItemForLightbox"
        :apiBaseUrl="settingsStore.apiBaseUrl"
        @close="closeLightbox"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/api';
import { useSettingsStore } from '@/stores/settings';
import { getFullImageUrl } from '@/utils/imageUtils';

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



const getDownloadFilename = (item) => {
  if (!item || !item.image_url) return 'download';
  // 从URL中提取文件名，并替换为标题
  const originalFilename = item.image_url.split('/').pop();
  const extension = originalFilename.split('.').pop();
  // 生成一个更友好的文件名，例如 "作品标题.mp4"
  return `${item.title.replace(/[/\\?%*:|"<>]/g, '-')}.${extension}`;
};

onMounted(() => {
  fetchGalleryItems();
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

.gallery-media {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

/* 视频播放按钮图标样式 */
.video-play-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 4rem;
  color: rgba(255, 255, 255, 0.8);
  text-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
  pointer-events: none; /* 确保它不影响点击事件 */
  opacity: 0.8;
  transition: opacity 0.3s;
}

.gallery-item:hover .video-play-icon {
  opacity: 1;
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
.gallery-item:hover .gallery-media {
  transform: scale(1.05); /* 图片/视频放大 */
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



/* 分页组件样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 3rem;
  padding: 1rem;
}
</style>