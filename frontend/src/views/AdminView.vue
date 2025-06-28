<template>
  <div class="admin-view">
    <h1 class="page-title">Site Console</h1>
    <p class="page-description">
      欢迎来到自定义管理面板。
    </p>

    <div class="admin-module">
      <h2 class="module-title">站点配置 (site-config.json)</h2>
      <div v-if="configLoading" class="loading-message">正在加载配置...</div>

      <form v-if="!configLoading && siteConfig" @submit.prevent="saveSiteConfig" class="config-form">

        <fieldset>
          <legend>基础配置</legend>
          <div class="form-group">
            <label for="apiBaseUrl">后端 API 地址</label>
            <input id="apiBaseUrl" type="text" v-model="siteConfig.apiBaseUrl">
          </div>
        </fieldset>

        <fieldset>
          <legend>首页顶部</legend>
          <div class="form-group">
            <label for="heroTitle">主标题</label>
            <input id="heroTitle" type="text" v-model="siteConfig.heroSection.title">
          </div>
          <div class="form-group">
            <label for="heroSubtitle">副标题</label>
            <input id="heroSubtitle" type="text" v-model="siteConfig.heroSection.subtitle">
          </div>
        </fieldset>

        <fieldset>
          <legend>联系方式</legend>
          <div class="form-group">
            <label for="contactTitle">模块标题</label>
            <input id="contactTitle" type="text" v-model="siteConfig.contactInfo.title">
          </div>
          <div class="form-group">
            <label for="contactDesc">模块描述</label>
            <textarea id="contactDesc" v-model="siteConfig.contactInfo.description" rows="2"></textarea>
          </div>
          <div v-for="(item, index) in siteConfig.contactInfo.items" :key="index" class="dynamic-item">
            <div class="form-group">
              <label :for="'contact-label-' + index">项目 {{ index + 1 }}: 标签</label>
              <input :id="'contact-label-' + index" type="text" v-model="item.label" placeholder="例如：邮箱">
            </div>
            <div class="form-group">
              <label :for="'contact-value-' + index">项目 {{ index + 1 }}: 值</label>
              <input :id="'contact-value-' + index" type="text" v-model="item.value"
                     placeholder="例如：contact@example.com">
            </div>
            <div class="form-group">
              <label :for="'contact-url-' + index">项目 {{ index + 1 }}: 链接 (可选)</label>
              <input :id="'contact-url-' + index" type="text" v-model="item.url"
                     placeholder="例如：mailto:contact@example.com">
            </div>
            <button type="button" @click="removeContactItem(index)" class="api-button small-button danger">移除此项
            </button>
          </div>
          <button type="button" @click="addContactItem" class="api-button small-button">添加联系方式</button>
        </fieldset>

        <fieldset>
          <legend>关于页面内容</legend>
          <div class="form-group">
            <label for="aboutPageHtml">HTML 内容</label>
            <textarea id="aboutPageHtml" v-model="siteConfig.aboutPageHtml" rows="10"></textarea>
          </div>
        </fieldset>

        <fieldset>
          <legend>页脚</legend>
          <div class="form-group">
            <label for="footerOwner">版权所有者</label>
            <input id="footerOwner" type="text" v-model="siteConfig.footer.copyrightOwner">
          </div>
          <div class="form-group">
            <label for="footerYear">起始年份</label>
            <input id="footerYear" type="number" v-model.number="siteConfig.footer.startYear">
          </div>
          <div class="form-group">
            <label for="footerHtml">自定义HTML (页脚)</label>
            <textarea id="footerHtml" v-model="siteConfig.footer.customHtml" rows="3"></textarea>
          </div>
        </fieldset>

        <fieldset>
          <legend>备案信息</legend>
          <div class="form-group">
            <label for="beianIcp">ICP备案号</label>
            <input id="beianIcp" type="text" v-model="siteConfig.beian.icp">
          </div>
          <div class="form-group">
            <label for="gonganText">公安备案号</label>
            <input id="gonganText" type="text" v-model="siteConfig.beian.gongan.text">
          </div>
          <div class="form-group">
            <label for="gonganLink">公安备案链接</label>
            <input id="gonganLink" type="text" v-model="siteConfig.beian.gongan.link">
          </div>
        </fieldset>

        <fieldset>
          <legend>网站追踪代码</legend>
          <div class="form-group">
            <label for="trackingCode">在此处粘贴统计脚本</label>
            <textarea id="trackingCode" v-model="siteConfig.trackingCode" rows="5"></textarea>
          </div>
        </fieldset>

        <div class="form-actions">
          <button type="submit" class="api-button" :disabled="isSavingConfig">
            {{ isSavingConfig ? '保存中...' : '保存所有站点配置' }}
          </button>
          <p v-if="configMessage" :class="['message', configMessageType]">
            {{ configMessage }}
          </p>
        </div>
      </form>
    </div>

    <div class="admin-module">
      <h2 class="module-title">画廊管理</h2>
      <div v-if="galleryLoading" class="loading-message">正在加载作品列表...</div>
      <div v-if="galleryError" class="error-message">{{ galleryError }}</div>
      <div v-if="!galleryLoading && galleryItems.length > 0" class="admin-table-container">
        <table class="admin-table">
          <thead>
          <tr>
            <th>ID</th>
            <th>预览</th>
            <th>标题</th>
            <th>创作者</th>
            <th>上传者</th>
            <th>上传时间</th>
            <th>操作</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="item in galleryItems" :key="item.id">
            <td>{{ item.id }}</td>
            <td><img :src="getFullImageUrl(item.thumbnail_url)" :alt="item.title" class="table-thumbnail"/></td>
            <td>{{ item.title }}</td>
            <td>{{ item.builder?.name || 'N/A' }}</td>
            <td>{{ item.uploader?.username || 'N/A' }}</td>
            <td>{{ formatDate(item.uploaded_at) }}</td>
            <td>
              <button @click="deleteGalleryItem(item.id)" class="api-button small-button danger">删除</button>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="!galleryLoading && galleryItems.length === 0" class="empty-message">暂无画廊作品</div>
    </div>

    <div class="admin-module">
      <h2 class="module-title">用户管理</h2>
      <div v-if="usersLoading" class="loading-message">正在加载用户列表...</div>
      <div v-if="usersError" class="error-message">{{ usersError }}</div>
      <div v-if="!usersLoading && users.length > 0" class="admin-table-container">
        <table class="admin-table">
          <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>已激活</th>
            <th>操作</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>
              <select v-model="user.role" @change="updateUserRole(user, $event.target.value)"
                      :disabled="user.id === authStore.user?.id">
                <option value="user">user</option>
                <option value="admin">admin</option>
              </select>
            </td>
            <td>{{ user.is_active ? '是' : '否' }}</td>
            <td>
              <button @click="toggleUserStatus(user)" class="api-button small-button"
                      :disabled="user.id === authStore.user?.id">切换激活
              </button>
              <button @click="deleteUser(user)" class="api-button small-button danger"
                      :disabled="user.id === authStore.user?.id">删除
              </button>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="admin-module">
      <h2 class="module-title">应用配置 (.env)</h2>
      <div class="action-card">
        <h3 class="card-title">重载配置</h3>
        <p class="card-description">修改服务器 `.env` 文件后，点击此按钮使新配置生效，无需重启服务。</p>
        <button @click="handleReloadConfig" :disabled="isLoading" class="api-button">
          <span v-if="isLoading">正在执行...</span>
          <span v-else>重载应用配置</span>
        </button>
        <p v-if="reloadMessage" :class="['message', reloadMessageType]">{{ reloadMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue';
import apiClient from '@/api';
import {useSettingsStore} from '@/stores/settings';
import {useAuthStore} from '@/stores/auth';
import {formatDate} from '@/utils/formatters';

const settingsStore = useSettingsStore();
const authStore = useAuthStore();

// --- 站点配置的状态 ---
const siteConfig = ref(null);
const configLoading = ref(true);
const isSavingConfig = ref(false);
const configMessage = ref('');
const configMessageType = ref('');

// --- 画廊管理的状态 ---
const galleryItems = ref([]);
const galleryLoading = ref(true);
const galleryError = ref(null);

// --- 应用配置重载的状态 ---
const isLoading = ref(false);
const reloadMessage = ref('');
const reloadMessageType = ref('');

// --- 用户管理的状态 ---
const users = ref([]);
const usersLoading = ref(true);
const usersError = ref(null);

// --- 辅助函数 ---
function getFullImageUrl(relativeUrl) {
  if (!relativeUrl) return '/placeholder-image.png';
  return `${settingsStore.apiBaseUrl}${relativeUrl}`;
}

// --- 站点配置函数 ---
async function fetchSiteConfig() {
  configLoading.value = true;
  try {
    siteConfig.value = await apiClient.get('/api/admin/site-config');
  } catch (error) {
    // 【核心修正】如果后端返回404（文件不存在），则加载默认配置到表单中
    if (error.response && error.response.status === 404) {
      console.warn('在服务器上未找到 site-config.json，为管理员加载默认模板。');
      // 直接从 settings store 导入并使用默认配置
      // (需要在 settings.js 中导出 DEFAULT_SITE_CONFIG)
      // 为了简单起见，我们在这里重新定义一个简化的默认结构
      siteConfig.value = {
        apiBaseUrl: "http://127.0.0.1:8000",
        heroSection: {title: "", subtitle: ""},
        contactInfo: {title: "", description: "", items: []},
        footer: {copyrightOwner: "", startYear: new Date().getFullYear(), customHtml: ""},
        beian: {icp: "", gongan: {text: "", link: ""}},
        aboutPageHtml: "",
        trackingCode: ""
      };
      configMessage.value = '提示：服务器上暂无配置文件，您可以填写以下表单来创建。';
      configMessageType.value = 'info'; // 使用一个新的消息类型
    } else {
      configMessage.value = '加载站点配置失败。';
      configMessageType.value = 'error';
      console.error(error);
    }
  } finally {
    configLoading.value = false;
  }

}

async function saveSiteConfig() {
  isSavingConfig.value = true;
  configMessage.value = '';
  configMessageType.value = '';
  try {
    const response = await apiClient.post('/api/admin/site-config', siteConfig.value);
    configMessage.value = response.message || '配置已保存！刷新网站前台页面即可看到更改。';
    configMessageType.value = 'success';
  } catch (error) {
    configMessage.value = `保存失败：${error.response?.data?.detail || '未知错误'}`;
    configMessageType.value = 'error';
    console.error(error);
  } finally {
    isSavingConfig.value = false;
  }
}

function addContactItem() {
  if (siteConfig.value?.contactInfo?.items) {
    siteConfig.value.contactInfo.items.push({label: '', value: '', url: ''});
  }
}

function removeContactItem(index) {
  if (siteConfig.value?.contactInfo?.items) {
    siteConfig.value.contactInfo.items.splice(index, 1);
  }
}

// --- 画廊管理函数 ---
async function fetchGalleryItems() {
  galleryLoading.value = true;
  galleryError.value = null;
  try {
    galleryItems.value = await apiClient.get('/api/admin/gallery-items');
  } catch (error) {
    console.error("获取画廊作品列表失败:", error);
    galleryError.value = '无法加载作品列表。';
  } finally {
    galleryLoading.value = false;
  }
}

async function deleteGalleryItem(itemId) {
  if (!confirm(`确定要永久删除 ID 为 ${itemId} 的作品及其文件吗？`)) return;
  try {
    await apiClient.delete(`/api/admin/gallery-items/${itemId}`);
    galleryItems.value = galleryItems.value.filter(item => item.id !== itemId);
  } catch (error) {
    alert('删除作品失败！');
    console.error(error);
  }
}

// --- 用户管理函数 ---
async function fetchUsers() {
  usersLoading.value = true;
  usersError.value = null;
  try {
    users.value = await apiClient.get('/api/admin/users');
  } catch (error) {
    console.error("获取用户列表失败:", error);
    usersError.value = '无法加载用户列表。';
  } finally {
    usersLoading.value = false;
  }
}

async function toggleUserStatus(user) {
  try {
    const updatedUser = await apiClient.patch(`/api/admin/users/${user.id}`, {is_active: !user.is_active});
    const index = users.value.findIndex(u => u.id === user.id);
    if (index !== -1) users.value[index] = updatedUser;
  } catch (error) {
    alert('更新用户状态失败！');
    console.error(error);
  }
}

async function updateUserRole(user, newRole) {
  try {
    const updatedUser = await apiClient.patch(`/api/admin/users/${user.id}`, {role: newRole});
    const index = users.value.findIndex(u => u.id === user.id);
    if (index !== -1) users.value[index] = updatedUser;
    alert(`用户 ${user.username} 的角色已更新为 ${newRole}`);
  } catch (error) {
    alert('更新用户角色失败！');
    user.role = user.role === 'admin' ? 'user' : 'admin'; // Revert on failure
    console.error(error);
  }
}

async function deleteUser(user) {
  if (!confirm(`确定要永久删除用户 "${user.username}" 吗？\n该用户的所有关联数据（如画廊作品、令牌）也将被一并删除！`)) return;
  try {
    const response = await apiClient.delete(`/api/admin/users/${user.id}`);
    users.value = users.value.filter(u => u.id !== user.id);
    alert(response.message || `用户 ${user.username} 已被删除。`);
  } catch (error) {
    alert(`删除用户失败：${error.response?.data?.detail || '未知错误'}`);
    console.error(error);
  }
}

// --- 应用配置重载函数 ---
async function handleReloadConfig() {
  isLoading.value = true;
  reloadMessage.value = '';
  try {
    const response = await apiClient.post('/admin/reload-config');
    reloadMessage.value = response.message || '配置已成功重载！';
    reloadMessageType.value = 'success';
  } catch (error) {
    reloadMessage.value = `错误: ${error.response?.data?.detail || '未知错误'}`;
    reloadMessageType.value = 'error';
  } finally {
    isLoading.value = false;
  }
}

// --- onMounted ---
onMounted(() => {
  fetchUsers();
  fetchGalleryItems();
  fetchSiteConfig();
});
</script>

<style scoped>
.admin-view {
  padding: 2rem 4rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-family: var(--font-special), cursive;
  font-size: 3rem;
  text-align: center;
  margin-bottom: 1rem;
}

.page-description {
  text-align: center;
  color: var(--link-color);
  margin-bottom: 4rem;
}

.admin-module {
  background-color: var(--secondary-bg-color);
  border: 1px solid var(--border-color);
  padding: 2rem;
  margin-bottom: 2rem;
  border-radius: 4px;
}

.module-title {
  font-size: 1.8rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
  margin-bottom: 2rem;
}

.admin-table-container {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.95em;
}

.admin-table th, .admin-table td {
  border: 1px solid var(--border-color);
  padding: 10px 15px;
  vertical-align: middle;
}

.admin-table th {
  background-color: var(--main-bg-color);
}

.admin-table td .api-button {
  margin-right: 8px;
}

.api-button.small-button {
  padding: 5px 10px;
  font-size: 0.8em;
  font-weight: normal;
}

.action-card {
  background-color: var(--main-bg-color);
  border: 2px solid var(--border-color);
  padding: 1.5rem;
}

.card-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.card-description {
  opacity: 0.8;
  margin-bottom: 1.5rem;
}

.message {
  margin-top: 1rem;
  padding: 0.75rem;
  text-align: center;
  border-radius: 4px;
}

.message.success {
  color: #4caf50;
  border: 1px dashed #4caf50;
}

.message.error {
  color: var(--primary-accent-color);
  border-color: var(--primary-accent-color);
}

.table-thumbnail {
  width: 80px;
  height: 60px;
  object-fit: cover;
  border: 1px solid var(--border-color);
  border-radius: 2px;
}

.api-button.danger {
  background-color: var(--primary-accent-color);
  border-color: var(--primary-accent-color);
  color: white;
}

.api-button.danger:hover {
  background-color: #6e3636;
}

.empty-message, .loading-message, .error-message {
  text-align: center;
  padding: 2rem;
  color: var(--link-color);
}

.error-message {
  color: var(--primary-accent-color);
}

select {
  background-color: var(--main-bg-color);
  color: var(--main-text-color);
  border: 1px solid var(--border-color);
  padding: 4px 8px;
  border-radius: 2px;
}

select:disabled, .api-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* --- 新表单样式 --- */
.config-form fieldset {
  border: 1px solid var(--border-color);
  padding: 1.5rem;
  margin-bottom: 2rem;
  border-radius: 4px;
}

.config-form legend {
  padding: 0 0.5rem;
  font-weight: bold;
  color: var(--main-text-color);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group textarea {
  width: 100%;
  padding: 8px 10px;
  box-sizing: border-box;
  background-color: var(--main-bg-color);
  border: 1px solid var(--border-color);
  color: var(--main-text-color);
  border-radius: 2px;
}

.dynamic-item {
  border: 1px dashed var(--border-color);
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.form-actions {
  margin-top: 2rem;
  border-top: 1px solid var(--border-color);
  padding-top: 2rem;
}

.message.info {
  color: #2196F3;
  border: 1px dashed #2196F3;
}
</style>