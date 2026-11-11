<template>
  <view class="page-container">
    <view class="content">
      <!-- 主标题 - 调整为项目名称 -->
      <view class="title-area">
        <text class="main-title">视界巡警</text>
        <!--        <text class="main-title">铁运安途</text>-->
      </view>

      <!-- 系统简介标题 -->
      <view class="section-title">
        <!--        <text>面向农产品冷链的轨道安全数字化服务平台</text>-->
        <text>基于多模态智能识别的轨道交通安全监测与应急处置系统</text>
      </view>

      <!-- 简介内容 - 调整为项目核心价值，移除emoji -->
      <view class="intro-content">
        <view class="feature-item">
          <view class="feature-dot" style="background-color: #2B6C8F;"></view>
          <view class="feature-wrapper">
            <text class="feature-title">乡村产地仓储</text>
            <text class="feature-text">温湿度实时监测，气体浓度预警，保障农产品源头品质。</text>
          </view>
        </view>

        <view class="feature-item">
          <view class="feature-dot" style="background-color: #38963C;"></view>
          <view class="feature-wrapper">
            <text class="feature-title">公路冷链短驳</text>
            <text class="feature-text">运输过程追踪，环境异常报警，衔接田间与铁路的关键环节。</text>
          </view>
        </view>

        <view class="feature-item">
          <view class="feature-dot" style="background-color: #2B6C8F;"></view>
          <view class="feature-wrapper">
            <text class="feature-title">铁路干线运输</text>
            <text class="feature-text">无人值守车厢巡检，火灾隐患识别，人员入侵预警，填补途中监管空白。</text>
          </view>
        </view>

        <view class="feature-item">
          <view class="feature-dot" style="background-color: #38963C;"></view>
          <view class="feature-wrapper">
            <text class="feature-title">移动端一体化管控</text>
            <text class="feature-text">远程操控巡检机器人，实时查看画面，分级预警推送，数据无缝对接铁路系统。</text>
          </view>
        </view>
      </view>

      <!-- 实时数据卡片 - 从欢迎页引入 -->
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

      <!-- 核心能力两栏布局 - 突出技术优势 -->
      <view class="two-columns">
        <view class="column">
          <text class="column-title">智能巡检机器人</text>
          <text class="column-text">温湿度/气体/烟雾多传感器融合</text>
          <text class="column-text">火花识别误报率≤5%，响应时间≤3秒</text>
          <text class="column-text">履带式机身，抗颠簸，耐低温，续航≥8小时</text>
          <text class="column-text">支持遥控/预制线路/自动避障三种模式</text>
        </view>
        <view class="column">
          <text class="column-title">移动端操控平台</text>
          <text class="column-text">实时画面传输，延迟≤1秒</text>
          <text class="column-text">分级预警推送（弹窗+声音+电话）</text>
          <text class="column-text">预制线路管理，手动绘制自定义路径</text>
          <text class="column-text">铁路专属功能：巡检记录导出、异常上报</text>
        </view>
      </view>

      <!-- 底部价值主张 - 从欢迎页引入并强化 -->
      <view class="value-proposition">
        <text class="value-text">减少农产品损耗 · 保障铁路货运安全 · 推动产业升级</text>
        <text class="value-subtext">田间—乡村仓储—公路短驳—铁路干线 全流程闭环管控</text>
      </view>

      <!-- 操作按钮区域 - 移动端常用底部按钮 -->
      <view class="action-buttons">
        <button @click="startInspection" class="btn primary-btn" hover-class="btn-hover">
          <text class="btn-text">开始巡检</text>
        </button>
        <button @click="viewReports" class="btn secondary-btn" hover-class="btn-hover">
          <text class="btn-text">查看报告</text>
        </button>
      </view>

      <!-- 底部安全距离 - 仅添加这个，防止底部导航栏遮挡 -->
      <view class="bottom-safe"></view>
    </view>
  </view>
</template>

<script setup>
// 页面逻辑
const startInspection = () => {
  // 跳转到巡检页面或打开巡检功能
  uni.showToast({
    title: '开始巡检',
    icon: 'success'
  });
  // 实际开发中可跳转：uni.navigateTo({ url: '/pages/inspection/inspection' });
}

const viewReports = () => {
  // 跳转到报告列表页面
  uni.showToast({
    title: '查看报告',
    icon: 'none'
  });
  // 实际开发中可跳转：uni.navigateTo({ url: '/pages/reports/reports' });
}
</script>

<style scoped>
page {
  height: 100vh;
  overflow: hidden;
  position: fixed;
  width: 100%;
}

.page-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow-y: auto;
  background-image: url('@/static/bg.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  padding: 30rpx;
  padding-top: calc(var(--status-bar-height) + 60rpx);
  /* 移除原来的底部padding，因为我们要用bottom-safe */
  box-sizing: border-box;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

/* 移除滚动条（保持功能） */
.page-container::-webkit-scrollbar {
  width: 0;
  height: 0;
  background: transparent;
}

.content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40rpx 30rpx;
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 32rpx;
  border: 2rpx solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8rpx 40rpx rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(20rpx);
  width: 100%;
  max-width: 700rpx;
  margin: auto;
}

/* 主标题 - 铁路蓝 + 农业绿主题 */
.title-area {
  margin-bottom: 30rpx;
  margin-top: 10rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.main-title {
  font-size: 56rpx;
  font-weight: 700;
  background: linear-gradient(135deg, #2B6C8F, #38963C);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 4rpx;
  line-height: 1.2;
  text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.1);
}

.main-title-en {
  font-size: 22rpx;
  color: #2B6C8F;
  font-weight: 500;
  letter-spacing: 2rpx;
  margin-top: 8rpx;
  opacity: 0.8;
}

/* 章节标题 */
.section-title {
  width: 100%;
  text-align: center;
  margin: 20rpx 0 30rpx;
  padding-bottom: 15rpx;
  border-bottom: 2rpx solid rgba(43, 108, 143, 0.3);
}

.section-title text {
  font-size: 34rpx;
  font-weight: bold;
  color: #2B6C8F;
  position: relative;
  display: inline-block;
}

.section-title text::after {
  content: '';
  position: absolute;
  bottom: -18rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 60rpx;
  height: 4rpx;
  background: linear-gradient(90deg, #2B6C8F, #38963C);
  border-radius: 2rpx;
}

/* 简介内容 - 无图标，使用圆点标识 */
.intro-content {
  width: 100%;
  margin-bottom: 30rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  padding: 16rpx 20rpx;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 20rpx;
  border-left: 6rpx solid transparent;
  transition: all 0.2s ease;
}

.feature-item:nth-child(odd) {
  border-left-color: #2B6C8F;
}

.feature-item:nth-child(even) {
  border-left-color: #38963C;
}

.feature-item:active {
  background: rgba(255, 255, 255, 0.8);
  transform: translateX(4rpx);
}

.feature-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  margin-top: 12rpx;
  flex-shrink: 0;
}

.feature-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.feature-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 6rpx;
}

.feature-text {
  font-size: 24rpx;
  line-height: 36rpx;
  color: #666;
  display: block;
}

/* 实时数据卡片 - 移动端优化 */
.stats-preview {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20rpx);
  border-radius: 48rpx;
  padding: 24rpx 20rpx;
  margin: 30rpx 0 40rpx;
  width: 100%;
  border: 1rpx solid rgba(43, 108, 143, 0.2);
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 22rpx;
  color: #666;
  margin-bottom: 6rpx;
  font-weight: 500;
}

.stat-value {
  font-size: 42rpx;
  font-weight: 700;
  color: #2B6C8F;
  line-height: 1.2;
}

.stat-value.warning {
  color: #FF6B6B;
  animation: pulse 1.5s ease-in-out infinite;
}

.stat-unit {
  font-size: 20rpx;
  color: #999;
  margin-left: 4rpx;
}

.stat-divider {
  width: 2rpx;
  height: 50rpx;
  background: rgba(43, 108, 143, 0.2);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* 两栏布局 - 移动端适配 */
.two-columns {
  display: flex;
  width: 100%;
  justify-content: space-between;
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.column {
  flex: 1;
  padding: 24rpx 20rpx;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.7));
  border: 1rpx solid rgba(43, 108, 143, 0.15);
  border-radius: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.03);
  backdrop-filter: blur(5rpx);
}

.column-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #38963C;
  text-align: center;
  margin-bottom: 20rpx;
  padding-bottom: 12rpx;
  border-bottom: 2rpx solid rgba(56, 150, 60, 0.2);
}

.column-text {
  display: block;
  font-size: 22rpx;
  line-height: 36rpx;
  color: #444;
  margin-bottom: 10rpx;
  padding-left: 16rpx;
  position: relative;
}

.column-text::before {
  content: '';
  position: absolute;
  left: 0;
  top: 14rpx;
  width: 8rpx;
  height: 8rpx;
  border-radius: 50%;
  background-color: #2B6C8F;
}

/* 底部价值主张 */
.value-proposition {
  text-align: center;
  padding: 30rpx 0 20rpx;
  border-top: 2rpx solid rgba(43, 108, 143, 0.15);
  width: 100%;
}

.value-text {
  display: block;
  font-size: 24rpx;
  font-weight: 600;
  color: #2B6C8F;
  line-height: 1.5;
  margin-bottom: 8rpx;
}

.value-subtext {
  display: block;
  font-size: 20rpx;
  color: #666;
  line-height: 1.5;
  opacity: 0.8;
}

/* 操作按钮区域 - 移动端底部按钮 */
.action-buttons {
  display: flex;
  width: 100%;
  gap: 20rpx;
  margin-top: 20rpx;
  margin-bottom: 10rpx;
}

.btn {
  flex: 1;
  height: 88rpx;
  border-radius: 44rpx;
  border: none;
  font-size: 28rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.btn-hover {
  transform: translateY(-2rpx);
  box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.15);
}

.primary-btn {
  background: linear-gradient(135deg, #2B6C8F, #38963C);
  color: #FFFFFF;
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.9);
  border: 2rpx solid #2B6C8F;
  color: #2B6C8F;
}

.btn-text {
  font-weight: 600;
}

/* 底部安全距离 - 防止底部导航栏遮挡内容 */
.bottom-safe {
  height: calc(40rpx + env(safe-area-inset-bottom));
  width: 100%;
}

/* 移动端响应式调整 */
@media (max-width: 375px) {
  .content {
    padding: 30rpx 20rpx;
  }

  .main-title {
    font-size: 48rpx;
  }

  .main-title-en {
    font-size: 18rpx;
  }

  .section-title text {
    font-size: 30rpx;
  }

  .feature-item {
    padding: 12rpx 16rpx;
  }

  .feature-title {
    font-size: 26rpx;
  }

  .feature-text {
    font-size: 22rpx;
    line-height: 34rpx;
  }

  .two-columns {
    flex-direction: column;
    gap: 16rpx;
  }

  .stat-value {
    font-size: 36rpx;
  }

  .btn {
    height: 80rpx;
    font-size: 26rpx;
  }
}

/* 适配全面屏底部 */
@media (min-height: 800px) {
  .content {
    padding: 40rpx 30rpx;
  }

  .action-buttons {
    margin-top: 30rpx;
    margin-bottom: 20rpx;
  }
}

/* 刘海屏适配 */
@supports (padding-bottom: constant(safe-area-inset-bottom)) {
  .bottom-safe {
    height: calc(40rpx + constant(safe-area-inset-bottom));
  }
}

@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .bottom-safe {
    height: calc(40rpx + env(safe-area-inset-bottom));
  }
}
</style>