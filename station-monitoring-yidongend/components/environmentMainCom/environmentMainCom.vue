<template>
  <view class="page-wrapper">
    <!-- 标题区域 -->
    <view class="title-area">
      <view class="title">环境监测</view>
      <view class="sub-title">AI环境管家 · 实时感知</view>
      <view class="status-indicator">
        <uv-icon name="eye" size="18" color="#38963C"></uv-icon>
<!--        <text class="status-text">实时监控中</text>-->
        <view class="status-dot"></view>
      </view>
    </view>

    <!-- 环境卡片网格 - 改为单列竖排 -->
    <view class="grid-container">
      <view
          class="card-wrapper"
          v-for="(item, index) in sensorData"
          :key="item.title"
          :style="{ animationDelay: `${index * 0.1}s` }"
          @touchstart="handleCardTouch(index)"
          @touchend="handleCardTouchEnd"
      >
        <gridCardItem
            :sensor="item"
            :class="{ 'card-active': activeCardIndex === index }"
            class="animated-card"
        />

        <!-- 环境状态标签 -->
        <view class="environment-label" :style="{ backgroundColor: getLabelColor(item.type) }">
          {{ getLabelText(item.type) }}
        </view>
      </view>
    </view>

    <!-- 环境数据汇总 - 改为竖排 -->
    <view class="summary-card" v-if="sensorData.length > 0">
      <view class="summary-header">
        <uv-icon name="bar-chart" size="20" color="#38963C"></uv-icon>
        <text class="summary-title">环境数据概览</text>
      </view>
      <view class="summary-content">
        <view class="summary-item" v-for="item in sensorData" :key="item.type">
          <view class="summary-label">
            <uv-icon :name="getIconName(item.type)" size="16" :color="getIconColor(item.type)"></uv-icon>
            <text class="label-text">{{ item.title }}</text>
          </view>
          <view class="summary-value">
            <text class="value-text">{{ formatValue(item.value, item.unit) }}</text>
            <text class="unit-text">{{ item.unit }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-if="sensorData.length === 0">
      <view class="empty-illustration">
        <uv-icon name="home" size="64" color="#C8C7CC"></uv-icon>
        <view class="empty-wave"></view>
      </view>
      <text class="empty-title">暂无环境数据</text>
      <text class="empty-subtitle">请确保环境传感器已连接</text>
      <view class="empty-action">
        <uv-button
            size="small"
            type="primary"
            plain
            shape="circle"
            @click="handleRefresh"
        >
          <uv-icon name="reload" size="14"></uv-icon>
          重新检测
        </uv-button>
      </view>
    </view>

    <!-- 底部提示 -->
<!--    <view class="bottom-tips">-->
<!--      <uv-icon name="info-circle" size="14" color="#8E8E93"></uv-icon>-->
<!--      <text class="tips-text">数据每5分钟自动更新 · 保持设备连接</text>-->
<!--    </view>-->

    <!-- 装饰性元素 -->
    <view class="decoration">
      <view class="wave wave-1"></view>
      <view class="wave wave-2"></view>
      <view class="dot dot-1"></view>
      <view class="dot dot-2"></view>
    </view>
  </view>
</template>

<script setup>
import {
  computed,
  ref,
  onMounted
} from 'vue';
import { useEnvironmentStore } from '@/store/environmentData.js'
const environmentStore = useEnvironmentStore()

let activeCardIndex = ref(-1)
let lastUpdateTime = ref(new Date())

let sensorData = computed(() => {
  return environmentStore.sensorData.filter(filterEnvironmentData)
})

function filterEnvironmentData(item) {
  return item.type === 'guang1' || item.type === 'humidity' || item.type === 'yanwu' || item.type === 'temp'
}

// 卡片触摸交互
function handleCardTouch(index) {
  activeCardIndex.value = index
}

function handleCardTouchEnd() {
  setTimeout(() => {
    activeCardIndex.value = -1
  }, 150)
}

// 刷新数据
function handleRefresh() {
  // 这里可以添加实际的数据刷新逻辑
  lastUpdateTime.value = new Date()

  // 模拟刷新效果
  const temp = activeCardIndex.value
  activeCardIndex.value = -1
  setTimeout(() => {
    activeCardIndex.value = temp
  }, 300)
}

// 根据传感器类型获取标签颜色
function getLabelColor(type) {
  const colors = {
    'temp': 'rgba(255, 114, 75, 0.15)',
    'humidity': 'rgba(91, 206, 189, 0.15)',
    'guang1': 'rgba(100, 103, 210, 0.15)',
    'yanwu': 'rgba(251, 19, 116, 0.15)'
  }
  return colors[type] || 'rgba(56, 150, 60, 0.15)'
}

// 根据传感器类型获取标签文本
function getLabelText(type) {
  const labels = {
    'temp': '温度',
    'humidity': '湿度',
    'guang1': '光照',
    'yanwu': '烟雾'
  }
  return labels[type] || '环境'
}

// 根据传感器类型获取图标
function getIconName(type) {
  const icons = {
    'temp': 'thermometer',
    'humidity': 'droplet',
    'guang1': 'sun',
    'yanwu': 'alert-circle'
  }
  return icons[type] || 'activity'
}

// 根据传感器类型获取图标颜色
function getIconColor(type) {
  const colors = {
    'temp': '#FF724B',
    'humidity': '#5BCEBD',
    'guang1': '#6467D2',
    'yanwu': '#FB1374'
  }
  return colors[type] || '#38963C'
}

// 格式化显示值
function formatValue(value, unit) {
  if (typeof value === 'number') {
    return value.toFixed(1)
  }
  return value
}

// 模拟数据更新
onMounted(() => {
  // 可以在这里添加定时更新逻辑
})
</script>

<style scoped lang="scss">
$primary-color: #38963C;
$primary-light: rgba(56, 150, 60, 0.1);
$primary-gradient: linear-gradient(135deg, #38963C 0%, #5BCEBD 100%);
$card-shadow: 0 8px 32px rgba(56, 150, 60, 0.12);
$card-shadow-active: 0 12px 48px rgba(56, 150, 60, 0.2);
$border-radius: 20px;
$transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

.page-wrapper {
  padding: 16px;
  background: linear-gradient(180deg, #F8F9FA 0%, #FFFFFF 100%);
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

// 标题区域
.title-area {
  padding: 20px 0 24px;
  animation: fadeInDown 0.6s ease-out;

  .title {
    font-size: 28px;
    font-weight: 800;
    color: #1D1D1F;
    line-height: 1.2;
    margin-bottom: 8px;
    background: $primary-gradient;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .sub-title {
    font-size: 14px;
    color: #8E8E93;
    font-weight: 400;
    margin-bottom: 12px;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(56, 150, 60, 0.08);
    padding: 6px 12px;
    border-radius: 16px;
    display: inline-flex;

    .status-text {
      font-size: 12px;
      color: $primary-color;
      font-weight: 500;
    }

    .status-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: $primary-color;
      animation: pulse 1.5s ease-in-out infinite;
    }
  }
}

// 网格容器 - 改为单列
.grid-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

// 卡片包装器
.card-wrapper {
  position: relative;
  animation: slideInUp 0.6s ease-out both;

  .animated-card {
    transition: $transition;

    :deep(.grid-card-item) {
      border-radius: $border-radius;
      overflow: hidden;
      box-shadow: $card-shadow;
      transition: $transition;
      position: relative;
      z-index: 1;

      &.card-active {
        transform: scale(0.98);
        box-shadow: 0 4px 16px rgba(56, 150, 60, 0.15);
      }

      &:hover {
        transform: translateY(-4px);
        box-shadow: $card-shadow-active;
      }
    }
  }

  .environment-label {
    position: absolute;
    top: -6px;
    right: 12px;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: 600;
    color: $primary-color;
    z-index: 2;
    backdrop-filter: blur(4px);
    animation: fadeIn 0.5s ease-out;
  }
}

// 汇总卡片 - 改为竖排
.summary-card {
  background: white;
  border-radius: $border-radius;
  padding: 20px;
  box-shadow: $card-shadow;
  margin-bottom: 24px;
  animation: slideInUp 0.6s ease-out 0.3s both;
  border: 1px solid rgba(56, 150, 60, 0.08);

  .summary-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;

    .summary-title {
      font-size: 16px;
      font-weight: 600;
      color: #1D1D1F;
    }
  }

  .summary-content {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .summary-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;

      &:not(:last-child) {
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
      }

      .summary-label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        color: #666;

        .label-text {
          min-width: 80px;
        }
      }

      .summary-value {
        display: flex;
        align-items: baseline;
        gap: 4px;

        .value-text {
          font-size: 18px;
          font-weight: 700;
          color: #1D1D1F;
        }

        .unit-text {
          font-size: 12px;
          color: #8E8E93;
        }
      }
    }
  }
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  animation: fadeIn 0.6s ease-out;

  .empty-illustration {
    position: relative;
    margin-bottom: 20px;

    .empty-wave {
      position: absolute;
      bottom: -10px;
      left: 50%;
      transform: translateX(-50%);
      width: 80px;
      height: 4px;
      background: linear-gradient(90deg, transparent, $primary-color, transparent);
      border-radius: 2px;
      animation: wave 2s ease-in-out infinite;
    }
  }

  .empty-title {
    font-size: 18px;
    color: #1D1D1F;
    font-weight: 600;
    margin-bottom: 8px;
  }

  .empty-subtitle {
    font-size: 14px;
    color: #8E8E93;
    margin-bottom: 24px;
  }

  .empty-action {
    margin-top: 8px;
  }
}

// 底部提示
.bottom-tips {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  background: rgba(248, 249, 250, 0.8);
  border-radius: 16px;
  margin-top: 20px;
  animation: fadeIn 0.6s ease-out 0.6s both;

  .tips-text {
    font-size: 12px;
    color: #8E8E93;
  }
}

// 装饰性元素
.decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;

  .wave {
    position: absolute;
    border-radius: 50%;
    background: $primary-light;

    &.wave-1 {
      width: 200px;
      height: 200px;
      top: -100px;
      right: -100px;
      opacity: 0.3;
      animation: float 20s ease-in-out infinite;
    }

    &.wave-2 {
      width: 150px;
      height: 150px;
      bottom: -75px;
      left: -75px;
      opacity: 0.2;
      animation: float 25s ease-in-out infinite reverse;
    }
  }

  .dot {
    position: absolute;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: $primary-color;
    opacity: 0.1;

    &.dot-1 {
      top: 30%;
      left: 20%;
    }

    &.dot-2 {
      bottom: 40%;
      right: 15%;
    }
  }
}

// 动画定义
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(0.8);
  }
}

@keyframes wave {
  0%, 100% {
    transform: translateX(-50%) scaleX(1);
  }
  50% {
    transform: translateX(-50%) scaleX(0.8);
  }
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  33% {
    transform: translate(30px, -20px) rotate(120deg);
  }
  66% {
    transform: translate(-20px, 15px) rotate(240deg);
  }
}

// 响应式调整
@media (max-width: 768px) {
  .page-wrapper {
    padding: 12px;
  }

  .title-area {
    padding: 16px 0 20px;

    .title {
      font-size: 24px;
    }
  }

  .grid-container {
    gap: 14px;
  }

  .summary-card {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .page-wrapper {
    padding: 10px;
  }

  .title-area {
    .title {
      font-size: 22px;
    }

    .sub-title {
      font-size: 13px;
    }
  }

  .grid-container {
    gap: 12px;
  }

  .summary-card {
    padding: 14px;

    .summary-content {
      .summary-item {
        .summary-label {
          .label-text {
            min-width: 70px;
          }
        }

        .summary-value {
          .value-text {
            font-size: 16px;
          }
        }
      }
    }
  }
}

@media (max-width: 375px) {
  .page-wrapper {
    padding: 8px;
  }

  .title-area {
    padding: 12px 0 16px;

    .title {
      font-size: 20px;
    }

    .status-indicator {
      padding: 4px 10px;
    }
  }

  .grid-container {
    gap: 10px;
  }

  .summary-card {
    padding: 12px;

    .summary-content {
      gap: 12px;

      .summary-item {
        padding: 10px 0;

        .summary-label {
          .label-text {
            min-width: 60px;
            font-size: 13px;
          }
        }

        .summary-value {
          .value-text {
            font-size: 15px;
          }
        }
      }
    }
  }

  .empty-state {
    padding: 40px 16px;
  }
}

@media (min-width: 1024px) {
  .page-wrapper {
    max-width: 600px;
    margin: 0 auto;
  }
}

@media (min-width: 768px) {
  .grid-container {
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
  }

  .summary-card {
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
  }
}
</style>