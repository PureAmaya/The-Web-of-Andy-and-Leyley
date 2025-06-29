import { useModalStore } from '@/stores/modal';

/**
 * 显示一个确认对话框
 * @param {string} message - 对话框中显示的消息.
 * @param {string} [title='确认操作'] - 对话框的标题.
 * @returns {Promise<boolean>} - 用户点击确认返回true, 点击取消返回false.
 */
export function confirmDialog(message, title = '确认操作') {
  const modalStore = useModalStore();
  return modalStore.show({
    title,
    message,
    isConfirmation: true,
  });
}

/**
 * 显示一个提示对话框
 * @param {string} message - 对话框中显示的消息.
 * @param {string} [title='提示'] - 对话框的标题.
 * @returns {Promise<boolean>} - 用户点击确定后返回true.
 */
export function alertDialog(message, title = '提示') {
  const modalStore = useModalStore();
  return modalStore.show({
    title,
    message,
    isConfirmation: false,
  });
}