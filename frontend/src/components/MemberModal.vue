<template>
  <div v-if="isOpen" class="modal-backdrop" @click="close">
    <div class="modal-content" @click.stop>
      <button class="modal-close-button" @click="close">&times;</button>

      <template v-if="member">
        <div v-if="!isEditing" class="view-mode">
          <Avatar
            :relativeUrl="member.avatar_url"
            :name="member.name"
            :alt="member.name"
            class="modal-avatar"
          />
          <h2>{{ member.name }}</h2>
          <h4>{{ member.role }}</h4>
          <p class="modal-bio">{{ member.bio || '暂无介绍' }}</p>

          <button v-if="canEdit" @click="startEditing" class="api-button edit-button">
            编辑我的信息
          </button>
        </div>

        <div v-else class="edit-mode">
          <h2>编辑信息</h2>
          <form @submit.prevent="saveChanges" class="edit-form">
            <div class="form-group">
              <label for="member-role">角色/职位</label>
              <input id="member-role" type="text" v-model="editableMember.role">
            </div>
            <div class="form-group">
              <label for="member-avatar">头像 URL (留空则使用MC皮肤)</label>
              <input id="member-avatar" type="text" v-model="editableMember.avatar_url">
            </div>
            <div class="form-group">
              <label for="member-bio">个人介绍</label>
              <textarea id="member-bio" v-model="editableMember.bio" rows="5"></textarea>
            </div>
            <p v-if="errorMessage" class="message error">{{ errorMessage }}</p>
            <div class="form-actions">
              <button type="button" @click="cancelEditing" class="api-button secondary">取消</button>
              <button type="submit" class="api-button" :disabled="isSaving">
                {{ isSaving ? '保存中...' : '保存更改' }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import Avatar from './Avatar.vue';
import apiClient from '@/api';

// 1. 定义 props 和 emits
const props = defineProps({
  isOpen: { type: Boolean, required: true },
  member: { type: Object, default: null },
  currentUser: { type: Object, default: null } // 接收当前登录用户
});

const emit = defineEmits(['close', 'member-updated']);

// 2. 定义组件内部状态
const isEditing = ref(false);
const editableMember = ref(null); // 用于表单绑定的可编辑成员对象
const isSaving = ref(false);
const errorMessage = ref('');

// 3. 计算属性判断当前用户是否可编辑此成员
const canEdit = computed(() => {
  return props.currentUser && props.member && props.currentUser.username === props.member.name;
});

// 4. 监听弹窗开启状态
watch(() => props.isOpen, (newVal) => {
  if (newVal && props.member) {
    // 弹窗打开时，重置编辑状态和数据
    isEditing.value = false;
    editableMember.value = { ...props.member }; // 创建一个可编辑的副本
    errorMessage.value = '';
  }
});

// 5. 定义各种方法
function close() {
  emit('close');
}

function startEditing() {
  isEditing.value = true;
}

function cancelEditing() {
  isEditing.value = false;
  editableMember.value = { ...props.member }; // 恢复为原始数据
  errorMessage.value = '';
}

async function saveChanges() {
  if (!editableMember.value) return;
  isSaving.value = true;
  errorMessage.value = '';
  try {
    const { id, name, created_at, updated_at, ...updateData } = editableMember.value;
    await apiClient.patch(`/members/${id}`, updateData);
    isEditing.value = false;
    emit('member-updated'); // 通知父组件数据已更新
    // 直接在保存成功后立即关闭弹窗
    close();
  } catch (error) {
    errorMessage.value = `保存失败: ${error.response?.data?.detail || '未知错误'}`;
    console.error(error);
  } finally {
    isSaving.value = false;
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
  box-sizing: border-box;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-content {
  background-color: var(--main-bg-color);
  padding: 2rem 3rem;
  border: 1px solid var(--border-color);
  width: 90%;
  max-width: 500px;
  position: relative;
  text-align: center;
}

.modal-close-button {
  position: absolute;
  top: 10px;
  right: 15px;
  background: none;
  border: none;
  font-size: 2rem;
  color: var(--link-color);
  cursor: pointer;
}

:deep(.modal-avatar) {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  margin-bottom: 1rem;
}

.modal-bio {
  margin: 1.5rem 0;
  text-align: left;
  line-height: 1.7;
  color: var(--main-text-color);
  white-space: pre-wrap; /* 保留换行和空格 */
}

.edit-button {
  margin-top: 1.5rem;
}

.edit-form .form-group {
  text-align: left;
  margin-bottom: 1rem;
}

.edit-form .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--link-color);
}

.edit-form .form-group input,
.edit-form .form-group textarea {
  width: 100%;
  box-sizing: border-box;
  /* 继承 main.css 的输入框样式 */
  background-color: rgba(0, 0, 0, 0.2);
  font-family: var(--font-main);
  border: 1px solid var(--border-color);
  color: var(--main-text-color);
  padding: 8px 10px;
}

.edit-form .form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.api-button.secondary {
  background-color: transparent;
  border-color: var(--border-color);
  color: var(--main-text-color);
}

.api-button.secondary:hover {
  background-color: var(--border-color);
}

.message.error {
  color: var(--primary-accent-color);
  border: 1px dashed var(--primary-accent-color);
  padding: 0.5rem;
  margin-top: 1rem;
  font-size: 0.9em;
  text-align: center;
}
</style>