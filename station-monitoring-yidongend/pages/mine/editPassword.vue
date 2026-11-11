<template>
  <view class="container align-center">
    <view class="title">修改密码</view>
    <view class="form">
      <uv-form :model="form" :rules="rules" ref="formRef" labelWidth="100px" label-position="top">
        <uv-form-item label="旧密码" prop="oldPassword" customStyle="width:288px">
          <uv-input v-model="form.oldPassword" type="password" placeholder="请输入旧密码"/>
        </uv-form-item>

        <uv-form-item label="新密码" prop="newPassword" customStyle="width:288px">
          <uv-input v-model="form.newPassword" type="password" placeholder="请输入新密码"/>
        </uv-form-item>

        <uv-form-item label="确认新密码" prop="confirmNewPassword" customStyle="width:288px">
          <uv-input v-model="form.confirmNewPassword" type="password" placeholder="请确认新密码"/>
        </uv-form-item>
      </uv-form>
    </view>

    <button type="default" @click="submitForm" class="btn-radius">提交</button>
    <uv-toast ref="toast"></uv-toast>
  </view>
</template>
<script setup>
import {
  ref
} from 'vue';
import {
  updatePassword
} from '../../api/account';

let toast = ref(null)

import {
  isEmpty
} from '../../utils';
import UvToast from "../../uni_modules/uv-toast/components/uv-toast/uv-toast.vue";

let form = ref({
  oldPassword: '',
  newPassword: '',
  confirmNewPassword: ''
});

let rules = {
  oldPassword: [{
    required: true,
    message: '请输入旧密码',
    trigger: 'blur'
  }],
  newPassword: [{
    required: true,
    message: '请输入新密码',
    trigger: 'blur'
  }],
  confirmNewPassword: [{
    required: true,
    message: '请确认新密码',
    trigger: 'blur'
  },
    {
      validator: validateConfirmNewPassword,
      trigger: 'blur'
    }
  ]
};

let formRef = ref(null);

function validateConfirmNewPassword(rule, value, callback) {
  if (value !== form.value.newPassword) {
    callback(new Error('两次输入的新密码不一致'));
  } else {
    callback();
  }
}

function submitForm() {
  formRef.value.validate().then(async () => {
    // 处理表单提交逻辑，例如发送请求到服务器
    let {
      oldPassword,
      newPassword
    } = form.value
    let newForm = {
      oldPassword,
      newPassword
    }
    try {
      toast.value.show({
        type: 'loading',
        title: '正在修改',
        message: "正在修改"
      });
      await updatePassword(newForm)
      toast.value.hide()
      uni.showToast({
        title: "修改成功",
        icon: "success"
      })
      setTimeout(() => {
        uni.removeStorageSync('token')
        uni.reLaunch({
          url: '/pages/login/login'
        })
      }, 500)
    } catch (err) {
      toast.value.hide()
      console.error(err)
      uni.showToast({
        icon: "error",
        title: err.data.message || "网络错误"
      })
    }
  }).catch(err => {
    console.log('表单验证失败：', err);
  });
}
</script>
<style lang="scss" scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.title {
  font-size: 24px;
  margin: 20px 0;
}

.form {
  width: 100%;
  max-width: 300px;
}

.btn-radius {
  margin-top: 20px;
  border-radius: 5px;
}
</style>