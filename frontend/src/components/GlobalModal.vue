<template>
  <transition name="modal-fade">
    <div v-if="modalStore.isOpen" class="modal-backdrop" @click.self="modalStore.handleCancel">
      <div class="modal-content" role="dialog" aria-modal="true" :aria-labelledby="modalTitleId">
        <header class="modal-header">
          <h2 :id="modalTitleId" class="modal-title">{{ modalStore.title }}</h2>
          <button @click="modalStore.handleCancel" class="modal-close-button" aria-label="关闭">&times;</button>
        </header>
        <section class="modal-body">
          <p>{{ modalStore.message }}</p>
        </section>
        <footer class="modal-footer">
          <button v-if="modalStore.isConfirmation" @click="modalStore.handleCancel" class="api-button secondary">
            取消
          </button>
          <button @click="modalStore.handleConfirm" class="api-button">
            确认
          </button>
        </footer>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { useModalStore } from '@/stores/modal';
import { computed } from 'vue';

const modalStore = useModalStore();
const modalTitleId = computed(() => `modal-title-${Date.now()}`);
</script>

<style scoped>
/* 样式与 MemberModal 类似，但更通用 */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}
.modal-content {
  background-color: var(--secondary-bg-color);
  border: 2px solid var(--border-color);
  box-shadow: 0 5px 15px rgba(0,0,0,0.5);
  width: 90%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
}
.modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-title {
  margin: 0;
  font-size: 1.25rem;
  color: var(--main-text-color);
}
.modal-close-button {
  background: none;
  border: none;
  font-size: 1.75rem;
  color: var(--link-color);
  cursor: pointer;
}
.modal-body {
  padding: 1.5rem;
  line-height: 1.6;
  color: var(--main-text-color);
  white-space: pre-wrap;
}
.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  background-color: var(--main-bg-color);
}
.api-button.secondary {
  background-color: transparent;
}

/* 过渡动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>