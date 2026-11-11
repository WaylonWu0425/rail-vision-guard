<template>
  <view class="container">
    <!-- 页面标题 -->
    <view class="page-header">
      <view class="header-content">
        <view class="title-section">
          <view class="main-title">
            <text class="title-text">智能环境监控</text>
            <view class="title-line"></view>
          </view>
        </view>

        <view class="header-stats">
          <view class="stat-item">
            <view class="stat-icon">📷</view>
            <view class="stat-info">
              <text class="stat-number">{{ deviceCount }}</text>
              <text class="stat-label">在线设备</text>
            </view>
          </view>
        </view>
      </view>

      <view class="status-indicator">
        <view class="status-dot"></view>
        <text class="status-text">系统运行正常</text>
        <view class="status-time">{{ currentTime }}</view>
      </view>
    </view>

    <!-- 设备列表 -->
    <view class="device-list-section">
      <view class="section-header">
        <view class="section-title-container">
          <text class="section-title">监控设备列表</text>
        </view>
        <view class="device-count">
          <text class="count-number">{{ deviceCount }}</text>
          <text class="count-text">台设备在线</text>
        </view>
      </view>

      <view class="card-container">
        <!-- 摄像头01 -->
        <view class="device-card" @touchstart="handleCardTouch(0)" @touchend="handleCardTouchEnd">
          <view class="card-header">
            <view class="device-info">
              <view class="device-icon">
                <text>📷</text>
              </view>
              <view class="device-details">
                <text class="device-name">摄像头X8934</text>
                <view class="device-status online">
                  <view class="status-dot"></view>
                  <text class="status-text">在线</text>
                </view>
              </view>
            </view>
          </view>

          <view class="video-container">
            <view class="video-overlay">
              <view class="video-time">{{ formatTime(currentVideoTime) }}</view>
            </view>
            <video
                :id="'cameraVideo0'"
                :src="videoSrc01"
                controls
                autoplay
                loop
                class="camera-video"
                @play="handleVideoPlay(0)"
                @pause="handleVideoPause(0)"
                @timeupdate="handleTimeUpdate"
            ></video>
          </view>

          <view class="card-footer">
            <view class="environment-info">
              <view class="info-item">
                <view class="info-icon">🌡️</view>
                <text class="info-text">温度: {{ tempValue }}℃</text>
              </view>
              <view class="info-item">
                <view class="info-icon">💧</view>
                <text class="info-text">湿度: {{ humidityValue }}%</text>
              </view>
            </view>
            <view class="view-detail-btn" @click="showEnvironmentDialog(0)">
              <text class="btn-text">查看环境详情</text>
              <view class="btn-icon">→</view>
            </view>
          </view>
        </view>

        <!-- 摄像头02 -->
        <view class="device-card" @touchstart="handleCardTouch(1)" @touchend="handleCardTouchEnd">
          <view class="card-header">
            <view class="device-info">
              <view class="device-icon">
                <text>📷</text>
              </view>
              <view class="device-details">
                <text class="device-name">摄像头Y8935</text>
                <view class="device-status online">
                  <view class="status-dot"></view>
                  <text class="status-text">在线</text>
                </view>
              </view>
            </view>
          </view>

          <view class="video-container">
            <view class="video-overlay">
              <view class="video-time">{{ formatTime(currentVideoTime) }}</view>
            </view>
            <video
                :id="'cameraVideo1'"
                :src="videoSrc02"
                controls
                autoplay
                loop
                class="camera-video"
                @play="handleVideoPlay(1)"
                @pause="handleVideoPause(1)"
                @timeupdate="handleTimeUpdate"
            ></video>
          </view>

          <view class="card-footer">
            <view class="environment-info">
              <view class="info-item">
                <view class="info-icon">🌡️</view>
                <text class="info-text">温度: {{ tempValue2 }}℃</text>
              </view>
              <view class="info-item">
                <view class="info-icon">💧</view>
                <text class="info-text">湿度: {{ humidityValue2 }}%</text>
              </view>
            </view>
            <view class="view-detail-btn" @click="showEnvironmentDialog(1)">
              <text class="btn-text">查看环境详情</text>
              <view class="btn-icon">→</view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态提示 -->
    <view class="empty-state" v-if="deviceCount === 0">
      <view class="empty-illustration">
        <view class="camera-icon">
          <text>📷</text>
        </view>
        <view class="empty-wave"></view>
      </view>
      <text class="empty-title">暂无监控设备</text>
      <text class="empty-subtitle">请添加设备以开始监控</text>
      <view class="empty-action" @click="addNewCamera">
        <text class="action-text">添加监控设备</text>
      </view>
    </view>

    <!-- 环境数据弹窗 -->
    <uni-popup ref="environmentPopup" type="center" background-color="#fff" :mask-click="false">
      <view class="popup-container">
        <view class="popup-header">
          <text class="popup-title">{{ popupTitle }}</text>
          <view class="close-btn" @click="closeEnvironmentDialog">
            <text>×</text>
          </view>
        </view>

        <view class="popup-content">
          <view class="sensor-grid">
            <view class="sensor-item" v-for="sensor in displayedSensors" :key="sensor.type">
              <view class="sensor-icon-container">
                <text class="sensor-icon">{{ getSensorIcon(sensor.type) }}</text>
              </view>
              <view class="sensor-info">
                <text class="sensor-name">{{ sensor.title }}</text>
                <view class="sensor-value-container">
                  <text class="sensor-value">{{ sensor.value.toFixed(1) }}</text>
                  <text class="sensor-unit">{{ sensor.unit }}</text>
                </view>
              </view>
            </view>
          </view>

          <view class="popup-summary">
            <view class="summary-title">
              <text>实时数据概览</text>
            </view>
            <view class="summary-grid">
              <view class="summary-item" v-for="item in popupDataSummary" :key="item.title">
                <text class="summary-label">{{ item.title }}</text>
                <text class="summary-value">{{ item.value }}</text>
              </view>
            </view>
          </view>
        </view>

        <view class="popup-footer">
          <view class="popup-time">
            <text class="time-label">更新时间：</text>
            <text class="time-value">{{ popupUpdateTime }}</text>
          </view>
          <view class="popup-actions">
            <view class="popup-btn refresh-btn" @click="refreshEnvironmentData">
              <text class="btn-text">刷新数据</text>
            </view>
            <view class="popup-btn close-btn-full" @click="closeEnvironmentDialog">
              <text class="btn-text">关闭</text>
            </view>
          </view>
        </view>
      </view>
    </uni-popup>

    <!-- 装饰元素 -->
    <view class="decoration">
      <view class="wave wave-1"></view>
      <view class="wave wave-2"></view>
    </view>
  </view>
</template>

<script setup>
import {ref, onMounted, onUnmounted, computed} from 'vue'
import {useEnvironmentStore} from '../../store/environmentData';

// 使用环境数据store
const environmentStore = useEnvironmentStore()

// 视频源
const videoSrc01 = ref('/static/videos/demo01.mp4')
const videoSrc02 = ref('/static/videos/demo02.mp4')

// 状态管理
const deviceCount = ref(2)
const currentVideoTime = ref(0)
const activeCardIndex = ref(-1)
const currentTime = ref('')

// 弹窗相关
const environmentPopup = ref(null)
const currentCameraIndex = ref(0)
const popupUpdateTime = ref('')

// 从环境数据store中获取数据
const sensorData = computed(() => environmentStore.sensorData)

// 获取温度数据（第一个设备的温度）
const tempValue = computed(() => {
  const tempSensor = sensorData.value.find(item => item.type === 'temp')
  return tempSensor ? tempSensor.value.toFixed(1) : '--'
})

// 获取湿度数据（第一个设备的湿度）
const humidityValue = computed(() => {
  const humiditySensor = sensorData.value.find(item => item.type === 'humidity')
  return humiditySensor ? humiditySensor.value.toFixed(0) : '--'
})

// 第二个设备的温度（模拟不同数据）
const tempValue2 = computed(() => {
  const tempSensor = sensorData.value.find(item => item.type === 'temp')
  return tempSensor ? (tempSensor.value - 1).toFixed(1) : '--'
})

// 第二个设备的湿度（模拟不同数据）
const humidityValue2 = computed(() => {
  const humiditySensor = sensorData.value.find(item => item.type === 'humidity')
  return humiditySensor ? (parseFloat(humiditySensor.value) + 3).toFixed(0) : '--'
})

// 弹窗标题
const popupTitle = computed(() => {
  const deviceNames = ['摄像头X8934', '摄像头Y8935']
  return `${deviceNames[currentCameraIndex.value]} - 环境数据详情`
})

// 弹窗显示的传感器数据
const displayedSensors = computed(() => {
  // 显示所有传感器数据
  return sensorData.value
})

// 弹窗数据概览
const popupDataSummary = computed(() => {
  const tempSensor = sensorData.value.find(item => item.type === 'temp')
  const humiditySensor = sensorData.value.find(item => item.type === 'humidity')
  const breathSensor = sensorData.value.find(item => item.type === 'breath')
  const heartSensor = sensorData.value.find(item => item.type === 'heart')

  // 根据摄像头索引调整数值
  const tempAdjust = currentCameraIndex.value === 0 ? 0 : -1
  const humidityAdjust = currentCameraIndex.value === 0 ? 0 : 3

  return [
    { title: '温度', value: tempSensor ? (tempSensor.value + tempAdjust).toFixed(1) + '℃' : '--' },
    { title: '湿度', value: humiditySensor ? (parseFloat(humiditySensor.value) + humidityAdjust).toFixed(0) + '%' : '--' },
    { title: '呼吸', value: breathSensor ? breathSensor.value.toFixed(1) + '次/分' : '--' },
    { title: '心跳', value: heartSensor ? heartSensor.value.toFixed(0) + '次/分' : '--' }
  ]
})

// 获取传感器图标
const getSensorIcon = (type) => {
  const iconMap = {
    'temp': '🌡️',
    'humidity': '💧',
    'breath': '🌬️',
    'heart': '❤️',
    'yanwu': '💨',
    'shengyin': '🔊',
    'move': '🚶',
    'guang1': '💡',
    'distance': '📏'
  }
  return iconMap[type] || '📊'
}

// 显示环境数据弹窗
const showEnvironmentDialog = (cameraIndex) => {
  currentCameraIndex.value = cameraIndex
  updatePopupTime()
  environmentPopup.value.open()
}

// 关闭环境数据弹窗
const closeEnvironmentDialog = () => {
  environmentPopup.value.close()
}

// 刷新环境数据
const refreshEnvironmentData = () => {
  // 更新弹窗时间
  updatePopupTime()

  // 可以添加数据刷新逻辑
  uni.showToast({
    title: '环境数据已刷新',
    icon: 'success'
  })
}

// 更新弹窗时间
const updatePopupTime = () => {
  const now = new Date()
  const hours = now.getHours().toString().padStart(2, '0')
  const minutes = now.getMinutes().toString().padStart(2, '0')
  const seconds = now.getSeconds().toString().padStart(2, '0')
  popupUpdateTime.value = `${hours}:${minutes}:${seconds}`
}

// 卡片触摸交互
const handleCardTouch = (index) => {
  activeCardIndex.value = index
}

const handleCardTouchEnd = () => {
  setTimeout(() => {
    activeCardIndex.value = -1
  }, 150)
}

// 视频控制
const handleVideoPlay = (index) => {
  console.log(`摄像头${index}开始播放`)
}

const handleVideoPause = (index) => {
  console.log(`摄像头${index}暂停播放`)
}

const handleTimeUpdate = (event) => {
  currentVideoTime.value = event.detail.currentTime
}

const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 设备操作
const toggleCameraFullscreen = (index) => {
  uni.showToast({
    title: `全屏查看摄像头${index + 1}`,
    icon: 'none'
  })
}

const toggleCameraSettings = (index) => {
  uni.showToast({
    title: `调整摄像头${index + 1}设置`,
    icon: 'none'
  })
}

const addNewCamera = () => {
  uni.showToast({
    title: '添加设备功能开发中',
    icon: 'none'
  })
}

// 更新时间
const updateCurrentTime = () => {
  const now = new Date()
  const hours = now.getHours().toString().padStart(2, '0')
  const minutes = now.getMinutes().toString().padStart(2, '0')
  currentTime.value = `${hours}:${minutes}`
}

// 初始化
onMounted(() => {
  // 启动时间更新
  updateCurrentTime()
  const timer = setInterval(updateCurrentTime, 60000)

  // 清理定时器
  onUnmounted(() => {
    clearInterval(timer)
  })
})
</script>

<style scoped lang="scss">
// 定义颜色变量
$primary-color: #38963C;
$primary-light: rgba(56, 150, 60, 0.1);
$primary-lighter: rgba(56, 150, 60, 0.05);
$primary-dark: #2E7D32;
$primary-gradient: linear-gradient(135deg, #38963C, #66BB6A);
$success-color: #4CAF50;
$success-light: rgba(76, 175, 80, 0.1);
$warning-color: #FF9800;
$card-shadow: 0 8rpx 32rpx rgba(56, 150, 60, 0.12);
$card-shadow-hover: 0 16rpx 48rpx rgba(56, 150, 60, 0.2);
$border-radius: 20rpx;
$border-radius-lg: 28rpx;
$transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

// 弹窗样式变量
$popup-bg: #ffffff;
$popup-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.2);
$popup-radius: 28rpx;

// 动画定义
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(0.95);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10rpx);
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

.container {
  padding: 20rpx 30rpx 150rpx;
  min-height: 100vh;
  background: linear-gradient(180deg, #F8FFF8 0%, #F0F7F0 100%);
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  position: relative;
  overflow: hidden;
}

/* 页面标题 */
.page-header {
  padding: 30rpx 0 40rpx;
  animation: fadeIn 0.6s ease-out;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24rpx;

    .title-section {
      .main-title {
        display: flex;
        flex-direction: column;
        gap: 8rpx;

        .title-text {
          font-size: 48rpx;
          font-weight: 800;
          color: $primary-dark;
          line-height: 1.2;
          background: $primary-gradient;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .title-line {
          width: 60rpx;
          height: 6rpx;
          background: $primary-gradient;
          border-radius: 3rpx;
        }
      }
    }

    .header-stats {
      .stat-item {
        display: flex;
        align-items: center;
        gap: 12rpx;
        padding: 16rpx 24rpx;
        background: $primary-light;
        border-radius: $border-radius;

        .stat-icon {
          font-size: 32rpx;
          color: $primary-color;
        }

        .stat-info {
          display: flex;
          flex-direction: column;
          gap: 2rpx;

          .stat-number {
            font-size: 32rpx;
            font-weight: 700;
            color: $primary-dark;
          }

          .stat-label {
            font-size: 22rpx;
            color: rgba(0, 0, 0, 0.6);
          }
        }
      }
    }
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 12rpx;
    padding: 12rpx 24rpx;
    background: $success-light;
    border-radius: 40rpx;
    display: inline-flex;

    .status-dot {
      width: 12rpx;
      height: 12rpx;
      background: $success-color;
      border-radius: 50%;
      animation: pulse 2s ease-in-out infinite;
    }

    .status-text {
      font-size: 24rpx;
      color: $success-color;
      font-weight: 500;
    }

    .status-time {
      font-size: 22rpx;
      color: rgba(0, 0, 0, 0.5);
      margin-left: auto;
    }
  }
}

/* 设备列表区域 */
.device-list-section {
  animation: fadeIn 0.6s ease-out 0.2s both;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32rpx;

    .section-title-container {
      display: flex;
      align-items: center;
      gap: 16rpx;

      .section-title {
        font-size: 32rpx;
        font-weight: 700;
        color: $primary-dark;
        position: relative;

        &::after {
          content: '';
          position: absolute;
          bottom: -6rpx;
          left: 0;
          width: 40rpx;
          height: 4rpx;
          background: $primary-color;
          border-radius: 2rpx;
        }
      }
    }

    .device-count {
      display: flex;
      align-items: baseline;
      gap: 4rpx;

      .count-number {
        font-size: 36rpx;
        font-weight: 700;
        color: $primary-color;
      }

      .count-text {
        font-size: 24rpx;
        color: rgba(0, 0, 0, 0.6);
      }
    }
  }

  .card-container {
    display: flex;
    flex-direction: column;
    gap: 32rpx;
  }
}

/* 设备卡片 */
.device-card {
  background: white;
  border-radius: $border-radius-lg;
  padding: 32rpx;
  box-shadow: $card-shadow;
  border: 1rpx solid $primary-light;
  transition: $transition;
  position: relative;
  overflow: hidden;

  &:active {
    transform: translateY(-4rpx) scale(0.99);
    box-shadow: $card-shadow-hover;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 28rpx;

    .device-info {
      display: flex;
      align-items: center;
      gap: 16rpx;

      .device-icon {
        width: 64rpx;
        height: 64rpx;
        background: $primary-light;
        border-radius: 16rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32rpx;
        color: $primary-color;
        transition: $transition;
      }

      .device-details {
        display: flex;
        flex-direction: column;
        gap: 4rpx;

        .device-name {
          font-size: 28rpx;
          font-weight: 600;
          color: #1a1a1a;
        }

        .device-status {
          display: flex;
          align-items: center;
          gap: 8rpx;

          &.online {
            .status-dot {
              background: $success-color;
              animation: pulse 1.5s ease-in-out infinite;
            }

            .status-text {
              color: $success-color;
            }
          }

          .status-dot {
            width: 8rpx;
            height: 8rpx;
            border-radius: 50%;
          }

          .status-text {
            font-size: 22rpx;
            font-weight: 500;
          }
        }
      }
    }
  }

  .video-container {
    position: relative;
    margin-bottom: 28rpx;
    border-radius: $border-radius;
    overflow: hidden;

    .video-overlay {
      position: absolute;
      top: 16rpx;
      left: 16rpx;
      right: 16rpx;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 2;
      pointer-events: none;

      .video-time {
        color: white;
        font-size: 22rpx;
        background: rgba(0, 0, 0, 0.5);
        padding: 4rpx 12rpx;
        border-radius: 12rpx;
        backdrop-filter: blur(5rpx);
      }
    }

    .camera-video {
      width: 100%;
      height: 320rpx;
      border-radius: $border-radius;
      object-fit: cover;
      display: block;
    }
  }

  .card-footer {
    .environment-info {
      display: flex;
      gap: 24rpx;
      margin-bottom: 24rpx;

      .info-item {
        display: flex;
        align-items: center;
        gap: 8rpx;

        .info-icon {
          font-size: 24rpx;
          color: $primary-color;
        }

        .info-text {
          font-size: 24rpx;
          color: #666;
        }
      }
    }

    .view-detail-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12rpx;
      padding: 20rpx;
      background: $primary-gradient;
      border-radius: $border-radius;
      transition: $transition;

      &:active {
        transform: translateY(-2rpx);
        opacity: 0.9;
      }

      .btn-text {
        font-size: 28rpx;
        font-weight: 500;
        color: white;
      }

      .btn-icon {
        font-size: 24rpx;
        color: white;
        transition: transform 0.3s ease;
      }

      &:active .btn-icon {
        transform: translateX(4rpx);
      }
    }
  }
}

/* 环境数据弹窗 */
.popup-container {
  width: 700rpx;
  background: $popup-bg;
  border-radius: $popup-radius;
  overflow: hidden;
  box-shadow: $popup-shadow;

  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 32rpx 32rpx 24rpx;
    background: $primary-gradient;

    .popup-title {
      font-size: 32rpx;
      font-weight: 600;
      color: white;
    }

    .close-btn {
      width: 48rpx;
      height: 48rpx;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 36rpx;
      transition: $transition;

      &:active {
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0.9);
      }
    }
  }

  .popup-content {
    padding: 32rpx;
    max-height: 700rpx;
    overflow-y: auto;

    .sensor-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 24rpx;
      margin-bottom: 40rpx;

      .sensor-item {
        background: $primary-lighter;
        border-radius: $border-radius;
        padding: 24rpx;
        display: flex;
        align-items: center;
        gap: 20rpx;
        transition: $transition;
        border: 1rpx solid $primary-light;

        &:active {
          transform: translateY(-4rpx);
          box-shadow: 0 8rpx 24rpx rgba(56, 150, 60, 0.15);
        }

        .sensor-icon-container {
          width: 64rpx;
          height: 64rpx;
          background: white;
          border-radius: 16rpx;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 32rpx;
          flex-shrink: 0;
        }

        .sensor-info {
          flex: 1;

          .sensor-name {
            font-size: 24rpx;
            color: #666;
            display: block;
            margin-bottom: 8rpx;
          }

          .sensor-value-container {
            display: flex;
            align-items: baseline;
            gap: 4rpx;

            .sensor-value {
              font-size: 32rpx;
              font-weight: 700;
              color: $primary-dark;
            }

            .sensor-unit {
              font-size: 22rpx;
              color: #999;
            }
          }
        }
      }
    }

    .popup-summary {
      background: $primary-light;
      border-radius: $border-radius;
      padding: 24rpx;

      .summary-title {
        font-size: 28rpx;
        font-weight: 600;
        color: $primary-dark;
        margin-bottom: 20rpx;
        padding-bottom: 16rpx;
        border-bottom: 2rpx solid rgba(56, 150, 60, 0.2);
      }

      .summary-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20rpx;

        .summary-item {
          display: flex;
          flex-direction: column;
          gap: 8rpx;

          .summary-label {
            font-size: 24rpx;
            color: #666;
          }

          .summary-value {
            font-size: 28rpx;
            font-weight: 700;
            color: $primary-dark;
          }
        }
      }
    }
  }

  .popup-footer {
    padding: 24rpx 32rpx 32rpx;
    border-top: 1rpx solid #eee;

    .popup-time {
      display: flex;
      align-items: center;
      gap: 8rpx;
      margin-bottom: 24rpx;
      padding: 12rpx 16rpx;
      background: #f8f8f8;
      border-radius: 12rpx;

      .time-label {
        font-size: 22rpx;
        color: #666;
      }

      .time-value {
        font-size: 22rpx;
        font-weight: 600;
        color: $primary-color;
      }
    }

    .popup-actions {
      display: flex;
      gap: 20rpx;

      .popup-btn {
        flex: 1;
        padding: 24rpx;
        border-radius: $border-radius;
        text-align: center;
        font-size: 28rpx;
        font-weight: 500;
        transition: $transition;

        &.refresh-btn {
          background: $primary-lighter;
          color: $primary-color;

          &:active {
            background: $primary-light;
          }
        }

        &.close-btn-full {
          background: $primary-gradient;
          color: white;

          &:active {
            opacity: 0.9;
          }
        }

        .btn-text {
          font-weight: 500;
        }
      }
    }
  }
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 20rpx;
  text-align: center;
  animation: fadeIn 0.6s ease-out;

  .empty-illustration {
    position: relative;
    margin-bottom: 40rpx;

    .camera-icon {
      width: 120rpx;
      height: 120rpx;
      background: $primary-light;
      border-radius: 30rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 64rpx;
      color: $primary-color;
      animation: float 3s ease-in-out infinite;
    }

    .empty-wave {
      position: absolute;
      bottom: -20rpx;
      left: 50%;
      transform: translateX(-50%);
      width: 100rpx;
      height: 4rpx;
      background: linear-gradient(90deg, transparent, $primary-color, transparent);
      border-radius: 2rpx;
      animation: wave 2s ease-in-out infinite;
    }
  }

  .empty-title {
    font-size: 32rpx;
    color: #1a1a1a;
    font-weight: 600;
    margin-bottom: 12rpx;
  }

  .empty-subtitle {
    font-size: 26rpx;
    color: #666;
    margin-bottom: 48rpx;
  }

  .empty-action {
    padding: 24rpx 48rpx;
    background: $primary-gradient;
    border-radius: 40rpx;
    color: white;
    font-size: 28rpx;
    font-weight: 500;
    transition: $transition;

    &:active {
      transform: scale(0.95);
      box-shadow: 0 8rpx 24rpx rgba(56, 150, 60, 0.3);
    }

    .action-text {
      color: white;
    }
  }
}

/* 装饰元素 */
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
      width: 300rpx;
      height: 300rpx;
      top: -150rpx;
      right: -150rpx;
      opacity: 0.2;
      animation: float 20s ease-in-out infinite;
    }

    &.wave-2 {
      width: 200rpx;
      height: 200rpx;
      bottom: -100rpx;
      left: -100rpx;
      opacity: 0.1;
      animation: float 25s ease-in-out infinite reverse;
    }
  }
}

/* 响应式调整 */
@media (max-width: 375px) {
  .container {
    padding: 16rpx 24rpx 140rpx;
  }

  .page-header {
    .header-content {
      flex-direction: column;
      gap: 24rpx;

      .header-stats {
        align-self: flex-start;
      }
    }
  }

  .device-card {
    .video-container {
      .camera-video {
        height: 280rpx;
      }
    }
  }

  .popup-container {
    width: 650rpx;

    .sensor-grid {
      grid-template-columns: 1fr !important;
    }

    .summary-grid {
      grid-template-columns: 1fr !important;
    }
  }
}
</style>