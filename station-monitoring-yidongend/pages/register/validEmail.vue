<template>
  <view class="container align-center">
    <view class="title1">输入验证码</view>
    <view class="title2">我们刚刚向您的邮箱{{ emailAddress }}</view>
    <view class="title4">发送了一条消息</view>
    <view class="form-item">
      <xt-verify-code type="middle" :size="4" v-model="verifyCode" @confirm="confirm"></xt-verify-code>
    </view>
    <view class="title3">
      <navigator url="/pages/login/login" open-type="navigate">已有账号？
        <text class="navigate">登录</text>
      </navigator>
    </view>

  </view>
  <uv-toast ref="toast"></uv-toast>
</template>

<script setup>
import {onMounted, ref} from 'vue';
import {verifyCodeID} from '../../api/login';

let inputItems = ref(null) // 定义一个ref来存储input元素数组
onMounted(() => {
  emailAddress.value = uni.getStorageSync('email')
  inputItems.value = document.querySelectorAll('.valid-input') // 在onMounted中获取input元素数组
})
let emailAddress = ref('example@gmail.com')
let verifyCode = ref('')
let toast = ref(null)

async function confirm() {
  try {
    toast.value.show({
      type: 'loading',
      title: '正在验证',
      message: "正在验证"
    });
    await verifyCodeID({
      address: emailAddress.value,
      verifyCode: verifyCode._value
    })
    toast.value.hide()

    setTimeout(() => {
      uni.showToast({
        icon: 'success',
        title: '验证成功'
      })
    }, 0)
    uni.navigateTo({
      url: '/pages/register/register'
    })
  } catch (err) {
    toast.value.hide()
    uni.showToast({
      icon: 'error',
      title: err.data.message
    })
  }

}
</script>

<style lang="scss" scoped>
.container {
  height: 100vh;
  width: 100%;
  position: fixed;
}

.title4 {
  font-size: $title-h3;
  color: $grey1;
  margin-top: 0;
}

.form-item {
  margin-top: 50px;
  width: 288px;
  display: flex;
  justify-content: center;
  align-items: center;
}

button {
  margin-top: 50px;
}

.title3 {
  margin-top: 75px;
}

.valid-input {
  width: 58px;
  height: 52px;
  border: 1px solid $border-color;
  border-radius: 12px;
  font-size: 32px;
  padding: 10px;
  text-align: center;
}

.navigate {
  color: $navigtion-color;
}
</style>
