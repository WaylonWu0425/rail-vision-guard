<template>
  <div class="login-container">
    <div class="login-box">
      <div class="app-name">车站异物检测系统</div>

      <div class="login-content">
        <el-tabs
            v-model="activeName"
            class="login-tabs"
            @tab-click="handleClick"
            :stretch="true"
        >
          <!-- 账户登录 -->
          <el-tab-pane label="账户登录" name="first">
            <div class="input-group">
              <div class="input-item">
                <span class="input-label">账户</span>
                <el-input
                    v-model="userInfo.account"
                    placeholder="请输入账户"
                    class="custom-input"
                    :clearable="true"
                />
              </div>
              <div class="input-item">
                <span class="input-label">密码</span>
                <el-input
                    v-model="userInfo.password"
                    type="password"
                    placeholder="请输入密码"
                    class="custom-input"
                    :show-password="true"
                />
              </div>
              <div class="remember-me">
                <el-checkbox v-model="checked1" label="记住密码" size="large" />
              </div>
            </div>
          </el-tab-pane>

          <!-- 邮箱登录 -->
          <el-tab-pane label="邮箱登录" name="second">
            <div class="input-group">
              <div class="input-item">
                <span class="input-label">邮箱</span>
                <el-input
                    v-model="userInfo.email"
                    placeholder="请输入邮箱"
                    class="custom-input"
                    :clearable="true"
                />
              </div>
              <div class="input-item">
                <span class="input-label">验证码</span>
                <el-input
                    v-model="userInfo.code"
                    placeholder="请输入验证码"
                    class="custom-input code-input"
                />
              </div>
              <div class="code-actions">
                <el-button
                    type="primary"
                    @click="getCode()"
                    :loading="codeLoading"
                    :disabled="!userInfo.email"
                    class="code-btn"
                >
                  {{ codeLoading ? '发送中...' : '获取验证码' }}
                </el-button>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <div class="register-link">
          <el-link
              type="primary"
              :underline="false"
              @click="goRegister()"
              class="register-text"
          >
            还没账号？立即注册
          </el-link>
        </div>

        <div class="login-actions">
          <el-button
              type="primary"
              round
              size="large"
              @click="login()"
              class="login-btn"
              :loading="loginLoading"
          >
            {{ loginLoading ? '登录中...' : '登录' }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus'
import { useStore } from 'vuex';
import { doLoginWithAccount, doLoginWithEmail, sendCode } from '@/http/api/user'

const router = useRouter()
const store = useStore()

// 状态管理
const activeName = ref('first')
const checked1 = ref(false)
const codeLoading = ref(false)
const loginLoading = ref(false)

// 用户信息
const userInfo = reactive({
  account: '',
  password: '',
  email: '',
  code: '',
})

// 登录函数
const login = async () => {
  loginLoading.value = true

  try {
    let response

    if (activeName.value === 'first') {
      // 账户密码登录
      if (!userInfo.account || !userInfo.password) {
        ElMessage.warning('请输入账户和密码')
        loginLoading.value = false
        return
      }

      response = await doLoginWithAccount(userInfo.account, userInfo.password);
    } else if (activeName.value === 'second') {
      // 邮箱验证码登录
      if (!userInfo.email || !userInfo.code) {
        ElMessage.warning('请输入邮箱和验证码')
        loginLoading.value = false
        return
      }

      response = await doLoginWithEmail(userInfo.email, userInfo.code);
    }

    if (response.data.msg === "登录成功") {
      store.dispatch('user/login', response.data.data);

      // 根据角色跳转到不同页面
      const userRole = response.data.data.role || '0';
      if (userRole === '1') {
        router.push('/jobManagement');
      } else {
        router.push('/employeeTask');
      }

      ElMessage.success('登录成功')
    } else {
      ElMessage.error(response.data.msg || '登录失败')
    }
  } catch (error) {
    console.error("登录失败:", error);
    ElMessage.error('网络错误，登录失败')
  } finally {
    loginLoading.value = false
  }
}

// 获取验证码
const getCode = async () => {
  if (!userInfo.email) {
    ElMessage.warning('请输入邮箱')
    return
  }

  // 简单的邮箱格式验证
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(userInfo.email)) {
    ElMessage.warning('请输入有效的邮箱地址')
    return
  }

  codeLoading.value = true

  try {
    const response = await sendCode(userInfo.email);

    if (response.data.success) {
      ElMessage.success('验证码已发送，请查收邮箱')
    } else {
      ElMessage.error(response.data.msg || '验证码发送失败')
    }
  } catch (error) {
    console.error("验证码发送失败:", error);
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    codeLoading.value = false
  }
}

// 跳转到注册页面
const goRegister = () => {
  router.push('/register')
}

// 标签切换处理
const handleClick = () => {
  // 清空表单数据
  userInfo.account = ''
  userInfo.password = ''
  userInfo.email = ''
  userInfo.code = ''
}
</script>

<style scoped>
.login-container {
  position: relative;
  height: 100vh;
  width: 100vw;
  background-image: url(../../assets/ruanzhu_test/login.png);
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-box {
  width: 420px;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  overflow: hidden;
  padding: 40px;
}

.app-name {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  text-align: center;
  margin-bottom: 40px;
  position: relative;
  padding-bottom: 15px;
}

.app-name::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  border-radius: 2px;
}

.login-content {
  width: 100%;
}

.login-tabs {
  margin-bottom: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 4px;
}

.custom-input {
  width: 100%;
}

.custom-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  padding: 10px 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.custom-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

.remember-me {
  margin-top: 8px;
  display: flex;
  align-items: center;
}

.code-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: -4px;
}

.code-btn {
  border-radius: 8px;
  padding: 8px 20px;
  font-size: 13px;
}

.register-link {
  text-align: center;
  margin: 24px 0;
}

.register-text {
  font-size: 14px;
  font-weight: 500;
  transition: color 0.3s ease;
}

.register-text:hover {
  color: #337ecc !important;
}

.login-actions {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.login-btn {
  width: 160px;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-box {
    width: 90%;
    max-width: 400px;
    padding: 30px 25px;
    margin: 20px;
  }

  .app-name {
    font-size: 24px;
    margin-bottom: 30px;
  }

  .input-group {
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .login-box {
    padding: 25px 20px;
  }

  .app-name {
    font-size: 22px;
  }

  .login-btn {
    width: 140px;
    height: 42px;
  }
}
</style>