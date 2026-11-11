<template>
  <div class="login">
    <div class="login-box">
      <div class="name">车站视频管理系统</div>
      <!--              <div class="name">车站监控系统</div>-->
      <!--            <div class="name">视界巡警</div>-->

      <div class="info">
        <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleClick" :stretch="true">
          <el-tab-pane label="账户登录" name="first">
            <div><span>账户</span>
              <el-input v-model="userInfo.account" style="width: 70%;margin-left: 30px;" class="input-box"/>
            </div>
            <div><span>密码</span>
              <el-input v-model="userInfo.password" style="width: 70%;margin-left: 30px;" class="input-box"/>
            </div>
            <div class="remenber">
              <el-checkbox v-model="checked1" label="记住密码" size="large"/>
            </div>
          </el-tab-pane>
          <el-tab-pane label="邮箱登录" name="second">
            <div><span>邮箱</span>
              <el-input v-model="userInfo.email" style="width: 70%;margin-left: 30px;" class="input-box"/>
            </div>
            <div><span>验证码</span>
              <el-input v-model="userInfo.code" style="width: 70%" class="input-box"/>
            </div>
            <div class="getCode">
              <el-button
                  type="plain"
                  @click=getCode()
                  link
              >
                获取验证码
              </el-button>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      <div class="register">
        <span><el-link type="primary" @click="goRegister()">还没账号，去注册</el-link></span>
      </div>
      <div class="login-btn">
        <el-button type="primary" round size="large" style="width: 120px" class="log-btn" @click="login()">登录
        </el-button>
      </div>
    </div>
  </div>

</template>

<script setup>
import {ref, reactive} from 'vue'
import {useRouter} from 'vue-router';
import {ElMessage} from 'element-plus'
import {useStore} from 'vuex';
import {doLoginWithAccount, doLoginWithEmail, sendCode} from '@/http/api/user'

const router = useRouter()
const activeName = ref('first')
//用户信息更新
const store = useStore()


//登录
const userInfo = reactive({
  account: '123456',
  password: '000000',
  email: '',
  code: '',
})
const login = async () => {
  if (activeName.value === 'first') {
    try {
      const response = await doLoginWithAccount(userInfo.account, userInfo.password);
      console.log(response)

      if (response.data.msg === "登录成功") {
        await store.dispatch('user/login', response.data.data);
        // 根据角色跳转到不同页面
        const userRole = response.data.data.role || '0';
        if (userRole === '1') {
          await router.push('/jobManagement');
        } else {
          await router.push('/employeeTask');
        }
      } else {
        ElMessage({
          message: '信息输入错误，登录失败',
          type: 'error',
          plain: true,
        })
      }
    } catch (error) {
      console.error("登录失败" + error);
      ElMessage({
        message: '网络错误，登录失败',
        type: 'error',
        plain: true,
      })
    }
  } else if (activeName.value === 'second') {
    try {
      const res = await doLoginWithEmail(userInfo.email, userInfo.code);
      if (res.data.msg === "登录成功") {
        await store.dispatch('user/login', res.data.data);
        // 根据角色跳转到不同页面
        const userRole = res.data.data.role || '0';
        if (userRole === '1') {
          await router.push('/jobManagement');
        } else {
          await router.push('/employeeTask');
        }
      } else {
        ElMessage({
          message: '信息输入错误，登录失败',
          type: 'error',
          plain: true,
        })
      }
    } catch (error) {
      console.error("登录失败" + error);
      ElMessage({
        message: '网络错误，登录失败',
        type: 'error',
        plain: true,
      })
    }
  }
}
//获取验证码
const getCode = async () => {
  try {
    const response = await sendCode(userInfo.email);
    console.log(response);

    if (response.data.success) {
      ElMessage({
        message: '验证码发送成功，请查收',
        type: 'success',
        plain: true,
      })
    } else {
      ElMessage({
        message: '验证码发送失败，请查收',
        type: 'error',
        plain: true,
      })
    }
  } catch (error) {
    console.log("发送失败：" + error);
    ElMessage({
      message: '网络错误',
      type: 'error',
      plain: true,
    })
  }
}

const goRegister = () => {
  router.push('/register')
}


</script>

<style scoped>
.login {
  position: relative;
  height: 100vh;
  background-image: url(../assets/login.jpg);
  filter: blur(0);
}

.login-box {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-around;
  right: 15%;
  top: 20%;
  height: 68%;
  width: 25%;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  border: 3px solid rgba(255, 255, 255, 0.8);
}

.name {
  font-size: 28px;
  font-weight: 600;
  margin-top: 15px;
}

.info {
  width: 70%;
}

.input-box {
  margin: 15px;
}

.remenber span {
  font-size: 12px;
}

.getCode {
  font-size: 10px;
  height: 40px;
  display: flex;
  justify-content: end;
  align-items: center;
  padding-right: 15px;
}
</style>
