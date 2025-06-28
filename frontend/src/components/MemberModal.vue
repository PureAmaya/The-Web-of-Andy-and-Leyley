<template>
  <div v-if="isOpen" class="modal-backdrop" @click="close">
    <div class="modal-content" @click.stop>
      <template v-if="member">
        <button class="modal-close-button" @click="close">&times;</button>
        <Avatar
          :relativeUrl="member.avatar_url"
          :name="member.name"
          :alt="member.name"
          class="modal-avatar"
        />
        <h2>{{ member.name }}</h2>
        <h4>{{ member.role }}</h4>
        <p class="modal-bio">{{ member.bio }}</p>
      </template>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import Avatar from './Avatar.vue';

// 定义组件接收的属性
defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  member: {
    type: Object,
    default: null
  }
});

// 定义组件可以发出的事件
const emit = defineEmits(['close']);


// 关闭弹窗的函数
function close() {
  emit('close');
}
</script>

<style scoped>

:deep(.modal-avatar) {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  margin-bottom: 1rem;
}


/* 这里是所有从 HomeView 移动过来的弹窗样式 */
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

.modal-avatar {
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
}
</style>