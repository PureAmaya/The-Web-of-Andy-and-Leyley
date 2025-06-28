<template>
  <div v-if="selectedItem" class="lightbox-overlay" @click.self="close">
    <div class="lightbox-content">
      <img
        v-if="selectedItem.item_type === 'image'"
        :src="`${apiBaseUrl}${selectedItem.image_url}`"
        :alt="selectedItem.title"
        class="lightbox-media"
      />
      <video
        v-else-if="selectedItem.item_type === 'video'"
        :src="`${apiBaseUrl}${selectedItem.image_url}`"
        class="lightbox-media"
        controls
        autoplay
        loop
      >
        您的浏览器不支持 Video 标签。
      </video>

      <div class="lightbox-details">
        <h2>{{ selectedItem.title }}</h2>
        <p v-if="selectedItem.description" class="lightbox-description">
          {{ selectedItem.description }}
        </p>
        <div class="lightbox-meta">
          <p v-if="selectedItem.builder">
            <strong>创作者:</strong> {{ selectedItem.builder.name }}
          </p>
          <p v-if="selectedItem.uploader">
            <strong>上传者:</strong> {{ selectedItem.uploader.username }}
          </p>
        </div>
        <a
          :href="`${apiBaseUrl}${selectedItem.image_url}`"
          :download="getDownloadFilename(selectedItem)"
          class="download-button"
          target="_blank"
          rel="noopener noreferrer"
        >
          下载原文件
        </a>
      </div>
      <button @click="close" class="close-button" aria-label="关闭">&times;</button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

// 定义组件接收的属性
const props = defineProps({
  selectedItem: {
    type: Object,
    default: null
  },
  apiBaseUrl: {
    type: String,
    required: true
  }
});

// 定义组件可以发出的事件
const emit = defineEmits(['close']);

// 关闭灯箱的函数，它会发出一个 "close" 事件
function close() {
  emit('close');
}

// 用于生成下载文件名的辅助函数
const getDownloadFilename = (item) => {
  if (!item || !item.image_url) return 'download';
  const extension = item.image_url.split('.').pop();
  return `${item.title}.${extension}`;
};
</script>

<style scoped>
/* 这里是所有从 GalleryView 和 HomeView 移动过来的灯箱样式 */
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

.lightbox-media {
  flex-shrink: 1;
  object-fit: contain;
  min-width: 0;
  min-height: 0;
  background-color: #000;
  max-height: 90vh;
}
@media (min-width: 1024px) {
  .lightbox-media { border-right: 2px solid var(--border-color); }
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

.download-button {
  display: block;
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
</style>