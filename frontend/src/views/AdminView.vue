<template>
  <div class="admin-view">
    <h1 class="page-title">Site Console</h1>
    <p class="page-description">
      欢迎来到自定义管理面板。
    </p>

    <div class="admin-module">
      <h2 class="module-title">站点配置 (site-config.json)</h2>
      <div v-if="configLoading" class="loading-message">正在加载配置...</div>
      <div v-if="!configLoading && siteConfig" class="scrollable-form-container">
        <form @submit.prevent="saveSiteConfig" class="config-form">
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
            <div class="form-group"><label for="footerOwner">版权所有者</label><input id="footerOwner" type="text"
                                                                                      v-model="siteConfig.footer.copyrightOwner">
            </div>
            <div class="form-group"><label for="footerYear">起始年份</label><input id="footerYear" type="number"
                                                                                   v-model.number="siteConfig.footer.startYear">
            </div>
            <div class="form-group"><label for="footerHtml">自定义HTML (页脚)</label><textarea id="footerHtml"
                                                                                               v-model="siteConfig.footer.customHtml"
                                                                                               rows="3"></textarea>
            </div>
          </fieldset>
          <fieldset>
            <legend>备案信息</legend>
            <div class="form-group"><label for="beianIcp">ICP备案号</label><input id="beianIcp" type="text"
                                                                                  v-model="siteConfig.beian.icp"></div>
            <div class="form-group"><label for="gonganText">公安备案号</label><input id="gonganText" type="text"
                                                                                     v-model="siteConfig.beian.gongan.text">
            </div>
            <div class="form-group"><label for="gonganLink">公安备案链接</label><input id="gonganLink" type="text"
                                                                                       v-model="siteConfig.beian.gongan.link">
            </div>
          </fieldset>
          <fieldset>
            <legend>网站追踪代码</legend>
            <div class="form-group"><label for="trackingCode">在此处粘贴统计脚本</label><textarea id="trackingCode"
                                                                                                  v-model="siteConfig.trackingCode"
                                                                                                  rows="5"></textarea>
            </div>
          </fieldset>
        </form>
      </div>
      <div class="form-actions" v-if="!configLoading && siteConfig">
        <button @click="saveSiteConfig" class="api-button" :disabled="isSavingConfig">
          {{ isSavingConfig ? '保存中...' : '保存所有站点配置' }}
        </button>
        <p v-if="configMessage" :class="['message', configMessageType]">{{ configMessage }}</p>
      </div>
    </div>

    <div class="admin-module">
      <h2 class="module-title">画廊管理</h2>
      <div v-if="galleryLoading" class="loading-message">正在加载作品列表...</div>
      <div v-if="galleryError" class="error-message">{{ galleryError }}</div>
      <div v-if="!galleryLoading && galleryItems.length > 0">
        <div class="admin-table-container">
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
        <div class="pagination-controls">
          <button @click="fetchGalleryItems(galleryCurrentPage - 1)" :disabled="galleryCurrentPage <= 1">上一页</button>
          <span>第 {{ galleryCurrentPage }} / {{ galleryTotalPages }} 页</span>
          <button @click="fetchGalleryItems(galleryCurrentPage + 1)"
                  :disabled="galleryCurrentPage >= galleryTotalPages">下一页
          </button>
        </div>
      </div>
      <div v-else-if="!galleryLoading" class="empty-message">暂无画廊作品</div>
    </div>

    <div class="admin-module">
      <h2 class="module-title">用户管理</h2>
      <div v-if="usersLoading" class="loading-message">正在加载用户列表...</div>
      <div v-if="usersError" class="error-message">{{ usersError }}</div>
      <div v-if="!usersLoading && userItems.length > 0">
        <div class="admin-table-container">
          <table class="admin-table">
            <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>角色</th>
              <th>已激活</th>
              <th class="actions-column">操作</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="user in userItems" :key="user.id">
              <td>{{ user.id }}</td>
              <td><input type="text" v-model="user.username" class="table-input"></td>
              <td>{{ user.email }}</td>
              <td><select v-model="user.role" :disabled="user.id === authStore.user?.id">
                <option value="user">user</option>
                <option value="admin">admin</option>
              </select></td>
              <td>{{ user.is_active ? '是' : '否' }}</td>
              <td class="action-buttons">
                <button @click="handleUpdateUser(user)" class="api-button small-button">更新</button>
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
        <div class="pagination-controls">
          <button @click="fetchUsers(usersCurrentPage - 1)" :disabled="usersCurrentPage <= 1">上一页</button>
          <span>第 {{ usersCurrentPage }} / {{ usersTotalPages }} 页</span>
          <button @click="fetchUsers(usersCurrentPage + 1)" :disabled="usersCurrentPage >= usersTotalPages">下一页
          </button>
        </div>
      </div>
      <div v-else-if="!usersLoading" class="empty-message">暂无用户</div>
    </div>

    <div class="admin-module">
      <h2 class="module-title">核心成员管理</h2>
      <div class="sub-module-container member-add-form">
        <h3 class="sub-module-title">添加新成员</h3>
        <form @submit.prevent="handleAddMember" class="config-form condensed">
          <div class="form-group"><label>名称</label><input type="text" v-model="newMember.name" placeholder="必填"
                                                            required></div>
          <div class="form-group"><label>角色/职位</label><input type="text" v-model="newMember.role"
                                                                 placeholder="例如：建筑师"></div>
          <div class="form-group"><label>介绍</label><textarea v-model="newMember.bio" rows="3"
                                                               placeholder="成员的简介"></textarea></div>
          <button type="submit" class="api-button">添加成员</button>
        </form>
      </div>

      <div class="sub-module-container">
        <h3 class="sub-module-title">编辑现有成员</h3>
        <div v-if="membersLoading" class="loading-message">正在加载成员列表...</div>
        <div v-if="membersError" class="error-message">{{ membersError }}</div>
        <div v-if="!membersLoading" class="member-editor">
          <div class="member-selector">
            <div class="form-group">
              <label for="role-filter">按角色筛选</label>
              <select id="role-filter" v-model="selectedRole">
                <option v-for="role in memberRoles" :key="role" :value="role">{{
                    role === 'all' ? '所有角色' : role
                  }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="member-select">选择要编辑的成员</label>
              <select id="member-select" :value="selectedMemberId" @change="handleMemberSelection">
                <option :value="null">-- 请选择 --</option>
                <option v-for="member in filteredMembers" :key="member.id" :value="member.id">{{ member.name }}</option>
              </select>
              <div v-if="isMemberDirty" class="dirty-warning">检测到未保存的修改！</div>
            </div>
          </div>
          <form v-if="memberToEdit" @submit.prevent="handleUpdateMember" class="config-form member-edit-form">
            <fieldset>
              <legend>正在编辑: {{ memberToEdit.name }}</legend>
              <div class="form-group"><label>名称</label><input type="text" v-model="memberToEdit.name"></div>
              <div class="form-group"><label>角色/职位</label><input type="text" v-model="memberToEdit.role"></div>
              <div class="form-group"><label>头像 URL (可选)</label><input type="text" v-model="memberToEdit.avatar_url"
                                                                           placeholder="留空则使用MC皮肤头像"></div>
              <div class="form-group"><label>个人介绍</label><textarea v-model="memberToEdit.bio" rows="5"></textarea>
              </div>
              <div class="member-card-actions">
                <button type="submit" class="api-button small-button">保存更改</button>
                <button type="button" @click="handleDeleteMember" class="api-button small-button danger">删除此成员
                </button>
              </div>
            </fieldset>
          </form>
          <div v-else class="empty-message selector-placeholder">请从上方选择一位成员进行编辑。</div>
        </div>
      </div>
    </div>

    <div class="admin-module">
      <h2 class="module-title">应用配置 (.env)</h2>
      <div class="action-card"><h3 class="card-title">重载配置</h3>
        <p class="card-description">修改服务器 `.env` 文件后，点击此按钮使新配置生效，无需重启服务。</p>
        <button @click="handleReloadConfig" :disabled="isReloading" class="api-button"><span
            v-if="isReloading">正在执行...</span><span v-else>重载应用配置</span></button>
        <p v-if="reloadMessage" :class="['message', reloadMessageType]">{{ reloadMessage }}</p></div>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, computed, watch} from 'vue';
import apiClient from '@/api';
import {useSettingsStore} from '@/stores/settings';
import {useAuthStore} from '@/stores/auth';
import {formatDate} from '@/utils/formatters';
import {alertDialog, confirmDialog} from '@/services/dialog';

const settingsStore = useSettingsStore();
const authStore = useAuthStore();

// --- States (Refactored to use ref for lists) ---
// Site Config
const siteConfig = ref(null);
const configLoading = ref(true);
const isSavingConfig = ref(false);
const configMessage = ref('');
const configMessageType = ref('');

// Gallery Management
const galleryItems = ref([]);
const galleryLoading = ref(true);
const galleryError = ref(null);
const galleryCurrentPage = ref(1);
const galleryTotalPages = ref(1);

// User Management
const userItems = ref([]);
const usersLoading = ref(true);
const usersError = ref(null);
const usersCurrentPage = ref(1);
const usersTotalPages = ref(1);

// Core Members Management
const memberList = ref([]);
const membersLoading = ref(true);
const membersError = ref(null);
const selectedRole = ref('all');
const selectedMemberId = ref(null);
const isMemberDirty = computed(() => { // 改为计算属性，实时反应
  if (!memberToEdit.value) return false;
  return JSON.stringify(memberToEdit.value) !== originalMemberJSON.value;
});
const memberToEdit = ref(null);
const originalMemberJSON = ref('');
const newMember = ref({name: '', role: '', bio: ''});

// App Reload
const isReloading = ref(false);
const reloadMessage = ref('');
const reloadMessageType = ref('');

// --- Computed Properties ---
const memberRoles = computed(() => {
  const roles = new Set(memberList.value.map(m => m.role).filter(Boolean));
  return ['all', ...roles];
});

const filteredMembers = computed(() => {
  if (selectedRole.value === 'all') return memberList.value;
  return memberList.value.filter(m => m.role === selectedRole.value);
});

// 使用 watch 监听 selectedMemberId 的变化，来加载要编辑的成员
watch(selectedMemberId, (newId, oldId) => {
  if (isMemberDirty.value) {
    if (!confirm('您有未保存的修改。确定要放弃并切换到其他成员吗？')) {
      // 如果用户取消，则将 selectedMemberId 恢复原状，阻止切换
      selectedMemberId.value = oldId;
      return;
    }
  }
  loadMemberForEditing(newId);
});

// 监听编辑中的成员对象，用于判断是否有未保存的更改
watch(memberToEdit, (newVal) => {
  // 这个逻辑可以简化或移除，因为 isMemberDirty 已经是计算属性了
}, {deep: true});

// --- Lifecycle Hooks ---
onMounted(() => {
  fetchSiteConfig();
  fetchGalleryItems(1);
  fetchUsers(1);
  fetchMembers();
});

// --- Methods ---
const getFullImageUrl = (relativeUrl) => {
  if (!relativeUrl) return '/placeholder-image.png';
  return `${settingsStore.apiBaseUrl}${relativeUrl}`;
};

// Site Config Methods
async function fetchSiteConfig() {
  configLoading.value = true;
  try {
    siteConfig.value = await apiClient.get('/api/admin/site-config');
  } catch (error) {
    if (error.response && error.response.status === 404) {
      siteConfig.value = { /* Default config structure */};
    } else {
      configMessage.value = '加载站点配置失败。';
      configMessageType.value = 'error';
    }
  } finally {
    configLoading.value = false;
  }
}

async function saveSiteConfig() {
  isSavingConfig.value = true;
  try {
    const response = await apiClient.post('/api/admin/site-config', siteConfig.value);
    configMessage.value = `${response.message || '配置已保存！'}\n路径: ${response.path || 'N/A'}`;
    configMessageType.value = 'success';
  } catch (error) {
    configMessage.value = `保存失败: ${error.response?.data?.detail || '未知错误'}`;
    configMessageType.value = 'error';
  } finally {
    isSavingConfig.value = false;
  }
}

function addContactItem() {
  siteConfig.value.contactInfo.items.push({label: '', value: '', url: ''});
}

function removeContactItem(index) {
  siteConfig.value.contactInfo.items.splice(index, 1);
}

// Gallery Methods
async function fetchGalleryItems(page = 1) {
  galleryLoading.value = true;
  try {
    const data = await apiClient.get(`/api/admin/gallery-items?page=${page}&page_size=10`);
    galleryItems.value = data.items;
    galleryTotalPages.value = data.total_pages;
    galleryCurrentPage.value = data.page;
  } catch (error) {
    galleryError.value = '无法加载作品列表。';
  } finally {
    galleryLoading.value = false;
  }
}

async function deleteGalleryItem(itemId) {
  // --- 使用 confirmDialog 替代 confirm ---
  if (!await confirmDialog(`确定要永久删除 ID 为 ${itemId} 的作品及其文件吗？`)) return;
  try {
    await apiClient.delete(`/api/admin/gallery-items/${itemId}`);
    fetchGalleryItems(galleryCurrentPage.value);
  } catch (error) {
    // --- 使用 alertDialog 替代 alert ---
    await alertDialog('删除作品失败！');
  }
}

// User Methods
async function fetchUsers(page = 1) {
  usersLoading.value = true;
  try {
    const data = await apiClient.get(`/api/admin/users?page=${page}&page_size=10`);
    userItems.value = data.items;
    usersTotalPages.value = data.total_pages;
    usersCurrentPage.value = data.page;
  } catch (error) {
    usersError.value = '无法加载用户列表。';
  } finally {
    usersLoading.value = false;
  }
}

async function handleUpdateUser(user) {
  try {
    const payload = {username: user.username, role: user.role};
    await apiClient.patch(`/api/admin/users/${user.id}`, payload);
    // --- 使用 alertDialog 替代 alert ---
    await alertDialog(`用户 ${user.email} 的信息已更新。`);
  } catch (error) {
    await alertDialog(`更新用户失败: ${error.response?.data?.detail || '未知错误'}`);
    fetchUsers(usersCurrentPage.value);
  }
}


async function toggleUserStatus(user) {
  try {
    const updated = await apiClient.patch(`/api/admin/users/${user.id}`, {is_active: !user.is_active});
    user.is_active = updated.is_active;
  } catch (error) {
    alert('更新用户状态失败！');
    fetchUsers(usersCurrentPage.value);
  }
}

async function deleteUser(user) {
  const confirmed = await confirmDialog(
    `您确定要永久删除用户 "${user.username}" 吗？\n\n警告：此操作不可逆！该用户上传的所有画廊作品也将被一并永久删除。`,
    '高危操作确认'
  );

  if (!confirmed) return;

  try {
    await apiClient.delete(`/api/admin/users/${user.id}`);
    await alertDialog(`用户 ${user.username} 已被成功删除。`, '操作成功');
    fetchUsers(1); // 刷新用户列表
  } catch (error) {
    await alertDialog(`删除用户失败: ${error.response?.data?.detail || '未知错误'}`, '错误');
  }
}



// Member Methods
async function fetchMembers() {
  membersLoading.value = true;
  try {
    const data = await apiClient.get('/api/admin/members');
    memberList.value = data;
  } catch (error) {
    membersError.value = "无法加载核心成员列表。";
  } finally {
    membersLoading.value = false;
  }
}

function handleMemberSelection(event) {
  const newId = event.target.value;
  if (isMemberDirty.value) {
    if (!confirm('您有未保存的修改。确定要放弃这些修改并切换到其他成员吗？')) {
      event.target.value = selectedMemberId.value;
      return;
    }
  }
  loadMemberForEditing(newId);
}

function loadMemberForEditing(id) {
  if (!id || id === 'null') {
    memberToEdit.value = null;
    originalMemberJSON.value = '';
    return;
  }
  const selected = memberList.value.find(m => m.id == id);
  if (selected) {
    memberToEdit.value = {...selected}; // 创建副本以供编辑
    originalMemberJSON.value = JSON.stringify(selected); // 存储原始状态
  } else {
    memberToEdit.value = null;
    originalMemberJSON.value = '';
  }
}

async function handleAddMember() {
  if (!newMember.value.name) {
    await alertDialog('新成员的名称不能为空！');
    return;
  }
  try {
    await apiClient.post('/api/admin/members', newMember.value);
    await alertDialog('新成员添加成功！');
    newMember.value = {name: '', role: '', bio: ''};
    await fetchMembers();
  } catch (error) {
    await alertDialog(`添加成员失败：${error.response?.data?.detail || '未知错误'}`);
  }
}

async function handleUpdateMember() {
  if (!memberToEdit.value) return;
  try {
    await apiClient.patch(`/api/admin/members/${memberToEdit.value.id}`, memberToEdit.value);
    await alertDialog('成员信息更新成功！');
    const updatedId = memberToEdit.value.id;
    await fetchMembers();
    loadMemberForEditing(updatedId);
  } catch (error) {
    await alertDialog(`更新失败: ${error.response?.data?.detail || '未知错误'}`);
  }
}


async function handleDeleteMember() {
  if (!memberToEdit.value) return;

  const confirmed = await confirmDialog(
    `您确定要永久删除核心成员 "${memberToEdit.value.name}" 吗？\n\n警告：此操作不可逆！所有关联到该成员的画廊作品将变为“匿名作者”。`,
    '删除成员确认'
  );

  if (!confirmed) return;

  try {
    await apiClient.delete(`/api/admin/members/${memberToEdit.value.id}`);
    await alertDialog('成员已删除。', '操作成功');
    loadMemberForEditing(null); // 清空编辑区
    await fetchMembers(); // 重新加载成员列表
  } catch (error) {
    await alertDialog(`删除失败: ${error.response?.data?.detail || '未知错误'}`, '错误');
  }
}

// App Reload Method
async function handleReloadConfig() {
  isReloading.value = true;
  try {
    const response = await apiClient.post('/admin/reload-config');
    reloadMessage.value = response.message || '配置已成功重载！';
    reloadMessageType.value = 'success';
  } catch (error) {
    reloadMessage.value = `错误: ${error.response?.data?.detail || '未知错误'}`;
  } finally {
    isReloading.value = false;
  }
}
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

.scrollable-form-container {
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 1rem;
  margin-right: -1rem;
  border: 1px dashed var(--border-color);
  padding: 1rem;
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

.actions-column {
  width: 220px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: nowrap;
}

.admin-table th {
  background-color: var(--main-bg-color);
}

.api-button.small-button {
  padding: 5px 10px;
  font-size: 0.8em;
  font-weight: normal;
}

.table-input {
  width: 100%;
  box-sizing: border-box;
  background-color: transparent;
  border: 1px solid transparent;
  color: var(--main-text-color);
  padding: 4px;
  border-radius: 2px;
}

.table-input:focus {
  background-color: var(--main-bg-color);
  border-color: var(--primary-accent-color);
  outline: none;
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
  white-space: pre-wrap;
  word-break: break-all;
}

.message.success {
  color: #4caf50;
  border: 1px dashed #4caf50;
}

.message.error {
  color: var(--primary-accent-color);
  border-color: var(--primary-accent-color);
}

.message.info {
  color: #2196F3;
  border: 1px dashed #2196F3;
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
  padding: 8px 10px;
  border-radius: 2px;
  width: 100%;
}

select:disabled, .api-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.config-form fieldset {
  border: 1px solid var(--border-color);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 4px;
}

.config-form legend {
  padding: 0 0.5rem;
  font-weight: bold;
  color: var(--main-text-color);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input[type="text"], .form-group input[type="number"], .form-group textarea, .form-group select {
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
  margin-top: 1.5rem;
  border-top: 1px solid var(--border-color);
  padding-top: 1.5rem;
}

.sub-module-container {
  border: 1px solid var(--border-color);
  padding: 1.5rem;
  margin-top: 2rem;
  border-radius: 4px;
}

.sub-module-title {
  font-size: 1.4rem;
  margin-top: 0;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  font-weight: normal;
  color: var(--link-color);
  border-bottom: 1px dashed var(--border-color);
}

.config-form.condensed .form-group {
  margin-bottom: 1rem;
}

.member-editor {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
  align-items: flex-start;
}

.member-selector {
  position: sticky;
  top: 80px;
}

.member-edit-form fieldset {
  margin-top: 0;
  border-color: var(--primary-accent-color);
}

.member-card-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.dirty-warning {
  margin-top: 0.5rem;
  padding: 0.5rem;
  font-size: 0.85em;
  color: var(--primary-accent-color);
  background-color: rgba(183, 28, 28, 0.1);
  border: 1px dashed var(--primary-accent-color);
  border-radius: 3px;
  text-align: center;
}

.selector-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
  border: 2px dashed var(--border-color);
  border-radius: 4px;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: var(--main-bg-color);
  border-top: 1px solid var(--border-color);
}

.pagination-controls button {
  padding: 6px 12px;
}

@media (max-width: 900px) {
  .admin-view {
    padding: 1rem;
  }

  .member-editor {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .member-selector {
    position: static;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 1rem;
    margin-bottom: 1rem;
  }

  .scrollable-form-container {
    max-height: 70vh;
  }
}
</style>