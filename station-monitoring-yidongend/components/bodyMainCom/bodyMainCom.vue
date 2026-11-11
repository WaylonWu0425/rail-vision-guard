<template>
  <view class="container">
    <!-- 标题区域 -->
    <view class="title-area">
      <view class="title">今日健康报告</view>
      <view class="sub-title">AI健康管家 · 实时守护</view>
    </view>

    <!-- 预览区域 -->
    <view class="preview-wrapper">
      <view class="preview">
        <priview></priview>
      </view>
      <view class="preview-label">健康概览</view>
    </view>

    <!-- 标签页区域 -->
    <view class="tab-wrapper">
      <uv-tabs
          @change="changeDataNav"
          :activeStyle="{
					color: '#303133',
					fontWeight: 'bold',
					transform: 'scale(1.05)',
					transition: 'transform 0.2s ease'
				}"
          :inactiveStyle="{
					color: '#8E8E93',
					transition: 'color 0.2s ease'
				}"
          :lineColor="dataList.lineColor"
          :list="dataList.lineData"
          :scrollable="false"
          :lineWidth="40"
          :lineHeight="4"
          :itemStyle="{
					padding: '0 16px',
					height: '48px'
				}"
          class="custom-tabs"
      ></uv-tabs>
    </view>

    <!-- 数据卡片区域 -->
    <view class="tab-list">
      <view class="card-wrapper">
        <gridCardItem
            :sensor="currentData"
            :class="{'card-active': isCardActive}"
            @touchstart="handleCardTouchStart"
            @touchend="handleCardTouchEnd"
        ></gridCardItem>
      </view>

      <!-- 数据更新提示 -->
      <view class="update-indicator" v-if="showUpdateIndicator">
        <uv-icon name="checkmark-circle" color="#38963C" size="16"></uv-icon>
        <text class="update-text">数据已更新</text>
      </view>

      <!-- 空状态提示 -->
      <view class="empty-state" v-if="!currentData">
        <uv-icon name="list" size="48" color="#C8C7CC"></uv-icon>
        <text class="empty-text">暂无数据</text>
        <text class="empty-subtext">请确保设备已连接</text>
      </view>
    </view>

    <!-- 底部装饰 -->
    <view class="bottom-decoration">
      <view class="dot dot-1"></view>
      <view class="dot dot-2"></view>
      <view class="dot dot-3"></view>
    </view>
  </view>
</template>

<script setup>
import {
  computed,
  onMounted,
  ref,
  watchEffect
} from 'vue';
import { useEnvironmentStore } from '../../store/environmentData';

let current = ref('heart')
let dataStr = ref('')
const environmentStore = useEnvironmentStore()

// 卡片交互状态
let isCardActive = ref(false)
let showUpdateIndicator = ref(false)

let currentData = computed(() => {
  return environmentStore.sensorData.find(item => item.type === current.value)
})

function change(index) {
  current.value = index
}

// data导航栏
let dataList = ref({
  Index: null,
  lineColor: '#38963C',
  lineData: [{
    name: "心率",
    type: 'heart',
    color: "#FB1374",
  }, {
    name: "活动",
    type: 'move',
    color: "#6467D2",
  }, {
    name: "呼吸",
    type: "breath",
    color: "#5BCEBD",
  }, {
    name: "距离",
    type: "distance",
    color: "#38963C",
  }, ],
})

// 处理navchange
function changeDataNav(index) {
  dataList.value.Index = index,
      dataList.value.lineColor = index.color
  current.value = index.type

  // 显示数据更新提示
  showUpdateIndicator.value = true
  setTimeout(() => {
    showUpdateIndicator.value = false
  }, 2000)
}

// 卡片触摸交互
function handleCardTouchStart() {
  isCardActive.value = true
}

function handleCardTouchEnd() {
  setTimeout(() => {
    isCardActive.value = false
  }, 150)
}

// 模拟数据更新
onMounted(() => {
  setTimeout(() => {
    showUpdateIndicator.value = true
    setTimeout(() => {
      showUpdateIndicator.value = false
    }, 2000)
  }, 1000)
})
</script>

<style lang="scss" scoped>
$primary-color: #38963C;
$primary-light: rgba(56, 150, 60, 0.1);
$primary-gradient: linear-gradient(135deg, #38963C 0%, #5BCEBD 100%);
$card-shadow: 0 8px 32px rgba(56, 150, 60, 0.12);
$card-shadow-active: 0 12px 48px rgba(56, 150, 60, 0.2);
$border-radius: 20px;
$transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

.container {
  padding: 0 16px;
  background: linear-gradient(180deg, #F8F9FA 0%, #FFFFFF 100%);
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

// 标题区域
.title-area {
  padding: 20px 0;
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
  }
}

// 预览区域
.preview-wrapper {
  position: relative;
  margin: 24px 0;
  animation: slideInUp 0.6s ease-out 0.2s both;

  .preview {
    background: white;
    border-radius: $border-radius;
    box-shadow: $card-shadow;
    overflow: hidden;
    transition: $transition;
    border: 1px solid rgba(56, 150, 60, 0.08);

    &:hover {
      transform: translateY(-4px);
      box-shadow: $card-shadow-active;
    }
  }

  .preview-label {
    position: absolute;
    top: -10px;
    left: 20px;
    background: $primary-color;
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    z-index: 2;
  }
}

// 标签页区域
.tab-wrapper {
  margin: 32px 0 24px;
  animation: fadeIn 0.6s ease-out 0.4s both;

  .custom-tabs {
    background: white;
    border-radius: $border-radius;
    padding: 4px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    border: 1px solid rgba(56, 150, 60, 0.08);
  }
}

// 数据卡片区域
.tab-list {
  position: relative;
  animation: fadeIn 0.6s ease-out 0.6s both;

  .card-wrapper {
    position: relative;

    :deep(.grid-card-item) {
      border-radius: $border-radius;
      overflow: hidden;
      transition: $transition;
      background: white;
      box-shadow: $card-shadow;
      border: 1px solid rgba(56, 150, 60, 0.08);

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

  .update-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 16px;
    padding: 8px 16px;
    background: rgba(56, 150, 60, 0.08);
    border-radius: 20px;
    animation: slideInUp 0.4s ease-out;

    .update-text {
      font-size: 14px;
      color: $primary-color;
      margin-left: 8px;
      font-weight: 500;
    }
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 48px 20px;
    background: rgba(248, 249, 250, 0.8);
    border-radius: $border-radius;
    margin-top: 20px;
    animation: fadeIn 0.6s ease-out;

    .empty-text {
      font-size: 16px;
      color: #8E8E93;
      margin-top: 12px;
      font-weight: 500;
    }

    .empty-subtext {
      font-size: 14px;
      color: #C8C7CC;
      margin-top: 4px;
    }
  }
}

// 底部装饰
.bottom-decoration {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  gap: 8px;
  opacity: 0.3;

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: $primary-color;
    animation: pulse 2s ease-in-out infinite;

    &.dot-1 {
      animation-delay: 0s;
    }

    &.dot-2 {
      animation-delay: 0.2s;
    }

    &.dot-3 {
      animation-delay: 0.4s;
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
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.6;
  }
}

// 响应式调整
@media (max-width: 375px) {
  .title {
    font-size: 24px;
  }

  .tab-wrapper {
    margin: 24px 0 20px;
  }
}
</style>