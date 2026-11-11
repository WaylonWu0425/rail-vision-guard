<template>
  <view class="login">
    <!-- 背景图片 -->
    <image
        :lazy-load="true"
        :fade-show="true"
        src="/static/bg.jpg"
        mode="aspectFill"
        class="background-image"
    ></image>

    <!-- 渐变遮罩层 -->
    <view class="gradient-overlay"></view>

    <view class="login-box">
      <view class="app-brand">
<!--        <text class="app-name">铁运安途</text>-->
        <text class="app-name">视界巡警</text>
        <text class="app-subname">基于多模态智能识别的轨道交通安全监测与应急处置系统</text>
<!--        <text class="app-subname">面向农产品冷链的轨道安全数字化服务平台</text>-->
      </view>

      <!-- 系统状态提示 -->
      <view class="system-status">
        <text class="status-dot"></text>
        <text class="status-text">智能巡检系统 · 在线</text>
      </view>

      <!-- 标签切换 -->
      <view class="tabs">
        <view
            class="tab"
            :class="{ active: activeName === 'account' }"
            @click="activeName = 'account'"
        >
          账户登录
        </view>
        <view
            class="tab"
            :class="{ active: activeName === 'email' }"
            @click="activeName = 'email'"
        >
          邮箱登录
        </view>
      </view>

      <!-- 账户登录 -->
      <view v-if="activeName === 'account'" class="form">
        <view class="form-item">
          <text class="label">账户</text>
          <input
              class="input"
              type="text"
              v-model="userInfo.account"
              placeholder="请输入账户"
              placeholder-class="placeholder"
          />
        </view>
        <view class="form-item">
          <text class="label">密码</text>
          <input
              class="input"
              type="password"
              v-model="userInfo.password"
              placeholder="请输入密码"
              placeholder-class="placeholder"
          />
        </view>
        <view class="form-options">
          <label class="remember-label">
            <checkbox
                :checked="checked1"
                @click="checked1 = !checked1"
                color="#2B6C8F"
                style="transform: scale(0.8)"
            />
            <text class="remember-text">记住密码</text>
          </label>
          <text class="forgot-text">忘记密码？</text>
        </view>
      </view>

      <!-- 邮箱登录 -->
      <view v-if="activeName === 'email'" class="form">
        <view class="form-item">
          <text class="label">邮箱</text>
          <input
              class="input"
              type="text"
              v-model="userInfo.email"
              placeholder="请输入邮箱"
              placeholder-class="placeholder"
          />
        </view>
        <view class="form-item code-item">
          <text class="label">验证码</text>
          <view class="code-wrapper">
            <input
                class="input code-input"
                type="text"
                v-model="userInfo.code"
                placeholder="请输入验证码"
                placeholder-class="placeholder"
            />
            <button
                class="code-btn"
                :disabled="codeSending || codeCountdown > 0"
                @click="getCode"
            >
              {{ codeCountdown > 0 ? `${codeCountdown}s` : '获取验证码' }}
            </button>
          </view>
        </view>
      </view>

<!--      &lt;!&ndash; 巡检员快捷登录提示 &ndash;&gt;-->
<!--      <view class="demo-hint" v-if="activeName === 'account'">-->
<!--        <text class="hint-text">演示账号：1234567 / 000000</text>-->
<!--      </view>-->

      <view class="register" @click="goRegister">
        <text>还没有账号？立即注册</text>
      </view>

      <view class="login-btn">
        <button
            class="btn"
            :disabled="loginLoading"
            @click="login"
        >
          <text class="btn-text">{{ loginLoading ? '登录中...' : '登录' }}</text>
          <view class="btn-icon" v-if="!loginLoading">→</view>
        </button>
      </view>

      <!-- 底部角色提示 -->
      <view class="role-tips">
        <text class="tip-text">乡村用户 | 铁路工作人员 | 管理员</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import {onMounted, reactive, ref} from 'vue';
import {useUserStore} from '@/store/user';

// 确保 store 正确初始化
let userStore;
try {
  userStore = useUserStore();
  console.log('Pinia store 初始化成功:', userStore);
} catch (error) {
  console.error('Pinia store 初始化失败:', error);
}

const activeName = ref('account');
const loginLoading = ref(false);
const codeSending = ref(false);
const codeCountdown = ref(0);
const checked1 = ref(false);

const userInfo = reactive({
  account: '1234567',
  password: '000000',
  email: '',
  code: ''
});

let countdownTimer = null;

// 读取记住的密码
onMounted(() => {
  const savedAccount = uni.getStorageSync('savedAccount');
  if (savedAccount) {
    userInfo.account = savedAccount.account || '';
    userInfo.password = savedAccount.password || '';
    checked1.value = true;
  }
});

// 获取验证码
const getCode = async () => {
  if (!userInfo.email) {
    uni.showToast({
      title: '请输入邮箱',
      icon: 'none'
    });
    return;
  }

  const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
  if (!emailRegex.test(userInfo.email)) {
    uni.showToast({
      title: '邮箱格式不正确',
      icon: 'none'
    });
    return;
  }

  codeSending.value = true;

  try {
    const res = await sendCode(userInfo.email);
    console.log('验证码响应:', res);

    if (res.data && res.data.msg === '验证码发送成功') {
      uni.showToast({
        title: '验证码已发送',
        icon: 'success'
      });

      codeCountdown.value = 60;
      if (countdownTimer) clearInterval(countdownTimer);
      countdownTimer = setInterval(() => {
        codeCountdown.value--;
        if (codeCountdown.value <= 0) {
          clearInterval(countdownTimer);
        }
      }, 1000);
    } else {
      uni.showToast({
        title: res.data?.msg || '发送失败',
        icon: 'none'
      });
    }
  } catch (error) {
    console.error('发送失败:', error);
    uni.showToast({
      title: '网络错误',
      icon: 'none'
    });
  } finally {
    codeSending.value = false;
  }
};

// 登录
const login = async () => {
  // 表单验证
  if (activeName.value === 'account') {
    if (!userInfo.account) {
      uni.showToast({title: '请输入账户', icon: 'none'});
      return;
    }
    if (!userInfo.password) {
      uni.showToast({title: '请输入密码', icon: 'none'});
      return;
    }
  } else {
    if (!userInfo.email) {
      uni.showToast({title: '请输入邮箱', icon: 'none'});
      return;
    }
    if (!userInfo.code) {
      uni.showToast({title: '请输入验证码', icon: 'none'});
      return;
    }
  }

  loginLoading.value = true;
  uni.showLoading({title: '登录中...'});

  try {
    let res;

    if (activeName.value === 'account') {
      res = await doLoginWithAccount(userInfo.account, userInfo.password);
      console.log('账号登录响应:', res);

      if (checked1.value) {
        uni.setStorageSync('savedAccount', {
          account: userInfo.account,
          password: userInfo.password
        });
      } else {
        uni.removeStorageSync('savedAccount');
      }
    } else {
      res = await doLoginWithEmail(userInfo.email, userInfo.code);
      console.log('邮箱登录响应:', res);
    }

    uni.hideLoading();

    // 根据网页端的响应格式判断
    if (res.data && (res.data.msg === '登录成功' || res.data.code === 200)) {
      // 存储token
      if (res.data.token) {
        uni.setStorageSync('token', res.data.token);
      }

      // 存储用户信息到本地
      if (res.data.data) {
        uni.setStorageSync('userInfo', res.data.data);
        console.log('用户信息已存储到本地:', res.data.data);

        // 如果有 Pinia store，也存储到 Pinia
        if (userStore) {
          userStore.login(res.data.data);
          console.log('用户信息已存储到 Pinia');
        }
      }

      uni.showToast({
        title: '登录成功',
        icon: 'success',
        duration: 1500
      });

      // 根据角色跳转
      const userRole = res.data.data?.role || '0';
      setTimeout(() => {
        // 跳转到首页
        uni.reLaunch({url: '/pages/home/home'});
        // if (userRole === '1') {
        //   console.log('跳转到职位管理页面');
        //   uni.reLaunch({url: '/pages/jobManagement/jobManagement'});
        // } else {
        //   console.log('跳转到任务管理页面');
        //   uni.reLaunch({url: '/pages/employeeTask/employeeTask'});
        // }
      }, 1500);
    } else {
      uni.showToast({
        title: res.data?.msg || '登录失败',
        icon: 'none'
      });
    }
  } catch (error) {
    uni.hideLoading();
    console.error('登录失败:', error);

    uni.showToast({
      title: error.message || '网络错误',
      icon: 'none'
    });
  } finally {
    loginLoading.value = false;
  }
};

// 跳转到注册页
const goRegister = () => {
  uni.navigateTo({
    // url: '/pages/register/bindEmail'
    url: '/pages/register/register'
  });
};

// ==================== API 请求函数 ====================
const BASE_URL = 'http://localhost:8081';

const doLoginWithAccount = (account, password) => {
  return new Promise((resolve, reject) => {
    const url = `${BASE_URL}/user/doLogin/account?account=${encodeURIComponent(account)}&password=${encodeURIComponent(password)}`;

    uni.request({
      url: url,
      method: 'POST',
      header: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      success: (res) => {
        console.log('账号登录原始响应:', res);
        if (res.statusCode === 200) {
          resolve(res);
        } else {
          reject(new Error(res.data?.msg || `登录失败 (${res.statusCode})`));
        }
      },
      fail: (err) => {
        console.error('账号登录请求失败:', err);
        reject(err);
      }
    });
  });
};

const doLoginWithEmail = (email, code) => {
  return new Promise((resolve, reject) => {
    const url = `${BASE_URL}/user/doLogin/email?email=${encodeURIComponent(email)}&code=${encodeURIComponent(code)}`;

    uni.request({
      url: url,
      method: 'POST',
      header: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      success: (res) => {
        console.log('邮箱登录原始响应:', res);
        if (res.statusCode === 200) {
          resolve(res);
        } else {
          reject(new Error(res.data?.msg || `登录失败 (${res.statusCode})`));
        }
      },
      fail: (err) => {
        console.error('邮箱登录请求失败:', err);
        reject(err);
      }
    });
  });
};

const sendCode = (email) => {
  return new Promise((resolve, reject) => {
    const url = `${BASE_URL}/user/send-code?email=${encodeURIComponent(email)}`;

    uni.request({
      url: url,
      method: 'POST',
      header: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      success: (res) => {
        console.log('验证码原始响应:', res);
        if (res.statusCode === 200) {
          resolve(res);
        } else {
          reject(new Error(res.data?.msg || `发送失败 (${res.statusCode})`));
        }
      },
      fail: (err) => {
        console.error('验证码请求失败:', err);
        reject(err);
      }
    });
  });
};
</script>

<style lang="scss" scoped>
// 颜色变量
$primary-color: #2B6C8F;  // 铁路蓝
$secondary-color: #38963C; // 农业绿
$primary-gradient: linear-gradient(135deg, #2B6C8F, #38963C);
$white: #FFFFFF;
$white-transparent: rgba(255, 255, 255, 0.95);
$light-bg: rgba(255, 255, 255, 0.9);
$border-color: rgba(43, 108, 143, 0.2);
$text-primary: #2B6C8F;
$text-secondary: #38963C;
$text-regular: #333333;
$text-secondary-light: #666666;
$placeholder-color: #999999;

.login {
  position: relative;
  height: 100vh;
  width: 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
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
  background: linear-gradient(135deg,
      rgba(43, 108, 143, 0.7) 0%,
      rgba(56, 150, 60, 0.6) 100%);
  z-index: 1;
}

.login-box {
  position: relative;
  z-index: 2;
  width: 85%;
  max-width: 650rpx;
  background: $light-bg;
  backdrop-filter: blur(20px);
  border-radius: 32rpx;
  padding: 50rpx 40rpx;
  box-shadow: 0 20rpx 40rpx rgba(0, 0, 0, 0.2);
  border: 2rpx solid rgba(255, 255, 255, 0.3);
}

.app-brand {
  text-align: center;
  margin-bottom: 30rpx;

  .app-name {
    display: block;
    font-size: 56rpx;
    font-weight: 700;
    color: $text-primary;
    letter-spacing: 2rpx;
    margin-bottom: 8rpx;
    text-shadow: 0 2rpx 4rpx rgba(255, 255, 255, 0.5);
  }

  .app-subname {
    display: block;
    font-size: 26rpx;
    color: $text-secondary;
    background: rgba(56, 150, 60, 0.1);
    padding: 6rpx 20rpx;
    border-radius: 30rpx;
    display: inline-block;
    margin: 0 auto;
  }
}

.system-status {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 40rpx;

  .status-dot {
    width: 12rpx;
    height: 12rpx;
    background-color: #38963C;
    border-radius: 50%;
    margin-right: 8rpx;
    animation: pulse 1.5s ease-in-out infinite;
  }

  .status-text {
    font-size: 24rpx;
    color: $text-primary;
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

.tabs {
  display: flex;
  border-bottom: 2rpx solid $border-color;
  margin-bottom: 40rpx;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 20rpx 0;
  font-size: 30rpx;
  color: $text-secondary-light;
  position: relative;
}

.tab.active {
  color: $text-primary;
  font-weight: 600;
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: -2rpx;
  left: 20%;
  width: 60%;
  height: 4rpx;
  background: $primary-gradient;
  border-radius: 2rpx;
}

.form-item {
  margin-bottom: 30rpx;
}

.label {
  display: block;
  font-size: 28rpx;
  color: $text-regular;
  margin-bottom: 12rpx;
  font-weight: 500;
}

.input {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  border: 2rpx solid $border-color;
  border-radius: 16rpx;
  background-color: $white;
  box-sizing: border-box;
  transition: all 0.3s ease;

  &:focus {
    border-color: $text-primary;
    box-shadow: 0 0 0 4rpx rgba(43, 108, 143, 0.1);
  }
}

.placeholder {
  color: $placeholder-color;
  font-size: 26rpx;
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20rpx;
}

.remember-label {
  display: flex;
  align-items: center;
}

.remember-text {
  font-size: 26rpx;
  color: $text-secondary-light;
  margin-left: 8rpx;
}

.forgot-text {
  font-size: 26rpx;
  color: $text-primary;
  opacity: 0.8;
}

.code-item .code-wrapper {
  display: flex;
  gap: 20rpx;
}

.code-input {
  flex: 1;
}

.code-btn {
  width: 200rpx;
  height: 88rpx;
  background: $primary-gradient;
  color: $white;
  font-size: 26rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  padding: 0;
  box-shadow: 0 4rpx 12rpx rgba(43, 108, 143, 0.3);

  &::after {
    border: none;
  }

  &:disabled {
    opacity: 0.6;
    box-shadow: none;
  }

  &:active {
    opacity: 0.9;
    transform: translateY(2rpx);
  }
}

.demo-hint {
  background: rgba(43, 108, 143, 0.05);
  border-radius: 12rpx;
  padding: 16rpx 20rpx;
  margin: 20rpx 0;
  border-left: 6rpx solid $text-primary;

  .hint-text {
    font-size: 24rpx;
    color: $text-primary;
    font-family: monospace;
  }
}

.register {
  text-align: center;
  margin: 40rpx 0 30rpx;

  text {
    font-size: 28rpx;
    color: $text-primary;
    text-decoration: underline;
    text-underline-offset: 4rpx;
    text-decoration-color: rgba(43, 108, 143, 0.3);
  }
}

.login-btn {
  text-align: center;
}

.btn {
  width: 280rpx;
  height: 88rpx;
  background: $primary-gradient;
  color: $white;
  font-size: 32rpx;
  border-radius: 44rpx;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  box-shadow: 0 8rpx 16rpx rgba(43, 108, 143, 0.3);
  transition: all 0.3s ease;

  &::after {
    border: none;
  }

  &:disabled {
    opacity: 0.6;
    box-shadow: none;
  }

  &:active {
    transform: translateY(4rpx);
    box-shadow: 0 4rpx 8rpx rgba(43, 108, 143, 0.3);
  }

  .btn-text {
    font-weight: 600;
  }

  .btn-icon {
    font-size: 32rpx;
    margin-left: 8rpx;
    transition: transform 0.3s ease;
  }

  &:active .btn-icon {
    transform: translateX(6rpx);
  }
}

.role-tips {
  text-align: center;
  margin-top: 40rpx;
  padding-top: 30rpx;
  border-top: 2rpx solid $border-color;

  .tip-text {
    font-size: 24rpx;
    color: $text-secondary-light;
    letter-spacing: 2rpx;
  }
}

// 响应式调整
@media (max-width: 375px) {
  .login-box {
    padding: 40rpx 30rpx;
  }

  .app-name {
    font-size: 48rpx;
  }

  .app-subname {
    font-size: 24rpx;
  }

  .tab {
    font-size: 28rpx;
  }

  .input {
    height: 80rpx;
    font-size: 26rpx;
  }

  .code-btn {
    height: 80rpx;
    font-size: 24rpx;
    width: 180rpx;
  }

  .btn {
    width: 240rpx;
    height: 80rpx;
    font-size: 30rpx;
  }
}
</style>