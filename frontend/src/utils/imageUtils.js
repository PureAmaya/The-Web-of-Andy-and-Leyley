/**
 * 根据相对路径、名称和API基础URL，生成完整的图片或头像URL。
 * 优先级:
 * 1. 使用明确提供的、非空的相对URL (relativeUrl)。
 * 2. 如果没有，则使用名称 (name) 通过后端的MC头像代理获取头像。
 * 3. 如果都没有，则返回一个统一的占位符图片。
 * @param {string | null | undefined} relativeUrl - 数据库中存储的头像或图片的相对路径。
 * @param {string | null | undefined} name - 用于获取MC头像。
 * @param {string} apiBaseUrl - 后端API的基础地址。
 * @returns {string} 最终的图片URL。
 */
export function getFullImageUrl(relativeUrl, name, apiBaseUrl) {
  // 优先级 1: 使用数据库中指定的 URL，并确保它不是一个空字符串
  if (relativeUrl && relativeUrl.trim() !== '') {
    // [核心修复] 如果是完整的 http/https 或 data URL，直接返回
    if (relativeUrl.startsWith('http') || relativeUrl.startsWith('data:')) {
      return relativeUrl;
    }
    // 否则，假定它是服务器上的相对路径，与 apiBaseUrl 拼接
    // 确保拼接处只有一个斜杠
    return `${apiBaseUrl.replace(/\/$/, '')}/${relativeUrl.replace(/^\//, '')}`;
  }

  // 优先级 2: 使用 name 通过后端代理获取真实 MC 头像
  if (name && name.trim() !== '') {
    return `${apiBaseUrl}/avatars/mc/${name}`;
  }

  // 优先级 3: 最终备选方案，返回一个本地的或网络的统一占位符
  // 您可以替换为您喜欢的任何占位符图片URL
  return '/placeholder-avatar.png';
}