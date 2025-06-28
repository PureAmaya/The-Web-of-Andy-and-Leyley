/**
 * 根据相对路径、名称和API基础URL，生成完整的图片或头像URL。
 * 优先级:
 * 1. 使用明确提供的相对URL (relativeUrl)。
 * 2. 如果没有，则使用名称 (name) 通过后端的MC头像代理获取头像。
 * 3. 如果都没有，则生成一个备用的identicon头像。
 * @param {string | null} relativeUrl - 数据库中存储的头像或图片的相对路径。
 * @param {string | null} name - 用于获取MC头像或作为生成identicon的种子。
 * @param {string} apiBaseUrl - 后端API的基础地址。
 * @returns {string} 最终的图片URL。
 */
export function getFullImageUrl(relativeUrl, name, apiBaseUrl) {
  // 优先级 1: 使用数据库中指定的 URL
  if (relativeUrl) {
    // 如果已经是完整的 http/https URL，直接返回
    if (relativeUrl.startsWith('http')) {
      return relativeUrl;
    }
    // 否则，与 apiBaseUrl 拼接
    return `${apiBaseUrl}${relativeUrl}`;
  }

  // 优先级 2: 使用 name 通过后端代理获取真实 MC 头像
  if (name) {
    return `${apiBaseUrl}/avatars/mc/${name}`;
  }

  // 优先级 3: 最终备选方案，生成一个 identicon
  return `https://cravatar.cn/avatar/placeholder?d=identicon&s=100`;
}