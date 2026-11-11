<template>
  <view>
    <uv-toast ref="toast"></uv-toast>
  </view>
</template>

<script setup>
import { ref } from 'vue';

const toast = ref(null);

const showToast = (options) => {
  toast.value.show({
    type: options.type || 'info',
    title: options.title || '提示',
    message: options.message || ''
  });
};

const hideToast = () => {
  toast.value.hide();
};
</script>

<style lang="scss">
/* 添加样式 */
</style>
