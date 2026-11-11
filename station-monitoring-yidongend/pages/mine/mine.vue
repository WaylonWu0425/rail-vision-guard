<template>
  <view class="mine-container" :style="{height: `${windowHeight}px`}">
    <!--顶部个人信息栏-->
    <view class="header-section">
      <view class="flex padding justify-between">
        <view class="flex align-center">
          <!-- 头像显示：有avatar用图片，否则用本地默认头像 -->
          <image
              v-if="localAvatar"
              @click="handleToAvatar"
              :src="localAvatar"
              class="cu-avatar xl round"
              mode="aspectFill"
          >
          </image>
          <view v-else class="cu-avatar xl round bg-white" @click="handleToAvatar">
            <uni-icons type="person" size="40" color="#999"></uni-icons>
          </view>

          <view v-if="!name" @click="handleToLogin" class="login-tip">
            点击登录
          </view>
          <view v-if="name" @click="handleToInfo" class="user-info">
            <view class="u_title">
              用户名：{{ name }}
            </view>
          </view>
        </view>
        <view @click="handleToInfo" class="flex align-center">
          <text>个人信息 <uni-icons type="right" size="16" color="#fff"></uni-icons></text>

        </view>
      </view>
    </view>

    <view class="content-section">
      <!-- 四宫格功能图标 -->
      <view class="mine-actions grid col-4 text-center">
        <view class="action-item" @click="handleJiaoLiuQun">
          <view class="icon-wrapper pink">
            <uni-icons type="chat-filled" size="28" color="#fff"></uni-icons>
          </view>
          <text class="text">交流群</text>
        </view>
        <view class="action-item" @click="handleBuilding">
          <view class="icon-wrapper blue">
            <uni-icons type="headphones" size="28" color="#fff"></uni-icons>
          </view>
          <text class="text">在线客服</text>
        </view>
        <view class="action-item" @click="handleBuilding">
          <view class="icon-wrapper purple">
            <uni-icons type="chatboxes-filled" size="28" color="#fff"></uni-icons>
          </view>
          <text class="text">反馈社区</text>
        </view>
        <view class="action-item" @click="handleBuilding">
          <view class="icon-wrapper green">
            <uni-icons type="hand-up-filled" size="28" color="#fff"></uni-icons>
          </view>
          <text class="text">点赞我们</text>
        </view>
      </view>

      <!-- 菜单列表 -->
      <view class="menu-list">
        <view class="list-cell" @click="handleToEditInfo">
          <view class="menu-item-box">
            <uni-icons type="person-filled" size="20" color="#666"></uni-icons>
            <text>编辑资料</text>
          </view>
          <uni-icons type="right" size="14" color="#ccc"></uni-icons>
        </view>

        <view class="list-cell" @click="handleHelp">
          <view class="menu-item-box">
            <uni-icons type="help-filled" size="20" color="#666"></uni-icons>
            <text>常见问题</text>
          </view>
          <uni-icons type="right" size="14" color="#ccc"></uni-icons>
        </view>

        <view class="list-cell" @click="handleAbout">
          <view class="menu-item-box">
            <uni-icons type="heart-filled" size="20" color="#666"></uni-icons>
            <text>关于我们</text>
          </view>
          <uni-icons type="right" size="14" color="#ccc"></uni-icons>
        </view>

        <view class="list-cell" @click="handleToSetting">
          <view class="menu-item-box">
            <uni-icons type="gear-filled" size="20" color="#666"></uni-icons>
            <text>应用设置</text>
          </view>
          <uni-icons type="right" size="14" color="#ccc"></uni-icons>
        </view>
      </view>
    </view>

    <!-- 底部安全距离 - 防止底部导航栏遮挡 -->
    <view class="bottom-safe"></view>
  </view>
</template>

<script setup>
import {useUserStore} from '../../store/user';
import {computed, ref, watch} from "vue"

const userStore = useUserStore()

// 直接使用计算属性获取头像，这样每次访问都会重新计算
const localAvatar = computed(() => {
  console.log('计算头像:', userStore.userInfo?.avatar)
  // if (userStore.userInfo?.avatar) {
  //   return userStore.userInfo.avatar
  // }
  return '/static/images/avatar/烈焰飞鸟11.png'
})

const name = computed(() => {
  console.log('计算用户名:', userStore.userInfo?.username)
  return userStore.userInfo?.username || ''
})

const windowHeight = computed(() => uni.getSystemInfoSync().windowHeight - 50)

// 检查登录状态的方法
function checkLogin() {
  if (!userStore.isLogIn) {
    uni.showToast({
      title: '请先登录',
      icon: 'none',
      duration: 2000
    })
    setTimeout(() => {
      uni.navigateTo({
        url: '/pages/login'
      })
    }, 1500)
    return false
  }
  return true
}

function handleToInfo() {
  if (!checkLogin()) return
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
  // uni.navigateTo('/pages/mine/info/index')
}

function handleToEditInfo() {
  if (!checkLogin()) return
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
  // uni.navigateTo('/pages/mine/info/edit')
}

function handleToSetting() {
  if (!checkLogin()) return
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
  // uni.navigateTo('/pages/mine/setting/index')
}

function handleToLogin() {
  uni.reLaunch({
    url: '/pages/login'
  })
}

function handleToAvatar() {
  if (!checkLogin()) return
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
  // uni.navigateTo('/pages/mine/avatar/index')
}

function handleHelp() {
  if (!checkLogin()) return
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
  // uni.navigateTo('/pages/mine/help/index')
}

function handleAbout() {
  if (!checkLogin()) return
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
  // uni.navigateTo('/pages/mine/about/index')
}

function handleJiaoLiuQun() {
  if (!checkLogin()) return
  uni.showToast({
    title: 'QQ群：①133713780(满)、②146013835(满)、③189091635',
    icon: 'none',
    duration: 3000
  })
}

function handleBuilding() {
  if (!checkLogin()) return
  uni.showToast({
    title: '模块建设中~',
    icon: 'none',
    duration: 2000
  })
}
</script>

<style lang="scss" scoped>
page {
  background-color: #f5f6f7;
}

.mine-container {
  width: 100%;
  height: 100%;

  .header-section {
    padding: 15px 15px 45px 15px;
    background-color: #3c96f3;
    color: white;

    .login-tip {
      font-size: 18px;
      margin-left: 10px;
    }

    .cu-avatar {
      width: 80px;
      height: 80px;
      border: 2px solid #eaeaea;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .user-info {
      margin-left: 15px;

      .u_title {
        font-size: 18px;
        line-height: 30px;
      }
    }
  }

  .content-section {
    position: relative;
    top: -50px;

    .mine-actions {
      margin: 15px 15px;
      padding: 20px 0px;
      border-radius: 8px;
      background-color: white;
      display: grid;
      grid-template-columns: repeat(4, 1fr);

      .action-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        .icon-wrapper {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 8px;

          &.pink {
            background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
          }

          &.blue {
            background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
          }

          &.purple {
            background: linear-gradient(135deg, #d4b6ff 0%, #b28aff 100%);
          }

          &.green {
            background: linear-gradient(135deg, #96e6a1 0%, #d4fc79 100%);
          }
        }

        .text {
          display: block;
          font-size: 13px;
        }
      }
    }

    .menu-list {
      margin: 15px 15px;
      background-color: white;
      border-radius: 8px;
      overflow: hidden;

      .list-cell {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 15px 20px;
        background-color: white;
        border-bottom: 1px solid #f0f0f0;

        &:last-child {
          border-bottom: none;
        }

        .menu-item-box {
          display: flex;
          align-items: center;
          gap: 15px;

          text {
            font-size: 16px;
            color: #333;
          }
        }
      }
    }
  }
}

/* 底部安全距离 */
.bottom-safe {
  height: calc(40rpx + env(safe-area-inset-bottom));
  width: 100%;
}
</style>