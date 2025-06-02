<template>
  <div class="gallery-view-component">
    <div v-if="isLoading" class="loading">正在加载画廊项目...</div>

    <div v-if="error" class="error-message">
      加载画廊项目失败: {{ error.message }}
    </div>

    <div v-if="!isLoading && !error && galleryItems.length > 0">
      <div class="gallery-grid">
        <div v-for="item in galleryItems" :key="item.id" class="gallery-item" @click="showFullImage(item)">
          <img :src="item.thumbnail_url ? `${settingsStore.apiBaseUrl}${item.thumbnail_url}` : 'https://via.placeholder.com/200x200.png?text=No+Thumb'" :alt="item.title" />
          <h3>{{ item.title }}</h3>
          <p v-if="item.uploader">上传者: {{ item.uploader.username }}</p>
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
        <button @click="closeLightbox" class="close-button">×</button>
        <img :src="`${settingsStore.apiBaseUrl}${selectedItemForLightbox.image_url}`" :alt="selectedItemForLightbox.title" />
        <h2>{{ selectedItemForLightbox.title }}</h2>
        <p v-if="selectedItemForLightbox.description">{{ selectedItemForLightbox.description }}</p>
        <p v-if="selectedItemForLightbox.uploader">上传者: {{ selectedItemForLightbox.uploader.username }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useSettingsStore } from '@/stores/settings';

const settingsStore = useSettingsStore(); // 2. 获取 settingsStore 实例

const galleryItems = ref([]);
const currentPage = ref(1);
const pageSize = ref(10); // 您可以根据需要调整默认值
const totalItems = ref(0);
const totalPages = ref(0);
const isLoading = ref(true);
const error = ref(null);
const selectedItemForLightbox = ref(null);

async function fetchGalleryItems(page = 1, limit = pageSize.value) {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await fetch(`${settingsStore.apiBaseUrl}/gallery/items?page=${page}&page_size=${limit}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    const data = await response.json();

    galleryItems.value = data.items;
    totalItems.value = data.total_items;
    totalPages.value = data.total_pages;
    currentPage.value = data.page;
  } catch (err) {
    console.error("获取画廊项目失败:", err);
    error.value = err; // 将错误对象直接赋给 error ref
    galleryItems.value = [];
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
/* 使用在 main.css 中定义的颜色变量 */
.gallery-view-component {
  padding: 10px 0; /* 调整组件本身的 padding */
}

.loading, .no-items { /* error-message 样式已在 main.css 定义 */
  text-align: center;
  padding: 40px 20px; /* 增加内边距 */
  font-size: 1.2em;
  color: var(--main-text-color);
  background-color: var(--secondary-bg-color); /* 给一个背景，使其在暗色主题下更明显 */
  border: 1px dashed var(--border-color); /* 使用虚线边框增加风格 */
  margin: 20px;
}
.error-message { /* 如果需要在局部覆盖全局样式 */
  margin: 20px;
  border-radius: 0;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); /* 可以根据需要调整minmax */
  gap: 25px; /* 调整间距 */
  margin-bottom: 30px;
}

.gallery-item {
  background-color: var(--secondary-bg-color);
  border: 1px solid var(--border-color);
  padding: 15px; /* 调整内边距 */
  border-radius: 0; /* 去掉圆角 */
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s ease-in-out, box-shadow 0.3s ease-in-out, border-color 0.3s ease-in-out;
  /* 设计风格参考：可以考虑添加 scanlines 效果或轻微的噪点背景 */
}

.gallery-item:hover {
  transform: translateY(-3px) scale(1.02); /* 轻微放大和上移 */
  border-color: var(--primary-accent-color); /* 悬停时用强调色边框 */
  box-shadow: 0 0 15px rgba(127, 0, 0, 0.4); /* 配合强调色的阴影 */
}

.gallery-item img {
  max-width: 100%;
  height: 200px; /* 固定高度 */
  object-fit: cover;
  margin-bottom: 15px; /* 图片和标题间距 */
  border: 1px solid var(--border-color); /* 图片也加一个边框 */
  filter: grayscale(30%) sepia(20%); /* 可选：给图片一点复古/暗色调滤镜 */
}

.gallery-item h3 {
  font-size: 1.05em; /* 调整字体大小 */
  margin: 0 0 8px 0; /* 调整间距 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--main-text-color);
  font-weight: normal;
  /* font-family: var(--font-pixel, var(--font-main)); */
}

.gallery-item p {
  font-size: 0.8em;
  color: #a0a0a0; /* 上传者信息颜色调暗一些 */
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 40px;
  padding: 10px;
}
/* 分页按钮样式继承自 main.css 的 button 基础样式，这里可以微调 */
.pagination button {
  /* background-color: var(--secondary-bg-color); */
  /* border-color: var(--border-color); */
  /* color: var(--main-text-color); */
  margin: 0 10px; /* 增加按钮间距 */
  font-size: 0.9em;
}
/* .pagination button:hover:not(:disabled) {
  background-color: var(--border-color);
  border-color: var(--primary-accent-color);
} */
.pagination button:disabled {
  /* opacity: 0.5; */ /* main.css 中已定义 */
  /* cursor: not-allowed; */
}
.pagination span {
  margin: 0 15px; /* 增加文字间距 */
  font-size: 0.95em;
  color: var(--main-text-color);
}

/* 灯箱样式 */
.lightbox-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.92); /* 更暗的背景 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
  box-sizing: border-box;
}

.lightbox-content {
  background-color: var(--secondary-bg-color); /* 灯箱内容区域背景 */
  padding: 25px 30px; /* 调整内边距 */
  border-radius: 0; /* 去掉圆角 */
  border: 2px solid var(--border-color); /* 灯箱边框 */
  max-width: 90%;
  max-height: 90vh;
  overflow: auto;
  position: relative;
  text-align: center;
  box-shadow: 0 0 25px rgba(0,0,0,0.7); /* 更强的阴影 */
  color: var(--main-text-color);
}

.lightbox-content img {
  max-width: 100%;
  max-height: calc(90vh - 180px); /* 为标题、描述、关闭按钮留出更多空间 */
  display: block;
  margin: 0 auto 20px auto; /* 增加图片下间距 */
  border: 1px solid var(--border-color);
  /* filter: brightness(0.9); 可选：让图片稍微暗一点以融入暗色主题 */
}

.lightbox-content h2 {
  margin-bottom: 15px;
  font-size: 1.6em; /* 调整字体大小 */
  color: var(--main-text-color);
  font-weight: normal;
  /* font-family: var(--font-pixel, var(--font-main)); */
}

.lightbox-content p {
  margin-bottom: 10px;
  color: #b0b0b0; /* 描述文字颜色 */
  font-size: 0.95em;
  line-height: 1.7;
}

.close-button { /* 关闭按钮样式调整 */
  position: absolute;
  top: 10px; /* 调整位置 */
  right: 10px;
  background: var(--primary-accent-color); /* 使用强调色 */
  color: var(--main-text-color);
  border: 1px solid darken(var(--primary-accent-color), 10%); /* 需要计算或手动指定更暗色 */
  border-color: #600000; /* 手动指定 */
  border-radius: 0; /* 去掉圆角 */
  width: 36px; /* 增大点击区域 */
  height: 36px;
  font-size: 22px; /* 调整字体大小 */
  font-weight: bold;
  cursor: pointer;
  line-height: 34px; /* 调整行高使 "×" 居中 */
  text-align: center;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.close-button:hover {
  background-color: #600000; /* 手动指定更深的红色 */
  transform: scale(1.1);
}
</style>