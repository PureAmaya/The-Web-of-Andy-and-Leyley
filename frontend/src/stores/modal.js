import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useModalStore = defineStore('modal', () => {
  const isOpen = ref(false);
  const title = ref('');
  const message = ref('');
  const isConfirmation = ref(false); // true for confirm, false for alert

  // 这个 promise a+ resolve 函数是关键
  let resolvePromise = null;

  function show(options) {
    isOpen.value = true;
    title.value = options.title || '提示';
    message.value = options.message || '';
    isConfirmation.value = options.isConfirmation || false;

    // 返回一个Promise，它的resolve函数被保存起来，等待用户操作后调用
    return new Promise((resolve) => {
      resolvePromise = resolve;
    });
  }

  function handleConfirm() {
    if (resolvePromise) {
      resolvePromise(true);
    }
    reset();
  }

  function handleCancel() {
    if (resolvePromise) {
      resolvePromise(false);
    }
    reset();
  }

  function reset() {
    isOpen.value = false;
    title.value = '';
    message.value = '';
    isConfirmation.value = false;
    resolvePromise = null;
  }

  return {
    isOpen, title, message, isConfirmation,
    show, handleConfirm, handleCancel
  };
});