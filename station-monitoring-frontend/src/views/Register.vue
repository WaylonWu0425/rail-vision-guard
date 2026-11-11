<template>
  <AuthShell panel-label="创建视界巡警账号">
    <header class="form-heading">
      <p>账号注册</p>
      <h2>创建视界巡警账号</h2>
      <span>注册后即可登录视频监控与告警处置工作台</span>
    </header>

    <el-tabs v-model="activeName" class="auth-tabs" stretch @tab-change="clearFormError">
      <el-tab-pane label="账号注册" name="account">
        <el-form ref="accountFormRef" :model="userInfo" :rules="accountRules" label-position="top"
                 class="auth-form" @submit.prevent="register">
          <el-form-item label="账号" prop="account">
            <el-input v-model.trim="userInfo.account" name="username" autocomplete="username"
                      placeholder="5–10位字母或数字" size="large" @input="clearFormError" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="userInfo.password" name="new-password" type="password" show-password
                      autocomplete="new-password" placeholder="6–15位且不能包含空格" size="large" @input="clearFormError" />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="userInfo.confirmPassword" name="confirm-password" type="password" show-password
                      autocomplete="new-password" placeholder="请再次输入密码" size="large" @input="clearFormError" />
          </el-form-item>
          <p v-if="formError" class="form-error" role="alert" aria-live="polite">{{ formError }}</p>
          <el-button native-type="submit" type="primary" size="large" class="submit-button"
                     :loading="submitting" :disabled="submitting">
            {{ submitting ? '正在创建…' : '创建账号' }}
          </el-button>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="邮箱注册" name="email">
        <el-form ref="emailFormRef" :model="userInfo" :rules="emailRules" label-position="top"
                 class="auth-form" @submit.prevent="register">
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
            {{ submitting ? '正在创建…' : '使用邮箱注册' }}
          </el-button>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <p class="login-link">已有账号？<el-link type="primary" @click="router.push('/login')">返回登录</el-link></p>
  </AuthShell>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AuthShell from '@/components/AuthShell.vue'
import { useEmailCodeCountdown } from '@/composables/useEmailCodeCountdown'
import { registerWithAccount, registerWithEmail, sendCode } from '@/http/api/user'

const router = useRouter()
const activeName = ref('account')
const accountFormRef = ref(null)
const emailFormRef = ref(null)
const submitting = ref(false)
const sendingCode = ref(false)
const formError = ref('')
const codeHint = ref('')
const userInfo = reactive({ account: '', password: '', confirmPassword: '', email: '', code: '' })
const { remainingSeconds, codeButtonText, startCountdown } = useEmailCodeCountdown(60)

const validatePasswordConfirmation = (rule, value, callback) => {
  if (!value) callback(new Error('请再次输入密码'))
  else if (value !== userInfo.password) callback(new Error('两次输入的密码不一致'))
  else callback()
}
const accountRules = {
  account: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9]{5,10}$/, message: '账号应为5–10位字母或数字', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { pattern: /^\S{6,15}$/, message: '密码应为6–15位且不能包含空格', trigger: 'blur' }
  ],
  confirmPassword: [{ validator: validatePasswordConfirmation, trigger: ['blur', 'change'] }]
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

const register = async () => {
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
      ? await registerWithAccount(userInfo.account, userInfo.password)
      : await registerWithEmail(userInfo.email, userInfo.code)
    if (!response.data?.success) {
      formError.value = response.data?.message || '注册失败，请检查输入后重试'
      return
    }
    ElMessage.success('账号创建成功，请登录')
    await router.push('/login')
  } catch (error) {
    formError.value = error.response?.data?.message || error.message || '注册请求失败，请检查网络和后端服务'
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
.form-heading { margin-bottom: 18px; }
.form-heading > p { margin: 0 0 7px; color: #315a7e; font-size: 13px; font-weight: 650; }
.form-heading h2 { margin: 0; color: #182f47; font-size: 28px; line-height: 1.4; font-weight: 650; }
.form-heading > span { display: block; margin-top: 8px; color: #667085; font-size: 14px; line-height: 1.6; }
.auth-tabs :deep(.el-tabs__header) { margin-bottom: 22px; }
.auth-tabs :deep(.el-tabs__item) { height: 44px; color: #475467; font-size: 15px; }
.auth-tabs :deep(.el-tabs__item.is-active) { color: #243e5c; font-weight: 600; }
.auth-tabs :deep(.el-tabs__active-bar) { height: 2px; background: #243e5c; }
.auth-form :deep(.el-form-item) { margin-bottom: 17px; }
.auth-form :deep(.el-form-item__label) { padding-bottom: 8px; color: #344054; font-size: 15px; font-weight: 550; line-height: 1.4; }
.auth-form :deep(.el-input__wrapper) { min-height: 48px; padding: 0 14px; border: 1px solid #7c8797; border-radius: 8px; box-shadow: none; transition: border-color 160ms, box-shadow 160ms; }
.auth-form :deep(.el-input__wrapper:hover) { border-color: #526579; }
.auth-form :deep(.el-input__wrapper.is-focus) { border-color: #315a7e; box-shadow: 0 0 0 3px rgba(49, 90, 126, .14); }
.auth-form :deep(.el-input__inner) { color: #182230; font-size: 16px; }
.auth-form :deep(.el-form-item.is-error .el-input__wrapper) { border-color: #b42318; }
.auth-form :deep(.el-form-item__error) { padding-top: 5px; color: #b42318; font-size: 13px; }
.code-row { width: 100%; display: grid; grid-template-columns: minmax(0, 1fr) 126px; gap: 10px; }
.code-button { height: 48px; border-color: #98a2b3; color: #243e5c; }
.code-button:hover:not(:disabled), .code-button:focus-visible { border-color: #315a7e; color: #243e5c; background: #f4f7fa; }
.code-hint { margin: -6px 0 14px; color: #475467; font-size: 13px; line-height: 1.5; }
.form-error { margin: -4px 0 14px; padding: 10px 12px; color: #912018; background: #fef3f2; border: 1px solid #fecdca; border-radius: 7px; font-size: 13px; line-height: 1.5; }
.submit-button { width: 100%; min-height: 48px; margin-top: 2px; border: 0; border-radius: 8px; background: #243e5c; font-size: 16px; font-weight: 600; }
.submit-button:hover, .submit-button:focus-visible { background: #1b3049; }
.login-link { display: flex; justify-content: center; align-items: center; gap: 5px; margin: 22px 0 0; color: #667085; font-size: 14px; }
.login-link :deep(.el-link) { color: #315a7e; font-size: 14px; font-weight: 550; }
@media (max-width: 480px) {
  .form-heading h2 { font-size: 25px; }
  .code-row { grid-template-columns: minmax(0, 1fr) 112px; gap: 8px; }
  .code-button { padding: 0 10px; font-size: 13px; }
}
</style>
