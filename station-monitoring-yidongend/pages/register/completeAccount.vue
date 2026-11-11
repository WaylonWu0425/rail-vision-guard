<template>
  <view class="container align-center">
    <view class="title1">完善用户信息</view>
    <view class="title2">请填写以下内容</view>
    <view class="form">
      <uv-form :model="form" :rules="rules" ref="formRef" labelWidth="80px" label-position="top">
        <uv-form-item label="姓名" prop="username" customStyle="width:288px">
          <uv-input class="input" v-model="form.username" placeholder="请输入姓名"/>
        </uv-form-item>

        <uv-form-item label="电话号码" prop="phoneNumber" customStyle="width:288px">
          <uv-input class="input" v-model="form.phoneNumber" placeholder="请输入电话号码"/>
        </uv-form-item>

        <uv-form-item label="生日" prop="birthday" customStyle="width:288px">
          <uv-calendars lunar ref="calendars" @confirm="confirm"/>
          <view @click="calendars.open()">
            <uv-input v-model="birthdayStr" readonly placeholder="请选择生日"/>
          </view>
        </uv-form-item>

        <uv-form-item label="性别" prop="gender" customStyle="width:288px">
          <uv-radio-group v-model="form.gender">
            <!--            <uv-radio customStyle="margin-right: 50px;" label="男" name="男"/>-->
            <!--            <uv-radio label="女" name="女"/>-->
            <uv-radio customStyle="margin-right: 50px;" label="男" :name="1"/>
            <uv-radio label="女" :name="2"/>
          </uv-radio-group>
        </uv-form-item>
      </uv-form>
    </view>

    <button type="default" @click="submitForm" class="btn-radius submit-button">提交信息</button>
  </view>
  <uv-toast ref="toast"></uv-toast>
</template>

<script setup>
import {ref, onMounted} from 'vue';
import {updataUser, getUser} from '@/api/account'
import {useUserStore} from "../../store/user";

const toast = ref(null);
const userStore = useUserStore();

let form = ref({
  username: '',
  phoneNumber: '',
  birthday: '', // 日期字符串
  gender: 1 // 假设 1 表示男性，2 表示女性
});

let birthdayStr = ref('');
let calendars = ref(null);

function confirm(e) {
  birthdayStr.value = e.fulldate;
  form.value.birthday = e.fulldate;
}

let rules = {
  username: [
    {required: true, message: '请输入姓名', trigger: 'blur'}
  ],
  phoneNumber: [
    {required: true, message: '请输入电话号码', trigger: 'blur'},
  ],
  birthday: [
    {required: true, message: '请选择生日', trigger: 'change'}
  ],
  gender: [
    {
      required: true,
      message: '请选择性别',
      trigger: 'change',
      validator: (rule, value, callback) => {
        if (value === 1 || value === 2) {
          callback();
        } else {
          callback(new Error('请选择性别'));
        }
      }
    }
  ]
};

// let rules = {
//   name: [
//     {required: true, message: '请输入姓名', trigger: 'blur'}
//   ],
//   phoneNumber: [
//     {required: true, message: '请输入电话号码', trigger: 'blur'},
//   ],
//   birthday: [
//     {required: true, message: '请选择生日', trigger: 'change'}
//   ],
//   gender: [
//     {required: true, message: '请选择性别', trigger: 'change'}
//   ]
// };

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

      // // 在pinia仓库中获取用户id
      // const userStore = useUserStore()
      // let userId = userStore.userInfo.id
      // // 结合form和id创建完整的数据：data
      // let data = {
      //   id: userId,
      //   name: form.value.name,
      //   phoneNumber: form.value.phoneNumber,
      //   birthday: form.value.birthday,
      //   gender: form.value.gender
      // }

      // await updataUser(data)

      await updataUser(form.value)

      // 获取用户信息并存储
      let userInfo = await getUser()
      userStore.userInfo = userInfo.data.user
      uni.setStorageSync('userInfo', userInfo.data.user)


      toast.value.hide()
      uni.reLaunch({
        url: '/pages/home/home',

      })
    } catch (err) {
      console.error(err);

      uni.showToast({
        title: err.data.message || '网络错误',
        icon: 'error'
      })
      toast.value.hide()
    }
  })
}

// 加载已存在的用户信息
onMounted(() => {
  if (userStore.userInfo) {
    // 如果用户已经有部分信息，预填到表单中
    if (userStore.userInfo.phoneNumber) {
      form.value.phoneNumber = userStore.userInfo.phoneNumber;
    }
    if (userStore.userInfo.birthday) {
      form.value.birthday = userStore.userInfo.birthday;
      birthdayStr.value = userStore.userInfo.birthday;
    }
    if (userStore.userInfo.gender && userStore.userInfo.gender !== 0) {
      form.value.gender = userStore.userInfo.gender;
    }
    if (userStore.userInfo.username) {
      form.value.username = userStore.userInfo.username;
    }
  }
});


</script>

<style lang="scss" scoped>
.submit-button {
  margin-top: 30px;
}
</style>
