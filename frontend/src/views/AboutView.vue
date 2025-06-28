<template>
  <div class="about-view">
    <div v-if="settingsStore.aboutPageHtml" v-html="settingsStore.aboutPageHtml"></div>
    <div v-else class="no-content-placeholder">
      <h1>关于我们</h1>
      <p>管理员尚未定义此页面的内容。</p>
      <p>请登录管理后台，在“站点配置”中添加 `aboutPageHtml` 字段来设置此页面的内容。</p>
    </div>
  </div>
</template>

<script setup>
import { useSettingsStore } from '@/stores/settings';

const settingsStore = useSettingsStore();
</script>

<style scoped>
.about-view {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: var(--secondary-bg-color);
  border: 1px solid var(--border-color);
  line-height: 1.7;
}

/* 这是一个重要的作用域样式，确保v-html渲染出来的内容有基础样式 */
.about-view :deep(h1),
.about-view :deep(h2),
.about-view :deep(h3) {
  color: var(--main-text-color);
  margin-bottom: 1rem;
  font-weight: bold;
}

.about-view :deep(p) {
  margin-bottom: 1.5rem;
}

.about-view :deep(a) {
  color: var(--primary-accent-color);
  text-decoration: underline;
}

.about-view :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 1rem 0;
}

.no-content-placeholder {
  text-align: center;
  color: var(--link-color);
  padding: 3rem;
  border: 2px dashed var(--border-color);
}
</style>