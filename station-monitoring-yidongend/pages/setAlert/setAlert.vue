<template>
  <view>
    <view class="alert-container">
      <!-- 空状态优化：增加样式和提示 -->
      <uv-empty
          text="请先选择设备"
          marginTop="80px"
          v-if="!facilitiesStore.currentFacility"
      ></uv-empty>

      <!-- 无报警数据时的空状态 -->
      <uv-empty
          text="暂无报警设置数据"
          marginTop="80px"
          v-else-if="!alertSettingStore.alarmData || alertSettingStore.alarmData.length === 0"
      ></uv-empty>

      <!-- 报警设置列表 -->
      <view v-else class="alertItem" v-for="(item, index) in alertSettingStore.alarmData" :key="index">
        <setAlertItem
            :label="item.label"
            :modelValue="item.value"
            @update:modelValue="debouncedUpdateWarningSetting(item.type, $event)"
        />
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { onPullDownRefresh } from '@dcloudio/uni-app';
import { useAlertSettingStore } from '@/store/alertSetting.js';
import { setalert } from '../../api/alert';
import { useFacilitiesStore } from '@/store/facilities';
import UvEmpty from "../../uni_modules/uv-empty/components/uv-empty/uv-empty.vue";
import SetAlertItem from "../../components/setAlertItem/setAlertItem.vue";

// 初始化 store
const alertSettingStore = useAlertSettingStore();
const facilitiesStore = useFacilitiesStore();

// 防抖函数（优化：增加立即执行判断，避免首次延迟）
function debounce(func, wait, immediate = false) {
  let timeout;
  return function (...args) {
    const context = this;
    clearTimeout(timeout);
    if (immediate && !timeout) {
      func.apply(context, args);
    } else {
      timeout = setTimeout(() => {
        func.apply(context, args);
      }, wait);
    }
  };
}

// 更新警报设置的方法（增加错误捕获）
async function updateWarningSetting(type, newSettings) {
  // 校验设备是否存在
  if (!facilitiesStore.currentFacility?.id) {
    uni.showToast({ title: '请先选择设备', icon: 'none' });
    return;
  }

  try {
    let data = {
      maxValue: newSettings.settings[1]?.value || 0,
      minValue: newSettings.settings[0]?.value || 0,
      warningPeriod: newSettings.warningPeriod || '08:00-22:00',
      type,
      cid: facilitiesStore.currentFacility.id,
      enable: newSettings.enabled || false,
      alarmThreshold: newSettings.settings[2]?.value || 0
    };
    // 发送更新请求
    let res = await setalert(data);
    if (res.code === 0) { // 假设接口返回code=0为成功
      uni.showToast({ title: '设置成功', icon: 'success' });
    }
    // 重新拉取数据
    await alertSettingStore.fetchData({
      cid: facilitiesStore.currentFacility.id
    });
  } catch (error) {
    console.error('更新警报设置失败：', error);
    uni.showToast({ title: '设置失败，请重试', icon: 'none' });
  }
}

// 创建防抖后的更新函数（缩短防抖时间，增加立即执行）
const debouncedUpdateWarningSetting = debounce(updateWarningSetting, 1000, false);

// 初始化数据（增加校验和加载提示）
async function init() {
  if (!facilitiesStore.currentFacility?.id) {
    console.warn('未选择设备，无法加载报警设置');
    return;
  }

  uni.showLoading({ title: '加载中...' });
  try {
    await alertSettingStore.fetchData({
      cid: facilitiesStore.currentFacility.id
    });
  } catch (error) {
    console.error('加载报警设置失败：', error);
    uni.showToast({ title: '加载失败，请重试', icon: 'none' });
  } finally {
    uni.hideLoading();
  }
}

// 监听下拉刷新事件
onPullDownRefresh(async () => {
  await init();
  uni.stopPullDownRefresh();
});

// 页面挂载后初始化（确保store已加载）
onMounted(() => {
  // 延迟执行，确保store数据已初始化
  setTimeout(() => {
    init();
  }, 300);
});
</script>

<style scoped>
.alert-container {
  padding: 10px;
  box-sizing: border-box;
}
.alertItem {
  margin-bottom: 15px;
}
</style>