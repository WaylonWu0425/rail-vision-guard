<template>
  <view class="work-container">
    <!-- 轮播图 -->
    <uni-swiper-dot class="uni-swiper-dot-box" :info="data" :current="current" field="content" :dots-styles="dotsStyles">
      <swiper
          class="swiper-box"
          :current="swiperDotIndex"
          @change="changeSwiper"
          :autoplay="true"
          :interval="3000"
          :duration="500"
          :circular="true"
      >
        <swiper-item v-for="(item, index) in data" :key="index">
          <view class="swiper-item" @click="clickBannerItem(item)">
            <image :src="item.image" mode="aspectFill" :draggable="false"/>
          </view>
        </swiper-item>
      </swiper>
    </uni-swiper-dot>

    <!-- 功能卡片 -->
    <view class="function-card">
      <view class="card-header">
        <view class="header-line"></view>
        <text class="card-title">基于多模态智能识别的轨道交通安全监测与应急处置系统</text>
<!--        <text class="card-title">面向农产品冷链的轨道安全数字化服务平台</text>-->
      </view>
      <view class="grid-body">
        <uni-grid :column="3" :showBorder="false" @change="changeGrid">
          <uni-grid-item>
            <view class="grid-item-box" @click="handleHazardClick">
              <uni-icons type="info-filled" size="30"></uni-icons>
              <text class="text">隐患信息查看</text>
            </view>
          </uni-grid-item>
          <uni-grid-item>
            <view class="grid-item-box" @click="handleDispatchClick">
              <uni-icons type="staff-filled" size="30"></uni-icons>
              <text class="text">任务派发与导航</text>
            </view>
          </uni-grid-item>
          <uni-grid-item>
            <view class="grid-item-box" @click="handleReportClick">
              <uni-icons type="person-filled" size="30"></uni-icons>
              <text class="text">人工上报</text>
            </view>
          </uni-grid-item>
          <uni-grid-item>
            <view class="grid-item-box" @click="handleReportViewClick">
              <uni-icons type="search" size="30"></uni-icons>
              <text class="text">报表查看</text>
            </view>
          </uni-grid-item>
          <uni-grid-item>
            <view class="grid-item-box" @click="handleStatisticsClick">
              <uni-icons type="list" size="30"></uni-icons>
              <text class="text">数据统计</text>
            </view>
          </uni-grid-item>
          <uni-grid-item>
            <view class="grid-item-box" @click="handleNoticeClick">
              <uni-icons type="chat-filled" size="30"></uni-icons>
              <text class="text">通知公告</text>
            </view>
          </uni-grid-item>
        </uni-grid>
      </view>
    </view>

    <!-- 底部安全距离 - 防止底部导航栏遮挡 -->
    <view class="bottom-safe"></view>
  </view>
</template>

<script setup>
import {ref} from "vue"

const current = ref(0)
const swiperDotIndex = ref(0)
const data = ref([
  {image: '/static/images/workbanner/banner01.jpg'},
  {image: '/static/images/workbanner/banner02.png'},
  {image: '/static/images/workbanner/banner03.jpg'},
  {image: '/static/images/workbanner/banner04.png'}
])

// 轮播图指示点样式
const dotsStyles = ref({
  backgroundColor: 'rgba(255, 255, 255, 0.3)',
  border: '1px rgba(255, 255, 255, 0.3) solid',
  color: '#fff',
  selectedBackgroundColor: '#3c96f3',
  selectedBorder: '1px #3c96f3 solid'
})

function clickBannerItem(item) {
  console.info(item)
}

function changeSwiper(e) {
  current.value = e.detail.current
  swiperDotIndex.value = e.detail.current
}

// 所有点击处理函数使用 uni.showToast
function handleDispatchClick() {
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
}

function handleHazardClick() {
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
}

function handleReportClick() {
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
}

function handleStatisticsClick() {
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
}

function handleReportViewClick() {
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
}

function handleNoticeClick() {
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
}

function changeGrid(e) {
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
}
</script>

<style lang="scss" scoped>
/* #ifndef APP-NVUE */
page {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  background-color: #f5f5f5;
  min-height: 100%;
  height: auto;
}

view {
  font-size: 14px;
  line-height: inherit;
}

/* #endif */

.work-container {
  background-color: #f5f5f5;
  min-height: 100vh;
  padding-bottom: 20rpx;
  position: relative;
}

/* 轮播图样式 */
.uni-swiper-dot-box {
  width: 100%;
  margin-bottom: 20rpx;
}

.swiper-box {
  height: 400rpx;
}

.swiper-item {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.swiper-item image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 功能卡片 */
.function-card {
  background-color: #ffffff;
  margin: 20rpx;
  margin-top: 30rpx;
  border-radius: 20rpx;
  padding: 30rpx 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
}

.header-line {
  width: 8rpx;
  height: 36rpx;
  background: linear-gradient(180deg, #00bcd4 0%, #0097a7 100%);
  border-radius: 4rpx;
  margin-right: 16rpx;
}

.card-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333333;
}

.text {
  text-align: center;
  font-size: 26rpx;
  margin-top: 10rpx;
}

.grid-item-box {
  flex: 1;
  /* #ifndef APP-NVUE */
  display: flex;
  /* #endif */
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 15px 0;
}

.uni-margin-wrap {
  width: 690rpx;
  width: 100%;
}

/* 底部安全距离 - 防止底部导航栏遮挡 */
.bottom-safe {
  height: calc(40rpx + env(safe-area-inset-bottom));
  width: 100%;
}

@media screen and (min-width: 500px) {
  .uni-swiper-dot-box {
    width: 400px;
    /* #ifndef APP-NVUE */
    margin: 0 auto;
    /* #endif */
    margin-top: 8px;
  }

  .image {
    width: 100%;
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