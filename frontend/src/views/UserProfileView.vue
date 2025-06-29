<template>
  <div class="user-profile-view">
    <h1>{{ pageTitle }}</h1>

    <div v-if="authStore.isLoadingUser" class="loading-user">正在加载用户信息...</div>
    <div v-else-if="authStore.userError" class="no-user-info error"><p>{{ authStore.userError }}</p></div>

    <div v-else-if="authStore.user" class="profile-container">
      <div v-if="!isEditing" class="profile-details-wrapper">
        <div class="profile-avatar-section">
          <Avatar
            :relativeUrl="authStore.user.avatar_url"
            :name="authStore.user.mc_name"
            alt="User Avatar"
            class="mc-avatar"
          />
        </div>
        <div class="profile-details">
          <p><strong>用户名:</strong> {{ authStore.user.username }}</p>
          <p><strong>邮箱:</strong> {{ authStore.user.email }}</p>
          <p><strong>Minecraft 名称:</strong> {{ authStore.user.mc_name || '未设置' }}</p>
          <p><strong>角色:</strong> {{ authStore.user.role }}</p>
          <p><strong>简介:</strong> {{ authStore.user.bio || '未设置' }}</p>
          <p><strong>注册时间:</strong> {{ formatDate(authStore.user.created_at) }}</p>

          <div class="profile-actions">
            <button @click="startEditing" class="api-button">编辑个人资料</button>
            <button @click="isChangingPassword = !isChangingPassword" class="api-button secondary">
              {{ isChangingPassword ? '取消修改密码' : '修改密码' }}
            </button>
          </div>
        </div>
      </div>

      <div v-else class="profile-edit-form">
        <h2>编辑个人资料</h2>

        <div class="form-group avatar-upload-section">
          <label>当前头像:</label>
          <div class="avatar-edit-container">
            <Avatar
              :relativeUrl="avatarPreviewUrl || editableUser.avatar_url"
              :name="editableUser.mc_name"
              alt="Avatar Preview"
              class="mc-avatar"
            />
            <div class="avatar-actions">
              <label for="avatar-file-input" class="api-button">上传新头像</label>
              <input
                type="file"
                id="avatar-file-input"
                @change="onFileSelected"
                accept="image/jpeg, image/png, image/gif"
                hidden
              />
              <button type="button" @click="clearAvatar" class="api-button secondary">恢复默认</button>
            </div>
          </div>
        </div>

        <form @submit.prevent="saveProfile">
          <div class="form-group">
            <label for="mc-name">Minecraft 名称:</label>
            <input id="mc-name" type="text" v-model="editableUser.mc_name">
          </div>
          <div class="form-group">
            <label for="avatar-url">自定义头像 URL (将覆盖上传的头像):</label>
            <input id="avatar-url" type="text" v-model="editableUser.avatar_url" @input="avatarUrlChanged">
            <p class="form-hint">如果想使用上传的头像，请将此项留空。</p>
          </div>
          <div class="form-group">
            <label for="bio">个人简介:</label>
            <textarea id="bio" v-model="editableUser.bio" rows="4"></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="cancelEditing" class="api-button secondary">取消</button>
            <button type="submit" class="api-button" :disabled="isSavingProfile">
              {{ isSavingProfile ? '保存中...' : '保存更改' }}
            </button>
          </div>
        </form>
      </div>

      <div v-if="isChangingPassword" class="password-change-form">
        <h2>修改密码</h2>
        <form @submit.prevent="changePassword">
           <div class="form-group">
              <label for="current-password">当前密码:</label>
              <input id="current-password" type="password" v-model="passwordData.current_password" required>
           </div>
           <div class="form-group">
              <label for="new-password">新密码:</label>
              <input id="new-password" type="password" v-model="passwordData.new_password" required minlength="8">
           </div>
           <div class="form-group">
              <label for="confirm-password">确认新密码:</label>
              <input id="confirm-password" type="password" v-model="passwordData.new_password_confirm" required>
           </div>
           <p v-if="passwordMessage" :class="['message', passwordMessageType]">{{ passwordMessage }}</p>
           <div class="form-actions">
              <button type="submit" class="api-button" :disabled="isSavingPassword">
                {{ isSavingPassword ? '提交中...' : '确认修改密码' }}
              </button>
           </div>
        </form>
      </div>

    </div>

    <div v-else class="no-user-info">
        <p>无法加载用户信息，或您未登录。</p>
        <RouterLink to="/login">请先登录</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { RouterLink } from 'vue-router';
import { formatDate } from '@/utils/formatters';
import Avatar from '@/components/Avatar.vue';
import apiClient from '@/api';
import { alertDialog } from '@/services/dialog';

const authStore = useAuthStore();
const pageTitle = ref('我的个人主页');

const isEditing = ref(false);
const isChangingPassword = ref(false);
const editableUser = ref({});
const isSavingProfile = ref(false);

const selectedFile = ref(null);
const avatarPreviewUrl = ref('');

const passwordData = reactive({
  current_password: '',
  new_password: '',
  new_password_confirm: ''
});
const isSavingPassword = ref(false);
const passwordMessage = ref('');
const passwordMessageType = ref('');

onMounted(async () => {
  if (authStore.isLoggedIn && !authStore.user) {
    await authStore.fetchAndSetUser();
  }
});

function startEditing() {
  editableUser.value = { ...authStore.user };
  selectedFile.value = null;
  avatarPreviewUrl.value = '';
  isEditing.value = true;
  isChangingPassword.value = false;
}

function cancelEditing() {
  isEditing.value = false;
}

function onFileSelected(event) {
  const file = event.target.files[0];
  if (!file) return;

  if (!['image/jpeg', 'image/png', 'image/gif'].includes(file.type)) {
    alertDialog('请选择 JPG, PNG, 或 GIF 格式的图片。', '格式错误');
    return;
  }

  selectedFile.value = file;

  const reader = new FileReader();
  reader.onload = (e) => {
    avatarPreviewUrl.value = e.target.result;
  };
  reader.readAsDataURL(file);

  editableUser.value.avatar_url = '';
}

function avatarUrlChanged() {
    selectedFile.value = null;
    avatarPreviewUrl.value = '';
    document.getElementById('avatar-file-input').value = null;
}

function clearAvatar() {
  selectedFile.value = null;
  avatarPreviewUrl.value = '';
  editableUser.value.avatar_url = '';
  document.getElementById('avatar-file-input').value = null;
}

async function saveProfile() {
  isSavingProfile.value = true;

  try {
    if (selectedFile.value) {
      const formData = new FormData();
      formData.append('file', selectedFile.value);

      const uploadedUserData = await apiClient.post('/users/me/upload-avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      editableUser.value.avatar_url = uploadedUserData.avatar_url;
    }

    await apiClient.patch('/users/me', {
        bio: editableUser.value.bio,
        mc_name: editableUser.value.mc_name,
        avatar_url: editableUser.value.avatar_url
    });

    await authStore.fetchAndSetUser();
    await alertDialog('个人资料更新成功！', '操作成功');
    isEditing.value = false;

  } catch (error) {
    await alertDialog(`更新失败: ${error.response?.data?.detail || '未知错误'}`, '错误');
  } finally {
    isSavingProfile.value = false;
  }
}

async function changePassword() {
  if (passwordData.new_password !== passwordData.new_password_confirm) {
    passwordMessage.value = '新密码与确认密码不匹配。';
    passwordMessageType.value = 'error';
    return;
  }
  isSavingPassword.value = true;
  passwordMessage.value = '';
  try {
    const response = await apiClient.post('/users/me/change-password', passwordData);
    passwordMessage.value = response.message || '密码更新成功！';
    passwordMessageType.value = 'success';
    Object.assign(passwordData, { current_password: '', new_password: '', new_password_confirm: '' });
    isChangingPassword.value = false;
  } catch (error) {
    passwordMessage.value = `修改失败: ${error.response?.data?.detail || '未知错误'}`;
    passwordMessageType.value = 'error';
  } finally {
    isSavingPassword.value = false;
  }
}
</script>

<style scoped>
.user-profile-view {
  padding: 30px 40px;
  max-width: 800px;
  margin: 30px auto;
  background-color: var(--secondary-bg-color);
  border: 1px solid var(--border-color);
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

.profile-container {
  margin-top: 1.5rem;
}

.profile-details-wrapper {
  display: flex;
  gap: 30px;
  align-items: flex-start;
}

.profile-avatar-section {
  flex-shrink: 0;
}

.mc-avatar {
  width: 128px;
  height: 128px;
  border: 2px solid var(--border-color);
  image-rendering: pixelated;
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
  color: var(--link-color);
  margin-right: 10px;
  min-width: 130px;
  display: inline-block;
  font-weight: bold;
}

.loading-user, .no-user-info {
  text-align: center;
  padding: 40px 20px;
  font-size: 1.1em;
  color: var(--link-color);
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

.profile-actions, .form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.api-button.secondary {
  background-color: transparent;
  border-color: var(--border-color);
  color: var(--main-text-color);
}
.api-button.secondary:hover {
  background-color: var(--border-color);
}

.profile-edit-form, .password-change-form {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

.profile-edit-form h2, .password-change-form h2 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  font-weight: normal;
  color: var(--main-text-color);
}

.form-group {
  margin-bottom: 1.5rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--link-color);
}
.form-group input, .form-group textarea {
  width: 100%;
  box-sizing: border-box;
  background-color: var(--main-bg-color);
  border: 1px solid var(--border-color);
  color: var(--main-text-color);
  padding: 8px 10px;
}

.message {
  padding: 0.75rem;
  border: 1px dashed;
  text-align: center;
  margin-bottom: 1rem;
}
.message.success {
  color: var(--secondary-accent-color);
  border-color: var(--secondary-accent-color);
}
.message.error {
  color: var(--primary-accent-color);
  border-color: var(--primary-accent-color);
}

.avatar-upload-section {
  text-align: center;
  margin-bottom: 2rem;
}
.avatar-edit-container {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px dashed var(--border-color);
}
.avatar-actions {
  display: flex;
  gap: 1rem;
}
.form-hint {
    font-size: 0.85em;
    color: var(--link-color);
    margin-top: 0.5rem;
}
</style>