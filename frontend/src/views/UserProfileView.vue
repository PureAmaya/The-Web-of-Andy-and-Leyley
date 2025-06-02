<template>
  <div class="user-profile-view">
    <h1>{{ pageTitle }}</h1>
    <div v-if="authStore.isLoadingUser" class="loading-user">
      正在加载用户信息...
    </div>
    <div v-else-if="authStore.user" class="profile-details">
      <p><strong>用户名:</strong> {{ authStore.user.username }}</p>
      <p><strong>邮箱:</strong> {{ authStore.user.email }}</p>
      <p><strong>全名:</strong> {{ authStore.user.full_name || '未设置' }}</p>
      <p><strong>简介:</strong> {{ authStore.user.bio || '未设置' }}</p>
      <p><strong>账户状态:</strong> {{ authStore.user.is_active ? '已激活' : '未激活' }}</p>
      <p><strong>邮箱验证状态:</strong> {{ authStore.user.is_verified ? '已验证' : '未验证' }}</p>
      <p><strong>注册时间:</strong> {{ formatDate(authStore.user.created_at) }}</p>
      </div>
    <div v-else class="no-user-info">
      <p>无法加载用户信息，或您未登录。</p>
      <RouterLink to="/login">请先登录</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { RouterLink } from 'vue-router'; // 如果模板中使用了 RouterLink

const authStore = useAuthStore();
const pageTitle = ref('我的个人主页');

// 简单的日期格式化函数
function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString(undefined, options);
}

// 组件挂载时，如果用户信息不存在且已登录，尝试再次获取
// (authStore.initAuth() 或 App.vue 中的 onMounted 可能已经处理了大部分情况)
onMounted(async () => {
  if (authStore.isLoggedIn && !authStore.user) {
    // 添加一个 isLoadingUser 的状态到 authStore 中会更好，以避免重复请求
    // authStore.isLoadingUser = true; // 假设 store 中有此状态
    await authStore.fetchAndSetUser();
    // authStore.isLoadingUser = false; // 假设 store 中有此状态
  }
});
</script>

<style scoped>
.user-profile-view {
  padding: 30px 40px; /* 增加内边距 */
  max-width: 700px; /* 可以适当调整宽度 */
  margin: 30px auto; /* 上下间距 */
  background-color: var(--secondary-bg-color); /* 使用次级背景色 */
  border: 1px solid var(--border-color);
  border-radius: 0; /* 去掉圆角 */
  box-shadow: 0 0 10px rgba(0,0,0,0.5); /* 可选：轻微阴影 */
}

.user-profile-view h1 {
  text-align: center;
  color: var(--main-text-color);
  margin-bottom: 35px; /* 增加标题下间距 */
  font-size: 2em; /* 增大标题字体 */
  font-weight: normal;
  /* font-family: var(--font-pixel, var(--font-main)); /* 标题使用风格字体 */
  border-bottom: 1px solid var(--border-color); /* 标题下划线 */
  padding-bottom: 15px; /* 下划线与文字间距 */
}

.profile-details p {
  margin-bottom: 18px; /* 增加段落间距 */
  font-size: 1em; /* 调整基础字体大小 */
  line-height: 1.7;
  color: var(--main-text-color);
  border-bottom: 1px dotted var(--border-color); /* 每条信息下加虚线分隔 */
  padding-bottom: 18px; /* 虚线与文字间距 */
}
.profile-details p:last-child {
  border-bottom: none; /* 最后一条信息不需要分隔线 */
  margin-bottom: 0;
  padding-bottom: 0;
}

.profile-details p strong {
  color: #c0c0c0; /* 标签文字颜色稍微亮一点 */
  margin-right: 10px;
  min-width: 130px; /* 确保标签对齐 */
  display: inline-block;
  font-weight: bold; /* 标签加粗 */
}

.loading-user, .no-user-info {
  text-align: center;
  padding: 40px 20px;
  font-size: 1.1em;
  color: #a0a0a0; /* 提示文字颜色 */
  border: 1px dashed var(--border-color);
  margin-top: 20px;
}

.no-user-info a {
  color: var(--link-color); /* 使用CSS变量 */
  text-decoration: underline;
}
.no-user-info a:hover {
  color: var(--link-hover-color);
}
</style>