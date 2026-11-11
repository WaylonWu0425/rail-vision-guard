<template>
  <view class="container">
    <text class="title">设备管理</text>

    <!-- 可购买的设备 -->
    <view class="section">
      <text class="subtitle">可购买的设备</text>
      <uv-list>
        <uv-list-item
            v-for="device in buy_facilities"
            :key="device.id"
            :title="device.name"
            :note="'￥' + device.price"
            thumb="https://vkceyugu.cdn.bspapp.com/VKCEYUGU-dc-site/460d46d0-4fcc-11eb-8ff1-d5dcf8779628.png"
            thumb-size="lg"
            rightText="购买"
            :clickable="true"
            @click="purchaseDevice(device)"
        >
        </uv-list-item>
      </uv-list>
      <view v-if="buy_facilities.length === 0" class="empty-tip">
        <text>暂无可用设备</text>
      </view>
    </view>

    <!-- 用户已购买的设备 -->
    <view class="section">
      <text class="subtitle">用户已购买的设备</text>
      <uv-list>
        <uv-list-item
            v-for="device in bought_facilities"
            :key="device.id"
            :title="device.name"
            :note="'已购买'"
            thumb="https://vkceyugu.cdn.bspapp.com/VKCEYUGU-dc-site/460d46d0-4fcc-11eb-8ff1-d5dcf8779628.png"
            thumb-size="lg"
        >
          <template #footer>
            <uv-button @click="commitRepair(device)" type="">申请维修</uv-button>
            <uv-button @click="removeDevice(device)" type="error">移除</uv-button>
          </template>
        </uv-list-item>
      </uv-list>
      <view v-if="bought_facilities.length === 0" class="empty-tip">
        <text>暂无已购买设备</text>
      </view>
    </view>

    <uv-toast ref="toast"></uv-toast>
  </view>
</template>

<script setup>
import {
  onMounted,
  ref,
  computed
} from 'vue'
import {
  useFacilitiesStore,
} from '../../store/facilities';
import {repairFacilities} from '../../api/facilities';
import UvList from "../../uni_modules/uv-list/components/uv-list/uv-list.vue";
import UvListItem from "../../uni_modules/uv-list/components/uv-list-item/uv-list-item.vue";
import UvButton from "../../uni_modules/uv-button/components/uv-button/uv-button.vue";
import UvToast from "../../uni_modules/uv-toast/components/uv-toast/uv-toast.vue";

const toast = ref(null)
const facilitiesStore = useFacilitiesStore()

// 使用 computed 来获取响应式数据
const buy_facilities = computed(() => facilitiesStore.buy_facilities)
const bought_facilities = computed(() => facilitiesStore.bought_facilities)

// 添加一个变量来控制节流
const isPurchasing = ref(false)

// 添加加载状态
const loading = ref(false)

onMounted(async () => {
  console.log('开始加载设备数据...')
  loading.value = true

  try {
    // 同时加载已购买设备和可购买设备
    await Promise.all([
      facilitiesStore.fetchFacilities(),
      facilitiesStore.fetchBuyFacilities()
    ])
  } catch (err) {
    console.error('加载设备列表失败:', err)
  } finally {
    loading.value = false
  }
})

//判断有没有当前设备
function hasFacility(deviceName) {
  return bought_facilities.value.some(item => item.name === deviceName)
}

//购买设备
const purchaseDevice = async (device) => {
  // 如果已经在购买过程中，则直接返回
  if (isPurchasing.value) {
    return
  }

  // 检查用户是否已经拥有该设备
  if (hasFacility(device.name)) {
    uni.showToast({
      title: "您已购买此设备",
      icon: 'none'
    })
    return
  }

  try {
    isPurchasing.value = true
    toast.value.show({
      type: 'loading',
      title: '正在购买',
      message: "正在购买",
    })

    console.log('购买设备:', device)

    // 执行购买操作
    await facilitiesStore.purchaseFacility({
      id: device.id
    })

    toast.value.hide()
    uni.showToast({
      title: "购买成功",
      icon: 'success'
    })

    console.log('购买后 - 可购买设备:', buy_facilities.value)
    console.log('购买后 - 已购买设备:', bought_facilities.value)

  } catch (err) {
    console.error('购买失败:', err)
    toast.value.hide()
    uni.showToast({
      title: "购买失败",
      icon: 'error'
    })
  } finally {
    isPurchasing.value = false
  }
}

// 移除设备
const removeDevice = async (device) => {
  try {
    await facilitiesStore.removeFacility('' + device.id)
    uni.showToast({
      title: '移除成功',
      icon: 'success'
    })

    console.log('移除后 - 可购买设备:', buy_facilities.value)
    console.log('移除后 - 已购买设备:', bought_facilities.value)

  } catch (err) {
    console.error('移除失败:', err)
    uni.showToast({
      title: "移除失败",
      icon: 'error'
    })
  }
}

// 申请维修
async function commitRepair(device) {
  try {
    let res = await repairFacilities({
      id: device.id
    })

    uni.showToast({
      title: "申请成功",
      icon: 'success'
    })
  } catch (err) {
    console.error('申请维修失败:', err)
    uni.showToast({
      title: "申请失败",
      icon: 'error'
    })
  }
}
</script>

<style lang="scss" scoped>
.container {
  font-family: Arial, sans-serif;
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
  border-radius: 8px;
}

.title {
  color: #333;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;
  font-size: 20px;
}

.section {
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .subtitle {
    display: block;
    margin: 10px 0 15px 0;
    color: #333;
    font-weight: bold;
    font-size: 16px;
  }

  .uv-list-item {
    background-color: #fff;
    border: 1px solid #eee;
    border-radius: 6px;
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .empty-tip {
    text-align: center;
    padding: 20px;
    color: #999;
    font-size: 14px;
  }
}

.uv-button {
  margin-left: 8px;
}
</style>