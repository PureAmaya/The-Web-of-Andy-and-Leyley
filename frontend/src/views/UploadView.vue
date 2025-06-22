<template>
  <div class="upload-view">
    <div class="upload-form-container">
      <h2>上传新的画廊作品</h2>
      <form @submit.prevent="handleFileUpload">
        <div class="form-group">
          <label for="title">作品标题:</label>
          <input type="text" id="title" v-model="title" required/>
        </div>

        <div class="form-group">
          <label for="description">作品描述 (可选):</label>
          <textarea id="description" v-model="description" rows="4"></textarea>
        </div>

        <div class="form-group">
          <label for="builder-name">创作者 (成员名称):</label>
          <input type="text" id="builder-name" v-model="builderName" required list="members-list" autocomplete="off"/>
          <datalist id="members-list">
            <option v-for="member in existingMembers" :key="member.id" :value="member.name"></option>
          </datalist>
        </div>

        <div class="form-group">
          <label for="image-file">选择图片文件:</label>
          <input type="file" id="image-file" @change="onFileSelected" accept="image/jpeg, image/png, image/gif"
                 required/>
          <div v-if="filePreviewUrl" class="image-preview-container">
            <p>图片预览:</p>
            <img :src="filePreviewUrl" alt="图片预览" class="image-preview"/>
          </div>
          <p v-if="fileError" class="validation-error">{{ fileError }}</p>
        </div>

        <button type="submit" class="form-button" :disabled="isLoading || !selectedFile">
          {{ isLoading ? '上传中...' : '上传作品' }}
        </button>

        <p v-if="uploadMessage" :class="['message', uploadStatus]">{{ uploadMessage }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'; // 确保导入 onMounted
import {useAuthStore} from '@/stores/auth';
import {useSettingsStore} from '@/stores/settings';
import {useRouter} from 'vue-router';

const authStore = useAuthStore();
const settingsStore = useSettingsStore();
const router = useRouter();

const title = ref('');
const description = ref('');
const builderName = ref(''); // 新增：创作者名称
const existingMembers = ref([]); // 新增：用于存放成员列表
const selectedFile = ref(null);
const filePreviewUrl = ref('');
const fileError = ref('');

const isLoading = ref(false);
const uploadMessage = ref('');
const uploadStatus = ref(''); // 'success' or 'error'

const MAX_FILE_SIZE_MB = 5; // 与后端配置一致
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
const ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/gif"]; // 与后端配置一致

// 组件挂载时获取成员列表，为创作者输入框提供建议
onMounted(async () => {
  try {
    const response = await fetch(`${settingsStore.apiBaseUrl}/members`); // 调用获取所有成员的接口
    if (response.ok) {
      existingMembers.value = await response.json();
    } else {
      console.error("无法加载成员列表");
    }
  } catch (err) {
    console.error("获取成员列表失败:", err);
  }
});


function onFileSelected(event) {
  const file = event.target.files[0];
  fileError.value = '';
  filePreviewUrl.value = '';
  selectedFile.value = null;

  if (!file) {
    return;
  }

  // 客户端文件类型校验
  if (!ALLOWED_MIME_TYPES.includes(file.type)) {
    fileError.value = `不支持的文件类型。请上传 JPG, PNG, 或 GIF 格式的图片。`;
    return;
  }

  // 客户端文件大小校验
  if (file.size > MAX_FILE_SIZE_BYTES) {
    fileError.value = `文件过大，最大允许 ${MAX_FILE_SIZE_MB}MB。`;
    return;
  }

  selectedFile.value = file;

  // 生成本地预览 URL
  const reader = new FileReader();
  reader.onload = (e) => {
    filePreviewUrl.value = e.target.result;
  };
  reader.readAsDataURL(file);
}

async function handleFileUpload() {
  if (!selectedFile.value || fileError.value || !builderName.value) {
    uploadMessage.value = '请选择有效的文件并填写所有必填信息。';
    uploadStatus.value = 'error';
    return;
  }
  if (!authStore.isLoggedIn || !authStore.accessToken) {
    uploadMessage.value = '请先登录后再上传作品。';
    uploadStatus.value = 'error';
    router.push({name: 'login', query: {redirect: '/upload'}});
    return;
  }

  isLoading.value = true;
  uploadMessage.value = '';
  uploadStatus.value = '';

  const formData = new FormData();
  formData.append('title', title.value);
  formData.append('builder_name', builderName.value); // 添加创作者名称
  if (description.value) {
    formData.append('description', description.value);
  }
  formData.append('image', selectedFile.value); // 'image' 对应后端 UploadFile 的参数名

  try {
    const response = await fetch(`${settingsStore.apiBaseUrl}/gallery/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
      },
      body: formData,
    });

    const data = await response.json();

    if (response.ok) { // HTTP 201 Created
      uploadMessage.value = `作品 "${data.title}" 上传成功！`;
      uploadStatus.value = 'success';
      // 清空表单
      title.value = '';
      description.value = '';
      builderName.value = '';
      selectedFile.value = null;
      filePreviewUrl.value = '';
      document.getElementById('image-file').value = null;

    } else {
      uploadMessage.value = data.detail || '上传失败，请重试。';
      uploadStatus.value = 'error';
    }
  } catch (err) {
    console.error('上传请求失败:', err);
    uploadMessage.value = '网络错误或服务器无响应，请稍后重试。';
    uploadStatus.value = 'error';
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
/* 样式与 RegisterView/LoginView 类似，可以复用或调整 */
.upload-view {
  display: flex;
  justify-content: center;
  align-items: flex-start; /* 改为 flex-start */
  padding: 30px 20px;
  min-height: calc(100vh - 160px);
  box-sizing: border-box;
}


.upload-form-container h2 {
  text-align: center;
  color: var(--main-text-color);
  margin-bottom: 30px;
  font-size: 1.8em;
  font-weight: normal;
  /* font-family: var(--font-pixel, var(--font-main)); */
}

.upload-form-container {
  background-color: var(--main-bg-color); /* 使用主背景色，使其与内容区融为一体 */
  border: 2px solid var(--border-color);
  box-shadow: none; /* 移除阴影 */
  padding: 2rem;
}

.form-group label {
  font-family: var(--font-special), cursive; /* 标签使用特殊字体 */
  color: var(--link-color);
}

.form-group input, .form-group textarea {
  background-color: rgba(0, 0, 0, 0.2); /* 输入框有半透明的深色背景 */
  font-family: var(--font-main); /* 输入内容使用正文字体 */
  border-color: var(--border-color);
}


.form-group {
  margin-bottom: 20px;
}


.image-preview-container {
  margin-top: 15px;
  border: 1px dashed var(--border-color);
  padding: 10px;
  text-align: center;
}

.image-preview-container p {
  margin-bottom: 10px;
  font-size: 0.9em;
  color: var(--main-text-color);
}

.image-preview {
  max-width: 100%;
  max-height: 250px; /* 限制预览图高度 */
  border: 1px solid var(--border-color);
}

.form-button {
  /* 继承自 main.css */
  width: 100%;
  padding: 12px 20px;
  font-size: 1.1em;
  background-color: var(--primary-accent-color); /* 上传按钮使用强调色 */
  border-color: #600000;
  color: var(--button-text-color);
}

.form-button:hover:not(:disabled) {
  background-color: #600000;
  border-color: #400000;
}

.validation-error {
  color: var(--primary-accent-color);
  font-size: 0.85em;
  margin-top: 5px;
}

/* message 样式继承自 main.css */
</style>