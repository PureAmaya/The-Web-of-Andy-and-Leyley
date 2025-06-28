<template>
  <img :src="imageSrc" :alt="alt" @error="handleError" />
</template>

<script setup>
import { ref, watch, defineProps } from 'vue';
import { useSettingsStore } from '@/stores/settings';
import { getFullImageUrl } from '@/utils/imageUtils';

const props = defineProps({
  relativeUrl: {
    type: String,
    default: null
  },
  name: {
    type: String,
    default: null
  },
  alt: {
    type: String,
    default: 'Avatar'
  }
});

const settingsStore = useSettingsStore();

// 内部状态，存储当前要显示的图片URL
const imageSrc = ref('');
// 记录是否已经尝试过备用方案，防止无限循环的错误
const hasFallenBack = ref(false);

// 当外部传入的属性变化时，重新计算图片URL
watch(() => [props.relativeUrl, props.name], () => {
  // 重置状态
  hasFallenBack.value = false;
  // 使用我们之前创建的工具函数来获取主头像URL
  imageSrc.value = getFullImageUrl(props.relativeUrl, props.name, settingsStore.apiBaseUrl);
}, { immediate: true }); // immediate: true 确保组件一加载就执行

// 当主头像加载失败时触发此函数
function handleError() {
  // 如果尚未尝试过备用方案，并且有一个名字可以用来生成随机头像
  if (!hasFallenBack.value && props.name) {
    // 标记为已尝试，防止死循环
    hasFallenBack.value = true;
    // 设置为备用的随机头像URL
    imageSrc.value = `https://cravatar.cn/avatar/${props.name}?d=identicon&s=128`;
  }
}
</script>