<template>
  <view>
    <view class="facility" @click="picker.open()">
      <text style="font-size: 12px; font-weight: 800;">当前设备:</text>
      <view class="facility-input input">
        <text class="facility-input-text">{{facility}}</text>
      </view>
    </view>
    <uv-picker
        ref="picker"
        :columns="[columns]"
        @confirm="confirm"
        v-if="facilitiesStore.bought_facilities && facilitiesStore.bought_facilities.length > 0"
    ></uv-picker>
  </view>
</template>

<script setup>
import {
  ref,
  computed,
  onMounted
} from 'vue'

import {
  useFacilitiesStore
} from '../../store/facilities'
import { useAlertSettingStore } from '../../store/alertSetting';
import UvPicker from "../../uni_modules/uv-picker/components/uv-picker/uv-picker.vue";

const facilitiesStore = useFacilitiesStore()
const alertSettingStore = useAlertSettingStore()
let picker = ref(null)

// 保持原来的 columns
let columns = computed(() => {
  return facilitiesStore.bought_facilities.map((item) => {
    return item.name
  })
})

let facility = computed(() => {
  if(facilitiesStore.bought_facilities.length===0)
    return '请先在"我的-设备管理"里购买设备'
  return facilitiesStore.currentFacility?.name?? '请先选择你的设备'
})

function confirm(e) {
  console.log('=== PICKER DEBUG START ===')
  console.log('Full event object:', e)
  console.log('Event type:', typeof e)
  console.log('Event keys:', Object.keys(e))

  // 尝试不同的访问方式
  console.log('e.value:', e.value)
  console.log('e.value[0]:', e.value?.[0])
  console.log('e.index:', e.index)
  console.log('e.index[0]:', e.index?.[0])

  // 检查所有的属性
  for (let key in e) {
    console.log(`e.${key}:`, e[key])
  }

  console.log('=== PICKER DEBUG END ===')

  // 先用最简单的逻辑测试
  let selectedValue;

  // 方法1：如果 e 直接是选中的值
  if (typeof e === 'string') {
    selectedValue = e
  }
  // 方法2：如果 e.value 是数组
  else if (Array.isArray(e.value)) {
    selectedValue = e.value[0]
  }
  // 方法3：如果 e.value 是字符串
  else if (typeof e.value === 'string') {
    selectedValue = e.value
  }
  // 方法4：如果 e 有 detail 属性（常见于小程序事件）
  else if (e.detail && e.detail.value) {
    selectedValue = Array.isArray(e.detail.value) ? e.detail.value[0] : e.detail.value
  }

  console.log('Selected value after parsing:', selectedValue)

  if (!selectedValue) {
    console.error('无法获取选中的值')
    uni.showToast({
      title: '选择失败',
      icon: 'error'
    })
    return
  }

  // 直接查找设备
  let obj = facilitiesStore.bought_facilities.find((item) => {
    return item.name === selectedValue
  })

  console.log('Found device:', obj)

  if (obj && obj.id) {
    // 设置当前设备
    facilitiesStore.setCurrentFacility(obj)
    // 获取当前设备的告警设置
    alertSettingStore.fetchData({
      cid: obj.id
    })

    // 显示成功提示
    uni.showToast({
      title: `已选择设备: ${obj.name}`,
      icon: 'success'
    })
  } else {
    console.error('Device not found or has no id:', obj)
    uni.showToast({
      title: '选择设备失败',
      icon: 'error'
    })
  }
}

// 只在有当前设备时调用
if(facilitiesStore.currentFacility && facilitiesStore.currentFacility.id){
  let id = facilitiesStore.currentFacility.id
  alertSettingStore.fetchData({
    cid: id
  })
}
</script>

<style scoped lang="scss">
.facility {
  display: flex;
  justify-content: flex-start;
  align-items: center;

  .facility-input {
    padding:0 10px;
    font-size: 12px;
    width: auto;
    height: 20px;
    display: flex;
    align-items: center;
    margin-left: 10px;
    .facility-input-text{
      color:#666;
      display: block;
      overflow: hidden;
    }
  }
}
</style>