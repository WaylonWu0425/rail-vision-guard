<template>
  <view class="container align-center">
    <view class="title1">完善用户信息</view>
    <view class="title2">请填写以下内容</view>
    <view class="form">
      <uv-form :model="form" :rules="rules" ref="formRef" labelWidth="80px" label-position="top">
        <uv-form-item label="姓名" prop="name" customStyle="width:288px">
          <uv-input class="input" v-model="form.name" placeholder="请输入姓名"/>
        </uv-form-item>

        <uv-form-item label="电话号码" prop="phoneNumber" customStyle="width:288px">
          <uv-input class="input" v-model="form.phoneNumber" placeholder="请输入电话号码"/>
        </uv-form-item>

        <uv-form-item label="生日" prop="birthday" customStyle="width:288px">
          <uv-input @click="calendars.open()" v-model="birthdayStr" readonly placeholder="请选择生日"/>
        </uv-form-item>

        <uv-form-item label="性别" prop="gender" customStyle="width:288px">
          <uv-radio-group v-model="form.gender">
            <uv-radio customStyle="margin-right: 50px;" label="男" name="男"/>
            <uv-radio label="女" name="女"/>
          </uv-radio-group>
        </uv-form-item>
      </uv-form>
    </view>
    <uv-calendars lunar ref="calendars" @confirm="confirm"/>
    <button type="default" @click="submitForm" class="btn-radius submit-button">提交信息</button>
  </view>
  <uv-toast ref="toast"></uv-toast>
</template>

<script setup>
import {ref, onMounted} from 'vue';
import {updataUser} from '@/api/account'
import {useUserStore} from '@/store/user.js'
import {formatDate} from '../../utils';
import UvFormItem from "../../uni_modules/uv-form/components/uv-form-item/uv-form-item.vue";
import UvForm from "../../uni_modules/uv-form/components/uv-form/uv-form.vue";
import UvInput from "../../uni_modules/uv-input/components/uv-input/uv-input.vue";
import UvRadioGroup from "../../uni_modules/uv-radio/components/uv-radio-group/uv-radio-group.vue";
import UvRadio from "../../uni_modules/uv-radio/components/uv-radio/uv-radio.vue";
import UvCalendars from "../../uni_modules/uv-calendars/components/uv-calendars/uv-calendars.vue";
import UvToast from "../../uni_modules/uv-toast/components/uv-toast/uv-toast.vue";

const toast = ref(null);

let userStore = useUserStore()
let form = ref({
  name: '',
  phoneNumber: '',
  birthday: '', // 日期字符串
  gender: '男'
});

let birthdayStr = ref('');
let calendars = ref(null);

function confirm(e) {
  birthdayStr.value = e.fulldate;
  form.value.birthday = e.fulldate;
}

let rules = {
  name: [
    {required: true, message: '请输入姓名', trigger: 'blur'}
  ],
  phoneNumber: [
    {required: true, message: '请输入电话号码', trigger: 'blur'},
    // 可以添加电话号码格式的验证规则
  ],
  gender: [
    {required: true, message: '请选择性别', trigger: 'change'}
  ]
};

let formRef = ref(null);

function submitForm() {
  formRef.value.validate().then(async () => {
    // 处理表单提交逻辑
    try {
      toast.value.show({
        type: 'loading',
        title: '正在加载',
        message: "正在加载"
      });
      console.log(form.value);
      await userStore.updateUserInfo(form.value)
      toast.value.hide()
      uni.showToast({
        title: '修改成功',
        icon: 'success'
      })
      userStore.fetchUserInfo()
    } catch (err) {
      console.error(err);

      uni.showToast({
        title: '网络错误',
        icon: 'error'
      })
      toast.value.hide()
    }
  })
}

// 如果有默认值，可以在此处初始化表单数据
onMounted(() => {
  form.value.gender = userStore.userInfo.gender
  form.value.birthday = userStore.userInfo.birthday
  form.value.name = userStore.userInfo.name
  form.value.phoneNumber = userStore.userInfo.phoneNumber
  birthdayStr.value = formatDate(userStore.userInfo.birthday, "YYYY-MM-DD")
});
</script>

<style lang="scss" scoped>
.submit-button {
  margin-top: 30px;
}
</style>
