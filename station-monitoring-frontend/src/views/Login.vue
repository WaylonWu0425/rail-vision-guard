<template>
  <LoginWorkspaceShell>
    <header class="form-heading">
      <p><el-icon aria-hidden="true"><Lock /></el-icon>视界巡警工作台</p>
      <h2>登录工作台</h2>
      <span>访问监控画面、告警与录像。</span>
    </header>

    <el-tabs v-model="activeName" class="auth-tabs" stretch @tab-change="clearFormError">
      <el-tab-pane label="账号密码" name="account">
        <el-form ref="accountFormRef" :model="userInfo" :rules="accountRules" label-position="top"
                 class="auth-form" @submit.prevent="login">
          <el-form-item label="账号" prop="account">
            <el-input v-model.trim="userInfo.account" name="username" autocomplete="username"
                      placeholder="请输入5–10位字母或数字" size="large" @input="clearFormError" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="userInfo.password" name="password" type="password" show-password
                      autocomplete="current-password" placeholder="请输入密码" size="large" @input="clearFormError" />
          </el-form-item>
          <div class="form-options"><el-checkbox v-model="rememberAccount">记住账号</el-checkbox><span>公共设备请勿勾选</span></div>
          <p v-if="formError" class="form-error" role="alert" aria-live="polite">{{ formError }}</p>
          <el-button native-type="submit" type="primary" size="large" class="submit-button"
                     :loading="submitting" :disabled="submitting">
            {{ submitting ? '正在登录…' : '登录工作台' }}
          </el-button>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="邮箱验证码" name="email">
        <el-form ref="emailFormRef" :model="userInfo" :rules="emailRules" label-position="top"
                 class="auth-form" @submit.prevent="login">
          <el-form-item label="邮箱" prop="email">
            <el-input v-model.trim="userInfo.email" name="email" type="email" autocomplete="email"
                      placeholder="请输入邮箱" size="large" @input="clearFormError" />
          </el-form-item>
          <el-form-item label="验证码" prop="code">
            <div class="code-row">
              <el-input v-model.trim="userInfo.code" name="one-time-code" inputmode="numeric"
                        maxlength="6" autocomplete="one-time-code" placeholder="6位验证码"
                        size="large" @input="clearFormError" />
              <el-button class="code-button" :loading="sendingCode"
                         :disabled="sendingCode || remainingSeconds > 0" @click="getCode">
                {{ sendingCode ? '发送中…' : codeButtonText }}
              </el-button>
            </div>
          </el-form-item>
          <p v-if="codeHint" class="code-hint" aria-live="polite">{{ codeHint }}</p>
          <p v-if="formError" class="form-error" role="alert" aria-live="polite">{{ formError }}</p>
          <el-button native-type="submit" type="primary" size="large" class="submit-button"
                     :loading="submitting" :disabled="submitting">
            {{ submitting ? '正在登录…' : '登录工作台' }}
          </el-button>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <p class="register-link">还没有账号？<el-link type="primary" @click="router.push('/register')">创建账号</el-link></p>
  </LoginWorkspaceShell>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { Lock } from '@element-plus/icons-vue'
import LoginWorkspaceShell from '@/components/LoginWorkspaceShell.vue'
import { useEmailCodeCountdown } from '@/composables/useEmailCodeCountdown'
import { doLoginWithAccount, doLoginWithEmail, sendCode } from '@/http/api/user'
import { preloadCorePages } from '@/utils/preloadCorePages'

const router = useRouter()
const route = useRoute()
const store = useStore()
const activeName = ref('account')
const accountFormRef = ref(null)
const emailFormRef = ref(null)
const submitting = ref(false)
const sendingCode = ref(false)
const formError = ref('')
const codeHint = ref('')
const savedAccount = localStorage.getItem('remembered-account') || ''
const rememberAccount = ref(Boolean(savedAccount))
const userInfo = reactive({ account: savedAccount, password: '', email: '', code: '' })
const { remainingSeconds, codeButtonText, startCountdown } = useEmailCodeCountdown(60)

const accountRules = {
  account: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9]{5,10}$/, message: '账号应为5–10位字母或数字', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { pattern: /^\S{6,15}$/, message: '密码应为6–15位且不能包含空格', trigger: 'blur' }
  ]
}
const emailRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效邮箱', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '请输入6位数字验证码', trigger: 'blur' }
  ]
}

const clearFormError = () => { formError.value = '' }
const maskEmail = (email) => {
  const [name, domain] = email.split('@')
  const visible = name.slice(0, Math.min(2, name.length))
  return `${visible}${'*'.repeat(Math.max(2, name.length - visible.length))}@${domain}`
}

const login = async () => {
  if (submitting.value) return
  const formRef = activeName.value === 'account' ? accountFormRef.value : emailFormRef.value
  try {
    await formRef?.validate()
  } catch (error) {
    return
  }

  submitting.value = true
  formError.value = ''
  try {
    const response = activeName.value === 'account'
      ? await doLoginWithAccount(userInfo.account, userInfo.password)
      : await doLoginWithEmail(userInfo.email, userInfo.code)
    if (response.data?.msg !== '登录成功' || !response.data?.data) {
      formError.value = response.data?.msg || '登录失败，请检查输入后重试'
      return
    }
    if (rememberAccount.value && activeName.value === 'account') {
      localStorage.setItem('remembered-account', userInfo.account)
    } else if (activeName.value === 'account') {
      localStorage.removeItem('remembered-account')
    }
    userInfo.password = ''
    userInfo.code = ''
    await store.dispatch('user/login', response.data.data)
    const redirect = typeof route.query.redirect === 'string' && route.query.redirect.startsWith('/')
      && !route.query.redirect.startsWith('//') ? route.query.redirect : '/'
    await router.replace(redirect)
    preloadCorePages()
  } catch (error) {
    formError.value = error.response?.data?.msg || error.response?.data?.message
      || error.message || '登录请求失败，请检查网络和后端服务'
  } finally {
    submitting.value = false
  }
}

const getCode = async () => {
  if (sendingCode.value || remainingSeconds.value > 0) return
  try {
    await emailFormRef.value?.validateField('email')
  } catch (error) {
    return
  }
  sendingCode.value = true
  formError.value = ''
  try {
    const response = await sendCode(userInfo.email)
    if (!response.data?.success) throw new Error(response.data?.message || '验证码发送失败')
    startCountdown()
    codeHint.value = `验证码已发送至 ${maskEmail(userInfo.email)}，5分钟内有效。`
    ElMessage.success('验证码已发送')
  } catch (error) {
    formError.value = error.response?.data?.message || error.message || '验证码发送失败，请稍后重试'
  } finally {
    sendingCode.value = false
  }
}
</script>

<style scoped>
.form-heading { margin-bottom: 29px; }
.form-heading > p { margin: 0 0 16px; display: flex; align-items: center; gap: 7px; color: #657f96; font-size: 12px; font-weight: 500; }
.form-heading > p :deep(.el-icon) { color: #718eab; font-size: 13px; }
.form-heading h2 { margin: 0 0 10px; color: #203c59; font-size: 32px; line-height: 1.35; letter-spacing: .5px; font-weight: 600; }
.form-heading > span { display: block; color: #5d748a; font-size: 15px; line-height: 1.8; }
.auth-tabs :deep(.el-tabs__header) { margin-bottom: 26px; padding: 4px; border: 1px solid #e3ebf2; border-radius: 7px; background: #f4f7fb; }
.auth-tabs :deep(.el-tabs__nav-wrap::after) { display: none; }
.auth-tabs :deep(.el-tabs__nav) { width: 100%; border: 0; }
.auth-tabs :deep(.el-tabs__item) { height: 40px; border: 1px solid transparent; border-radius: 4px; color: #6f8396; font-size: 14px; }
.auth-tabs :deep(.el-tabs__item.is-active) { border-color: #dde8f2; background: #fff; box-shadow: 0 1px 3px #2c577910; color: #1976d2; font-weight: 600; }
.auth-tabs :deep(.el-tabs__active-bar) { display: none; }
.auth-form :deep(.el-form-item) { margin-bottom: 21px; }
.auth-form :deep(.el-form-item__label) { padding-bottom: 9px; color: #40586e; font-size: 14px; font-weight: 500; line-height: 1.4; }
.auth-form :deep(.el-input__wrapper) { min-height: 50px; padding: 0 14px; border: 1px solid #cfdde9; border-radius: 5px; box-shadow: none; transition: border-color 160ms, box-shadow 160ms; }
.auth-form :deep(.el-input__wrapper:hover) { border-color: #8db6d7; }
.auth-form :deep(.el-input__wrapper.is-focus) { border-color: #1976d2; box-shadow: 0 0 0 3px #1976d210; }
.auth-form :deep(.el-input__inner) { color: #2c4760; font-size: 16px; }
.auth-form :deep(.el-input__inner::placeholder) { color: #7c90a2; font-size: 14px; }
.auth-form :deep(.el-form-item.is-error .el-input__wrapper) { border-color: #b42318; }
.auth-form :deep(.el-form-item__error) { padding-top: 5px; color: #b42318; font-size: 13px; }
.form-options { display: flex; justify-content: space-between; align-items: center; margin: -1px 0 27px; }
.form-options :deep(.el-checkbox) { height: auto; margin: 0; color: #61788d; font-size: 13px; }
.form-options > span { color: #788da0; font-size: 12px; }
.code-row { width: 100%; display: grid; grid-template-columns: minmax(0, 1fr) 126px; gap: 10px; }
.code-button { height: 50px; border-color: #cfdde9; border-radius: 5px; color: #1976d2; }
.code-button:hover:not(:disabled), .code-button:focus-visible { border-color: #1976d2; color: #1565c0; background: #f4f9fe; }
.code-hint { margin: -6px 0 14px; color: #61788d; font-size: 13px; line-height: 1.5; }
.form-error { margin: -4px 0 14px; padding: 10px 12px; color: #912018; background: #fef3f2; border: 1px solid #fecdca; border-radius: 7px; font-size: 13px; line-height: 1.5; }
.submit-button { width: 100%; min-height: 50px; margin-top: 2px; border: 0; border-radius: 5px; background: #1976d2; font-size: 15px; font-weight: 600; }
.submit-button:hover, .submit-button:focus-visible { background: #1565c0; }
.register-link { display: flex; justify-content: center; align-items: center; gap: 5px; margin: 22px 0 0; color: #788da0; font-size: 13px; }
.register-link :deep(.el-link) { color: #1976d2; font-size: 13px; font-weight: 500; }
@media (max-width: 480px) {
  .form-heading h2 { font-size: 25px; }
  .code-row { grid-template-columns: minmax(0, 1fr) 112px; gap: 8px; }
  .code-button { padding: 0 10px; font-size: 13px; }
}
</style>
