<template>
  <div class="user-profile-view">
    <h1>{{ pageTitle }}</h1>

    <div v-if="authStore.isLoadingUser" class="loading-user">
      正在加载用户信息...
    </div>

    <div v-else-if="authStore.userError" class="no-user-info error">
      <p>{{ authStore.userError }}</p>
    </div>

    <div v-else-if="authStore.user" class="profile-details-wrapper">
      <div class="profile-avatar-section">
        <Avatar
            v-if="authStore.user.mc_name"
            :name="authStore.user.mc_name"
            alt="Minecraft Avatar"
            class="mc-avatar"
        />
        <div v-else class="mc-avatar-placeholder">无MC头像</div>
      </div>
      <div class="profile-details">
        <p><strong>用户名:</strong> {{ authStore.user.username }}</p>
        <p><strong>邮箱:</strong> {{ authStore.user.email }}</p>
        <p><strong>Minecraft 名称:</strong> {{ authStore.user.mc_name || '未设置' }}</p>
        <p><strong>角色:</strong> {{ authStore.user.role }}</p>
        <p><strong>简介:</strong> {{ authStore.user.bio || '未设置' }}</p>
        <p><strong>账户状态:</strong> {{ authStore.user.is_active ? '已激活' : '未激活' }}</p>
        <p><strong>邮箱验证状态:</strong> {{ authStore.user.is_verified ? '已验证' : '未验证' }}</p>
        <p><strong>注册时间:</strong> {{ formatDate(authStore.user.created_at) }}</p>
      </div>
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
import { RouterLink } from 'vue-router';
import { formatDate } from '@/utils/formatters';
import Avatar from '@/components/Avatar.vue';

const authStore = useAuthStore();
const pageTitle = ref('我的个人主页');

onMounted(async () => {
  // 如果已登录但store中没有用户信息，则尝试获取
  if (authStore.isLoggedIn && !authStore.user) {
    await authStore.fetchAndSetUser();
  }
});
</script>

<style scoped>

:deep(.mc-avatar) {
  width: 128px;
  height: 128px;
  border: 2px solid var(--border-color);
  image-rendering: pixelated; /* 保持像素感 */
}


.user-profile-view {
  padding: 30px 40px;
  max-width: 800px; /* 稍微加宽以容纳头像 */
  margin: 30px auto;
  background-color: var(--secondary-bg-color);
  border: 1px solid var(--border-color);
  border-radius: 0;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}

.user-profile-view h1 {
  text-align: center;
  color: var(--main-text-color);
  margin-bottom: 35px;
  font-size: 2em;
  font-weight: normal;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 15px;
}

.profile-details-wrapper {
  display: flex;
  gap: 30px; /* 头像和信息之间的间距 */
  align-items: flex-start;
}

.profile-avatar-section {
  flex-shrink: 0;
}

.mc-avatar {
  width: 128px;
  height: 128px;
  border: 2px solid var(--border-color);
  image-rendering: pixelated; /* 保持像素感 */
}

.mc-avatar-placeholder {
  width: 128px;
  height: 128px;
  border: 2px dashed var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--link-color);
  background-color: rgba(0, 0, 0, 0.2);
}

.profile-details {
  flex-grow: 1;
}

.profile-details p {
  margin-bottom: 18px;
  font-size: 1em;
  line-height: 1.7;
  color: var(--main-text-color);
  border-bottom: 1px dotted var(--border-color);
  padding-bottom: 18px;
}

.profile-details p:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.profile-details p strong {
  color: #c0c0c0;
  margin-right: 10px;
  min-width: 130px;
  display: inline-block;
  font-weight: bold;
}

.loading-user, .no-user-info {
  text-align: center;
  padding: 40px 20px;
  font-size: 1.1em;
  color: #a0a0a0;
  border: 1px dashed var(--border-color);
  margin-top: 20px;
}

.no-user-info.error {
  color: var(--primary-accent-color);
  border-color: var(--primary-accent-color);
}

.no-user-info a {
  color: var(--link-color);
  text-decoration: underline;
}

.no-user-info a:hover {
  color: var(--link-hover-color);
}
</style>