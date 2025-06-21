/**
 * 将 ISO 格式的日期字符串格式化为更易读的本地化日期时间格式。
 * @param {string} dateString - 等待格式化的日期字符串 (例如 "2025-06-21T17:10:08.924879")。
 * @returns {string} 格式化后的日期字符串，如果输入无效则返回 'N/A'。
 */
export function formatDate(dateString) {
  if (!dateString) {
    return 'N/A';
  }

  try {
    const options = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false // 您可以根据喜好设为 true 或 false
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
  } catch (error) {
    console.error("日期格式化失败:", error);
    return '无效日期';
  }
}

