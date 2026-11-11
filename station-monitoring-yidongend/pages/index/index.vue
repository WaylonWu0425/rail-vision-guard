<template>
  <view class="welcome-container">
    <!-- 背景图片 -->
    <image
        :lazy-load="true"
        :fade-show="true"
        src="../../static/bg.jpg"
        mode="aspectFill"
        class="background-image"
    ></image>

    <!-- 渐变遮罩层 - 调整为铁路/农业主题色 -->
    <view class="gradient-overlay"></view>

    <!-- 主内容区域 -->
    <view class="content-wrapper">
      <!-- 应用图标和名称 -->
      <view class="app-brand">
<!--        <text class="app-name">铁运安途</text>-->
        <text class="app-name">视界巡警</text>
        <text class="app-subname">农链公铁联运版</text>
      </view>

      <!-- 欢迎标语 - 调整为项目定位 -->
      <view class="welcome-content">
        <text class="main-title">科技助农 · 智慧铁路</text>
        <text class="subtitle">基于多模态智能识别的轨道交通安全监测与应急处置系统</text>
<!--        <text class="subtitle">面向农产品冷链的轨道安全数字化服务平台</text>-->
        <text class="description">田间仓储 · 公路短驳 · 铁路干线 · 全流程管控</text>
      </view>

      <!-- 功能亮点 - 调整为项目核心功能 -->
      <view class="features">
        <view class="feature-item">
          <view class="feature-icon">
            <text>🌾</text>
          </view>
          <text class="feature-text">乡村仓储</text>
          <text class="feature-desc">环境监测</text>
        </view>
        <view class="feature-item">
          <view class="feature-icon">
            <text>🚛</text>
          </view>
          <text class="feature-text">公路冷链</text>
          <text class="feature-desc">实时追踪</text>
        </view>
        <view class="feature-item">
          <view class="feature-icon">
            <text>🚂</text>
          </view>
          <text class="feature-text">铁路干线</text>
          <text class="feature-desc">无人巡检</text>
        </view>
      </view>

      <!-- 实时数据预览卡片 -->
      <view class="stats-preview">
        <view class="stat-item">
          <text class="stat-label">在巡设备</text>
          <text class="stat-value">24</text>
          <text class="stat-unit">台</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-label">今日预警</text>
          <text class="stat-value warning">3</text>
          <text class="stat-unit">条</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-label">巡检里程</text>
          <text class="stat-value">1,286</text>
          <text class="stat-unit">km</text>
        </view>
      </view>

      <!-- 按钮区域 - 保持原有功能逻辑 -->
      <view class="action-buttons">
        <button
            @click="toRegister"
            class="btn register-btn"
            hover-class="btn-hover"
        >
          <text class="btn-text">立即注册</text>
          <view class="btn-icon">→</view>
        </button>

        <button
            @click="toLogin"
            class="btn login-btn"
            hover-class="btn-hover"
        >
          <text class="btn-text">已有账户，登录</text>
        </button>
      </view>

      <!-- 底部安全提示 - 调整为项目价值 -->
      <view class="safety-tips">
        <text class="tip-text">减少农产品损耗 · 保障铁路货运安全 · 推动产业升级</text>
      </view>
    </view>
  </view>
</template>

<script setup>
function toLogin(){
  uni.navigateTo({
    url: '/pages/login/login'
  });
}

function toRegister(){
  uni.navigateTo({
    url: '/pages/register/register'
  });
}
</script>

<style lang="scss" scoped>
// 颜色变量 - 调整为铁路蓝 + 农业绿的主题
$primary-color: #2B6C8F;  // 铁路蓝
$secondary-color: #38963C; // 农业绿
$primary-gradient: linear-gradient(135deg, #2B6C8F, #38963C);
$white: #FFFFFF;
$white-transparent: rgba(255, 255, 255, 0.9);
$dark-overlay: rgba(26, 35, 50, 0.8);
$light-text: rgba(255, 255, 255, 0.95);
$lighter-text: rgba(255, 255, 255, 0.7);
$warning-color: #FF6B6B;

// 动画效果
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
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

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.welcome-container {
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg,
      rgba(26, 35, 50, 0.9) 0%,
      rgba(43, 108, 143, 0.5) 50%,
      rgba(56, 150, 60, 0.4) 100%);
  z-index: 1;
}

.content-wrapper {
  position: relative;
  z-index: 2;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 100rpx 40rpx 60rpx;
  animation: fadeInUp 0.8s ease-out;
}

.app-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 60rpx;

  .app-name {
    font-size: 56rpx;
    font-weight: 700;
    color: $white;
    text-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.3);
    letter-spacing: 2rpx;
  }

  .app-subname {
    font-size: 28rpx;
    color: $lighter-text;
    margin-top: 8rpx;
    padding: 4rpx 20rpx;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 30rpx;
    backdrop-filter: blur(10rpx);
  }
}

.welcome-content {
  text-align: center;
  margin-bottom: 60rpx;

  .main-title {
    display: block;
    font-size: 48rpx;
    font-weight: 700;
    color: $white;
    margin-bottom: 16rpx;
    text-shadow: 0 4rpx 8rpx rgba(0, 0, 0, 0.3);
  }

  .subtitle {
    display: block;
    font-size: 36rpx;
    font-weight: 600;
    margin-bottom: 20rpx;
    background: linear-gradient(135deg, #FFFFFF, #E0E0E0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .description {
    display: block;
    font-size: 28rpx;
    color: $light-text;
    line-height: 1.6;
    background: rgba(255, 255, 255, 0.1);
    padding: 16rpx 30rpx;
    border-radius: 50rpx;
    display: inline-block;
    margin: 0 auto;
  }
}

.features {
  display: flex;
  justify-content: space-around;
  margin-bottom: 50rpx;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20rpx);
  border-radius: 40rpx;
  padding: 30rpx 20rpx;

  .feature-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8rpx;

    .feature-icon {
      width: 90rpx;
      height: 90rpx;
      background: $white-transparent;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 48rpx;
      backdrop-filter: blur(10rpx);
      animation: float 3s ease-in-out infinite;
      box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.2);

      &:nth-child(1) { animation-delay: 0s; }
      &:nth-child(2) { animation-delay: 0.5s; }
      &:nth-child(3) { animation-delay: 1s; }
    }

    .feature-text {
      font-size: 26rpx;
      color: $white;
      font-weight: 600;
      margin-top: 8rpx;
    }

    .feature-desc {
      font-size: 20rpx;
      color: $lighter-text;
    }
  }
}

.stats-preview {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(20rpx);
  border-radius: 40rpx;
  padding: 30rpx 20rpx;
  margin-bottom: 60rpx;

  .stat-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;

    .stat-label {
      font-size: 24rpx;
      color: $lighter-text;
      margin-bottom: 8rpx;
    }

    .stat-value {
      font-size: 40rpx;
      font-weight: 700;
      color: $white;
      line-height: 1.2;

      &.warning {
        color: $warning-color;
        animation: pulse 1.5s ease-in-out infinite;
      }
    }

    .stat-unit {
      font-size: 20rpx;
      color: $lighter-text;
      margin-left: 4rpx;
    }
  }

  .stat-divider {
    width: 2rpx;
    height: 60rpx;
    background: rgba(255, 255, 255, 0.2);
  }
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
  margin-bottom: 50rpx;

  .btn {
    height: 96rpx;
    border-radius: 48rpx;
    border: none;
    font-size: 32rpx;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;

    &.btn-hover {
      transform: translateY(-2rpx);
      box-shadow: 0 10rpx 20rpx rgba(0, 0, 0, 0.2);
    }

    .btn-text {
      font-weight: 600;
    }

    .btn-icon {
      font-size: 28rpx;
      margin-left: 12rpx;
      transition: transform 0.3s ease;
    }

    &:active .btn-icon {
      transform: translateX(4rpx);
    }
  }

  .register-btn {
    background: $primary-gradient;
    color: $white;
    box-shadow: 0 8rpx 16rpx rgba(43, 108, 143, 0.3);

    .btn-text {
      color: $white;
    }
  }

  .login-btn {
    background: transparent;
    border: 2rpx solid $white-transparent;
    color: $white;
    backdrop-filter: blur(10rpx);

    .btn-text {
      color: $white;
    }
  }
}

.safety-tips {
  text-align: center;
  padding-top: 30rpx;
  border-top: 1rpx solid rgba(255, 255, 255, 0.2);

  .tip-text {
    font-size: 24rpx;
    color: $lighter-text;
    line-height: 1.6;
  }
}

// 响应式调整
@media (max-width: 375px) {
  .content-wrapper {
    padding: 80rpx 30rpx 40rpx;
  }

  .app-brand {
    margin-bottom: 40rpx;

    .app-name {
      font-size: 48rpx;
    }

    .app-subname {
      font-size: 24rpx;
    }
  }

  .welcome-content {
    margin-bottom: 40rpx;

    .main-title {
      font-size: 40rpx;
    }

    .subtitle {
      font-size: 32rpx;
    }

    .description {
      font-size: 24rpx;
      padding: 12rpx 20rpx;
    }
  }

  .features {
    padding: 20rpx 10rpx;
    margin-bottom: 40rpx;

    .feature-icon {
      width: 80rpx;
      height: 80rpx;
      font-size: 40rpx;
    }

    .feature-text {
      font-size: 24rpx;
    }
  }

  .stats-preview {
    padding: 20rpx 10rpx;
    margin-bottom: 40rpx;

    .stat-value {
      font-size: 36rpx;
    }
  }

  .action-buttons {
    .btn {
      height: 88rpx;
    }
  }
}

@media (min-height: 800px) {
  .content-wrapper {
    padding-top: 140rpx;
  }

  .app-brand {
    margin-bottom: 80rpx;
  }

  .features {
    margin-bottom: 70rpx;
  }

  .stats-preview {
    margin-bottom: 80rpx;
  }
}
</style>