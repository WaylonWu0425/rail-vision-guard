<template>
  <view class="email-container">
    <!-- 背景装饰元素 -->
    <view class="background-elements">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
      <view class="circle circle-3"></view>
    </view>

    <!-- 邮箱绑定卡片 -->
    <view class="email-card">
      <!-- 欢迎标题 -->
      <view class="welcome-section">
        <view class="welcome-icon">
          <!-- <text>📧</text> -->
        </view>
        <text class="welcome-title">验证邮箱</text>
        <text class="welcome-subtitle">请输入您的邮箱地址以继续注册</text>
      </view>

      <!-- 邮箱表单 -->
      <view class="form-section">
        <uv-form ref="formRef" label-width="150" label-position="top" :model="form" :rules="rules">

          <!-- 邮箱输入 -->
          <view class="form-item">
            <view class="form-label">
              <!-- <text class="label-icon">📧</text> -->
              <text class="label-text">邮箱地址</text>
            </view>
            <uv-input
                v-model="form.email"
                placeholder="请输入您的邮箱"
                :customStyle="inputStyle"
                border="none"
            >
              <template #prefix>
                <!-- <text class="input-prefix">@</text> -->
              </template>
            </uv-input>
            <view class="email-tips">
              <text class="tip-text">我们将向该邮箱发送验证码，请确保邮箱可用</text>
            </view>
          </view>

          <!-- 发送按钮 -->
          <button class="send-btn" @click="submitForm" :disabled="isLoading">
            <text class="btn-text" v-if="!isLoading">发送验证邮件</text>
            <text class="btn-text" v-else>发送中...</text>
            <view class="btn-icon" v-if="!isLoading">→</view>
          </button>
        </uv-form>

        <!-- 登录链接 -->
        <view class="login-section">
          <text class="login-text">已有账号？</text>
          <navigator url="/pages/login/login" open-type="navigate" class="login-link">
            <text>立即登录</text>
            <view class="link-icon">→</view>
          </navigator>
        </view>

      </view>

      <!-- 底部提示 -->
      <view class="footer-tips">
        <text class="tip-text">继续注册即表示您同意</text>
        <text class="tip-link" @click="handleTerms">《用户协议》</text>
        <text class="tip-text">和</text>
        <text class="tip-link" @click="handlePrivacy">《隐私政策》</text>
      </view>
    </view>

    <!-- Toast组件 -->
    <uv-toast ref="toast"></uv-toast>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { verifyCode } from '../../api/login';

// 颜色变量
const primaryColor = '#38963C';
const primaryLight = 'rgba(56, 150, 60, 0.1)';
const primaryGradient = 'linear-gradient(135deg, #38963C, #66BB6A)';

// 表单引用
const toast = ref(null);
const formRef = ref(null);
const isLoading = ref(false);

// 表单数据
let form = ref({
  email: '',
});

// 输入框样式
const inputStyle = computed(() => ({
  height: '88rpx',
  padding: '0 24rpx',
  borderRadius: '16rpx',
  backgroundColor: '#F8FFF8',
  border: '1rpx solid rgba(56, 150, 60, 0.2)'
}));

// 表单验证规则
let rules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
};

// 处理用户协议
function handleTerms() {
  uni.navigateTo({
    url: '/pages/agreement/terms'
  });
}

// 处理隐私政策
function handlePrivacy() {
  uni.navigateTo({
    url: '/pages/agreement/privacy'
  });
}

async function submitForm() {
  try {
    // 验证表单
    await formRef.value.validate();

    isLoading.value = true;

    // 显示加载提示
    toast.value.show({
      type: 'loading',
      title: '发送邮件中',
      message: '正在发送验证邮件...'
    });

    let obj = {
      address: form.value.email
    };

    // 调用发送验证码接口
    await verifyCode(obj);

    // 隐藏加载提示
    toast.value.hide();
    isLoading.value = false;

    // 存储邮箱到本地
    uni.setStorageSync('email', form.value.email);

    // 显示成功提示
    uni.showToast({
      title: '验证邮件已发送',
      icon: 'success',
      duration: 2000
    });

    // 延迟跳转到验证页面
    setTimeout(() => {
      uni.navigateTo({
        url: '/pages/register/validEmail'
      });
    }, 1500);

  } catch (err) {
    // 隐藏加载提示
    toast.value.hide();
    isLoading.value = false;

    // 错误处理
    let errorMessage = '发送失败，请稍后重试';

    if (err.data && err.data.message) {
      errorMessage = err.data.message;
    } else if (err.message) {
      errorMessage = err.message;
    } else if (err.response && err.response.data && err.response.data.message) {
      errorMessage = err.response.data.message;
    }

    uni.showToast({
      title: errorMessage,
      icon: 'error',
      duration: 2000
    });

    console.error('发送验证码错误:', err);
  }
}

</script>

<style lang="scss" scoped>
// 颜色变量
$primary-color: #38963C;
$primary-light: rgba(56, 150, 60, 0.1);
$primary-lighter: rgba(56, 150, 60, 0.05);
$primary-dark: #2E7D32;
$primary-gradient: linear-gradient(135deg, #38963C, #66BB6A);
$success-color: #4CAF50;
$text-color: #333;
$text-light: #666;
$text-lighter: #999;
$border-color: rgba(56, 150, 60, 0.2);
$background-color: #F8FFF8;
$card-shadow: 0 20rpx 60rpx rgba(56, 150, 60, 0.15);

// 动画
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

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10rpx);
  }
}

.email-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40rpx;
  position: relative;
  overflow: hidden;
}

.background-elements {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;

  .circle {
    position: absolute;
    border-radius: 50%;
    background: $primary-light;
    animation: float 6s ease-in-out infinite;

    &.circle-1 {
      width: 200rpx;
      height: 200rpx;
      top: 10%;
      left: 10%;
      opacity: 0.3;
    }

    &.circle-2 {
      width: 300rpx;
      height: 300rpx;
      bottom: 20%;
      right: 10%;
      opacity: 0.2;
      animation-delay: -2s;
    }

    &.circle-3 {
      width: 150rpx;
      height: 150rpx;
      top: 60%;
      left: 20%;
      opacity: 0.4;
      animation-delay: -4s;
    }
  }
}

.email-card {
  width: 100%;
  max-width: 600rpx;
  background: white;
  border-radius: 32rpx;
  padding: 60rpx 40rpx;
  box-shadow: $card-shadow;
  position: relative;
  z-index: 1;
  animation: fadeIn 0.6s ease-out;
  border: 1rpx solid rgba(56, 150, 60, 0.1);
}

.welcome-section {
  text-align: center;
  margin-bottom: 60rpx;

  .welcome-icon {
    width: 80rpx;
    height: 80rpx;
    background: $primary-gradient;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 24rpx;
    font-size: 40rpx;
    color: white;
    animation: float 3s ease-in-out infinite;
  }

  .welcome-title {
    display: block;
    font-size: 40rpx;
    font-weight: 700;
    color: $primary-dark;
    margin-bottom: 12rpx;
  }

  .welcome-subtitle {
    display: block;
    font-size: 28rpx;
    color: $text-light;
  }
}

.form-section {
  .form-item {
    margin-bottom: 40rpx;

    .form-label {
      display: flex;
      align-items: center;
      gap: 12rpx;
      margin-bottom: 16rpx;

      .label-icon {
        font-size: 28rpx;
        color: $primary-color;
      }

      .label-text {
        font-size: 28rpx;
        font-weight: 600;
        color: $text-color;
      }
    }

    .input-prefix {
      font-size: 28rpx;
      color: $primary-color;
      margin-right: 12rpx;
    }

    .email-tips {
      margin-top: 12rpx;
      padding: 12rpx 16rpx;
      background-color: $primary-lighter;
      border-radius: 12rpx;
      border-left: 4rpx solid $primary-color;

      .tip-text {
        font-size: 24rpx;
        color: $text-light;
        line-height: 1.4;
      }
    }
  }
}

.send-btn {
  width: 100%;
  height: 88rpx;
  background: $primary-gradient;
  border-radius: 44rpx;
  border: none;
  color: white;
  font-size: 32rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  margin-bottom: 40rpx;
  transition: all 0.3s ease;

  &:active {
    transform: translateY(-2rpx);
    opacity: 0.9;
  }

  &:disabled {
    background: linear-gradient(135deg, #cccccc, #dddddd);
    opacity: 0.7;
  }

  .btn-text {
    font-weight: 600;
  }

  .btn-icon {
    font-size: 28rpx;
    transition: transform 0.3s ease;
  }

  &:active .btn-icon {
    transform: translateX(4rpx);
  }
}

.login-section {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 50rpx;

  .login-text {
    font-size: 26rpx;
    color: $text-light;
  }

  .login-link {
    display: flex;
    align-items: center;
    gap: 8rpx;
    font-size: 26rpx;
    color: $primary-color;
    font-weight: 600;
    text-decoration: none;

    .link-icon {
      font-size: 22rpx;
      transition: transform 0.3s ease;
    }

    &:active .link-icon {
      transform: translateX(4rpx);
    }
  }
}

.footer-tips {
  text-align: center;
  font-size: 24rpx;
  color: $text-lighter;
  padding-top: 30rpx;
  border-top: 1rpx solid $border-color;

  .tip-link {
    color: $primary-color;
    padding: 0 4rpx;
  }
}

// 响应式调整
@media (max-width: 375px) {
  .email-card {
    padding: 50rpx 30rpx;
  }

  .welcome-title {
    font-size: 36rpx;
  }

  .welcome-subtitle {
    font-size: 26rpx;
  }
}
</style>