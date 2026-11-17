<template>
  <main class="ai-page">
    <section class="workspace">
      <aside class="assistant-panel" :class="{ open: sidebarOpen }" aria-label="AI 助手功能">
        <div class="assistant-brand">
          <div class="brand-icon"><el-icon><MagicStick /></el-icon></div>
          <div class="brand-copy">
            <span class="brand-eyebrow">视界巡警 · 车站视频监控平台</span>
            <h1>智能运维助手</h1>
            <p>设备接入、智能检测、告警核查与录像回溯</p>
          </div>
          <button type="button" class="sidebar-close" aria-label="关闭助手菜单" @click="sidebarOpen = false">
            <el-icon><Close /></el-icon>
          </button>
        </div>

        <section class="panel-section">
          <h2>常用运维场景</h2>
          <button v-for="action in quickActions" :key="action.label" type="button" class="quick-action"
                  :disabled="loading" @click="handleQuickAction(action.prompt)">
            <span>{{ action.label }}</span><el-icon><ArrowRight /></el-icon>
          </button>
        </section>

        <section class="panel-section capability-section">
          <button type="button" class="panel-heading" :aria-expanded="capabilitiesExpanded"
                  @click="capabilitiesExpanded = !capabilitiesExpanded">
            <span>系统知识范围</span>
            <el-icon :class="{ expanded: capabilitiesExpanded }"><ArrowDown /></el-icon>
          </button>
          <ul v-show="capabilitiesExpanded" class="capability-list">
            <li v-for="item in capabilities" :key="item"><el-icon><Check /></el-icon><span>{{ item }}</span></li>
          </ul>
        </section>

        <div class="scope-note">
          <el-icon><InfoFilled /></el-icon>
          <div><strong>使用说明</strong><span>助手提供操作与排查建议。设备操作和告警处置由值守人员核查确认。</span></div>
        </div>
      </aside>
      <button v-if="sidebarOpen" type="button" class="sidebar-backdrop" aria-label="关闭助手菜单" @click="sidebarOpen = false"></button>

      <section class="chat-card" aria-label="AI 对话区">
        <div class="chat-toolbar">
          <div class="conversation-title">
            <button type="button" class="mobile-sidebar-toggle" aria-label="打开助手菜单" @click="sidebarOpen = true">
              <el-icon><Menu /></el-icon>
            </button>
            <el-icon><ChatDotRound /></el-icon>
            <div><strong>运维会话</strong><span>{{ messages.length ? `${messages.length} 条消息` : '等待输入系统问题' }}</span></div>
          </div>
          <div class="toolbar-actions">
            <div class="service-status" :class="serviceState" role="status" aria-live="polite">
              <span class="status-dot" aria-hidden="true"></span>
              <div><strong>{{ serviceStatusText }}</strong></div>
            </div>
            <el-button text :icon="Delete" :disabled="messages.length === 0 || loading" @click="clearConversation">清空对话</el-button>
          </div>
        </div>

        <div ref="messagesContainer" class="messages" role="log" aria-live="polite" aria-relevant="additions"
             @scroll.passive="handleMessagesScroll">
          <div v-if="messages.length === 0" class="welcome">
            <div class="welcome-icon"><el-icon><MagicStick /></el-icon></div>
            <h2>视界巡警运维知识助手</h2>
            <p>查询摄像头接入、检测任务、告警核查和录像回看等操作步骤。</p>
            <div class="prompt-grid">
              <button v-for="example in exampleQuestions" :key="example" type="button" :disabled="loading"
                      @click="handleQuickAction(example)">
                <el-icon><ChatLineRound /></el-icon><span>{{ example }}</span>
              </button>
            </div>
          </div>

          <article v-for="message in messages" :key="message.id" class="message-row" :class="message.role">
            <div class="message-avatar"><el-icon v-if="message.role === 'assistant'"><MagicStick /></el-icon><span v-else>我</span></div>
            <div class="message-body">
              <div v-if="message.role === 'assistant'" class="message-bubble markdown-body"
                   v-html="renderMarkdown(message.content)"></div>
              <div v-else class="message-bubble">{{ message.content }}</div>
              <div class="message-meta">
                <span>{{ formatTime(message.timestamp) }}</span>
                <button v-if="message.role === 'assistant'" type="button" class="copy-button" @click="copyMessage(message.content)">
                  <el-icon><CopyDocument /></el-icon>复制
                </button>
              </div>
            </div>
          </article>

          <article v-if="loading" class="message-row assistant">
            <div class="message-avatar"><el-icon><MagicStick /></el-icon></div>
            <div class="message-body"><div class="message-bubble typing"><span></span><span></span><span></span><em>正在生成运维建议</em></div></div>
          </article>

          <div v-if="lastError" class="error-card" role="alert">
            <el-icon><WarningFilled /></el-icon>
            <div><strong>回答生成失败</strong><span>{{ lastError }}</span></div>
            <el-button :icon="Refresh" :loading="loading" @click="retryLastQuestion">重试</el-button>
          </div>
        </div>

        <button v-if="showScrollLatest" type="button" class="scroll-latest" @click="scrollToBottom(true)">
          <el-icon><ArrowDown /></el-icon><span>回到最新消息</span>
        </button>

        <div class="composer">
          <div class="composer-inner">
            <label for="ai-question">系统运维问题</label>
            <div class="composer-box" :class="{ focused: inputFocused }">
              <el-input ref="questionInput" id="ai-question" v-model="inputMessage" type="textarea"
                        :autosize="{ minRows: 2, maxRows: 6 }" maxlength="4000" resize="none"
                        placeholder="输入系统运维问题，例如：YOLO 检测服务未就绪如何排查？"
                        :disabled="loading || serviceState === 'unavailable'" @focus="inputFocused = true"
                        @blur="inputFocused = false" @compositionstart="isComposing = true"
                        @compositionend="isComposing = false" @keydown.enter.exact="handleEnter" />
              <div class="composer-actions">
                <span>Enter 发送 · Shift + Enter 换行</span>
                <el-button type="primary" :icon="Promotion" :loading="loading" :disabled="!canSend" @click="sendMessage()">发送</el-button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, ArrowRight, ChatDotRound, ChatLineRound, Check, Close, CopyDocument, Delete,
  InfoFilled, MagicStick, Menu, Promotion, Refresh, WarningFilled } from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'
import { getAiHealth, sendAiChat } from '@/http/api/aiChat'

const markdown = new MarkdownIt({ html: false, breaks: true, linkify: true, typographer: false })
const defaultLinkOpen = markdown.renderer.rules.link_open || ((tokens, index, options, env, self) => self.renderToken(tokens, index, options))
markdown.renderer.rules.link_open = (tokens, index, options, env, self) => {
  tokens[index].attrSet('target', '_blank')
  tokens[index].attrSet('rel', 'noopener noreferrer')
  return defaultLinkOpen(tokens, index, options, env, self)
}
markdown.disable('image')

const inputMessage = ref('')
const inputFocused = ref(false)
const questionInput = ref(null)
const isComposing = ref(false)
const messages = ref([])
const messagesContainer = ref(null)
const loading = ref(false)
const lastError = ref('')
const lastQuestion = ref('')
const serviceState = ref('checking')
const capabilitiesExpanded = ref(false)
const sidebarOpen = ref(false)
const showScrollLatest = ref(false)
let healthCheckTimer = null

const capabilities = [
  '摄像头接入、在线状态与取流配置',
  '实时预览、截图与手动录像',
  '人员与车辆检测任务',
  '告警记录、截图核查与处置状态',
  '录像检索、回放与告警时间关联',
  '固定机位画面变化检测的设置与限制'
]
const quickActions = [
  { label: '查找告警关联录像', prompt: '请说明值守人员如何根据摄像头和告警发生时间查找关联录像，以及没有覆盖该时段的录像时如何记录。' },
  { label: '排查摄像头离线', prompt: '视界巡警实时预览页显示摄像头离线。请按照供电与网络、设备地址、RTSP 配置、后端服务和页面状态的顺序给出排查步骤。' },
  { label: '设置画面变化检测', prompt: '请说明视界巡警固定机位基线比对的设置步骤、使用条件，以及何时需要重新采集空场景基准。' },
  { label: '规范告警处置', prompt: '请结合告警类型、摄像头、发生时间、截图、处理状态和关联录像，给出视界巡警的告警核查与处置流程。' }
]
const exampleQuestions = [
  '如何从实时预览录制并回看录像？',
  '固定枪机为什么不显示云台和光学变焦控制？',
  '检测画面打不开时怎么排查？',
  '如何根据告警发生时间定位对应录像？'
]

const serviceStatusText = computed(() => ({ checking: '正在连接助手', configured: '助手已配置',
  verified: '助手可用', unavailable: '助手未配置', error: '助手暂不可用' }[serviceState.value]))
const canSend = computed(() => inputMessage.value.trim().length > 0 && !loading.value && serviceState.value !== 'unavailable')
const renderMarkdown = (content) => markdown.render(content || '')

const checkService = async (showChecking = false) => {
  const connectionVerified = serviceState.value === 'verified'
  if (showChecking) serviceState.value = 'checking'
  try {
    const data = (await getAiHealth()).data || {}
    serviceState.value = data.configured ? (connectionVerified ? 'verified' : 'configured') : 'unavailable'
  } catch (error) {
    serviceState.value = 'error'
  }
}

const handleServiceRecovery = () => checkService(false)

const sendMessage = async (question = inputMessage.value.trim()) => {
  const text = question.trim()
  if (!text || loading.value) return
  lastQuestion.value = text
  lastError.value = ''
  messages.value.push(createMessage('user', text))
  inputMessage.value = ''
  loading.value = true
  await scrollToBottom(true)
  try {
    const history = messages.value.map(({ role, content }) => ({ role, content }))
    const result = (await sendAiChat(history)).data?.data
    if (!result?.content) throw new Error('AI服务返回了空内容')
    messages.value.push(createMessage('assistant', result.content))
    serviceState.value = 'verified'
  } catch (error) {
    lastError.value = error.message || 'AI服务暂时不可用，请稍后重试'
    serviceState.value = 'error'
  } finally {
    loading.value = false
    await scrollToBottom(false)
  }
}

const retryLastQuestion = () => {
  if (!lastQuestion.value || loading.value) return
  const lastMessage = messages.value[messages.value.length - 1]
  if (lastMessage?.role === 'user' && lastMessage.content === lastQuestion.value) messages.value.pop()
  sendMessage(lastQuestion.value)
}
const handleQuickAction = async (prompt) => {
  if (loading.value) return
  inputMessage.value = prompt
  sidebarOpen.value = false
  await nextTick()
  questionInput.value?.focus()
}
const clearConversation = async () => {
  if (!messages.value.length || loading.value) return
  try {
    await ElMessageBox.confirm('清空后无法恢复当前页面中的对话记录。', '清空当前对话', {
      confirmButtonText: '确认清空', cancelButtonText: '取消', type: 'warning'
    })
    messages.value = []
    lastError.value = ''
    lastQuestion.value = ''
    showScrollLatest.value = false
  } catch (error) {
    // 用户取消时保持原对话不变。
  }
}
const copyMessage = async (content) => {
  try { await navigator.clipboard.writeText(content); ElMessage.success('回答已复制') }
  catch (error) { ElMessage.error('复制失败，请手动选择文本') }
}
const createMessage = (role, content) => ({ id: `${Date.now()}-${Math.random().toString(16).slice(2)}`, role, content, timestamp: Date.now() })
const handleMessagesScroll = () => {
  const el = messagesContainer.value
  if (!el) return
  showScrollLatest.value = el.scrollHeight - el.scrollTop - el.clientHeight > 120
}
const scrollToBottom = async (force = false) => {
  await nextTick()
  const el = messagesContainer.value
  if (!el || (!force && showScrollLatest.value)) return
  el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  showScrollLatest.value = false
}
const handleEnter = (event) => {
  if (event.isComposing || isComposing.value || event.keyCode === 229) return
  event.preventDefault()
  sendMessage()
}
const handleGlobalKeydown = (event) => { if (event.key === 'Escape') sidebarOpen.value = false }
const formatTime = (timestamp) => new Date(timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })
onMounted(() => {
  checkService(true)
  healthCheckTimer = window.setInterval(() => checkService(false), 30000)
  window.addEventListener('online', handleServiceRecovery)
  window.addEventListener('focus', handleServiceRecovery)
  window.addEventListener('keydown', handleGlobalKeydown)
})
onBeforeUnmount(() => {
  if (healthCheckTimer) window.clearInterval(healthCheckTimer)
  window.removeEventListener('online', handleServiceRecovery)
  window.removeEventListener('focus', handleServiceRecovery)
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<style scoped>
.ai-page { --primary:var(--primary-color,#1976d2); --primary-hover:var(--primary-dark,#1565c0); --ink:#1e293b; --muted:#64748b; --line:#e2e8f0; width:100%; height:100%; min-height:0; padding:1%; box-sizing:border-box; display:flex; flex-direction:column; overflow:hidden; color:var(--ink); background:radial-gradient(circle at 92% 3%,rgba(25,118,210,.08),transparent 27%),#f5f7fb; }
.service-status { min-width:174px; padding:8px 11px; display:flex; align-items:center; gap:9px; background:#f8fafc; border:1px solid var(--line); border-radius:10px; }
.service-status .status-dot { width:9px; height:9px; border-radius:50%; background:#94a3b8; box-shadow:0 0 0 4px rgba(148,163,184,.16); }
.service-status.configured .status-dot { background:var(--primary); box-shadow:0 0 0 4px rgba(25,118,210,.13); }
.service-status.verified .status-dot { background:#15803d; box-shadow:0 0 0 4px rgba(21,128,61,.14); }
.service-status.error .status-dot,.service-status.unavailable .status-dot { background:#dc2626; box-shadow:0 0 0 4px rgba(220,38,38,.12); }
.service-status div { display:flex; flex-direction:column; gap:2px; }.service-status strong{font-size:14px}.service-status span:last-child{color:var(--muted);font-size:12px}
.workspace { position:relative; width:100%; min-height:0; flex:1 1 auto; margin:0; display:grid; grid-template-columns:280px minmax(0,1fr); background:#fff; border:1px solid var(--line); border-radius:16px; overflow:hidden; box-shadow:0 4px 16px rgba(15,23,42,.05); }
.assistant-panel { padding:20px 16px; display:flex; flex-direction:column; background:linear-gradient(180deg,#f8faff,#f5f7fb); border-right:1px solid var(--line); overflow-y:auto; }
.assistant-brand { display:flex; align-items:center; gap:11px; padding:2px 6px 18px; border-bottom:1px solid var(--line); }
.brand-icon,.welcome-icon { display:grid; place-items:center; color:#fff; background:linear-gradient(135deg,#3b82f6,#1d4ed8); box-shadow:0 8px 20px rgba(37,99,235,.24); }
.brand-icon{width:44px;height:44px;flex:0 0 auto;border-radius:12px;font-size:21px}.brand-copy{min-width:0;display:flex;flex:1;flex-direction:column}.brand-eyebrow{margin-bottom:2px;color:var(--primary);font-size:11px;font-weight:700;letter-spacing:.03em}.brand-copy h1{margin:0;color:var(--ink);font-size:18px;line-height:1.4}.brand-copy p{margin:2px 0 0;color:var(--muted);font-size:12px;line-height:1.5}.sidebar-close,.mobile-sidebar-toggle{display:none;border:0;background:transparent;color:#475569;cursor:pointer}
.panel-section{margin-top:20px}.panel-section h2,.panel-heading{margin:0 6px 10px;color:#465368;font-size:14px;font-weight:600}.panel-heading{width:calc(100% - 12px);padding:0;display:flex;align-items:center;justify-content:space-between;border:0;background:transparent;cursor:pointer}.panel-heading .el-icon{transition:transform 180ms ease}.panel-heading .el-icon.expanded{transform:rotate(180deg)}.capability-list{margin:0;padding:0 6px;list-style:none}.capability-list li{padding:7px 0;display:flex;align-items:center;gap:8px;color:#475569;font-size:14px;line-height:1.5}.capability-list .el-icon{flex:0 0 auto;color:#15803d}
.quick-action { width:100%; min-height:44px; margin-bottom:8px; padding:10px 12px; display:flex; justify-content:space-between; align-items:center; gap:8px; color:#334155; background:#fff; border:1px solid var(--line); border-radius:10px; font:inherit; font-size:14px; text-align:left; cursor:pointer; transition:border-color 180ms,color 180ms,background 180ms; }
.quick-action:hover:not(:disabled),.quick-action:focus-visible{color:var(--primary);border-color:#93b4fa;background:#f7faff;outline:none}.quick-action:disabled{opacity:.55;cursor:not-allowed}
.scope-note{margin-top:auto;padding:11px;display:flex;gap:8px;color:#475569;background:#eff6ff;border:1px solid #dbeafe;border-radius:10px;font-size:12px;line-height:1.55}.scope-note .el-icon{flex:0 0 auto;margin-top:2px;color:var(--primary)}.scope-note div{display:flex;flex-direction:column;gap:3px}.scope-note strong{color:#1e3a5f;font-size:12px}.scope-note span{display:block}
.chat-card{position:relative;min-width:0;min-height:0;height:100%;display:flex;flex-direction:column;overflow:hidden}.chat-toolbar{min-height:68px;flex:0 0 auto;padding:8px 22px;display:flex;align-items:center;justify-content:space-between;gap:16px;border-bottom:1px solid var(--line)}.conversation-title{display:flex;align-items:center;gap:10px}.conversation-title>.el-icon{width:36px;height:36px;color:var(--primary);background:#eff6ff;border-radius:10px}.conversation-title div{display:flex;flex-direction:column;gap:2px}.conversation-title strong{font-size:16px}.conversation-title span{color:var(--muted);font-size:12px}.toolbar-actions{display:flex;align-items:center;gap:10px}
.messages{flex:1 1 0;min-height:0;padding:28px clamp(18px,4vw,54px);overflow-x:hidden;overflow-y:auto;overscroll-behavior:contain;scrollbar-gutter:stable;background:linear-gradient(180deg,#fbfcff,#fff 35%)}.welcome{max-width:720px;margin:6vh auto 0;text-align:center}.welcome-icon{width:62px;height:62px;margin:0 auto 18px;border-radius:18px;font-size:27px}.welcome h2{margin:0 0 8px;font-size:24px}.welcome>p{margin:0 auto 26px;color:var(--muted);font-size:16px;line-height:1.7}
.prompt-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;text-align:left}.prompt-grid button{min-height:58px;padding:12px 14px;display:flex;align-items:center;gap:10px;color:#334155;background:#fff;border:1px solid var(--line);border-radius:12px;font:inherit;font-size:14px;line-height:1.5;cursor:pointer;transition:border-color 180ms,background 180ms}.prompt-grid button:hover:not(:disabled),.prompt-grid button:focus-visible{border-color:#93b4fa;background:#f7faff;outline:none}.prompt-grid .el-icon{flex:0 0 auto;color:var(--primary);font-size:18px}
.message-row{width:100%;max-width:960px;margin:0 auto 24px;display:flex;align-items:flex-start;gap:12px}.message-row.user{flex-direction:row-reverse}.message-avatar{width:36px;height:36px;flex:0 0 auto;display:grid;place-items:center;color:#fff;background:linear-gradient(135deg,#3b82f6,#1d4ed8);border-radius:10px;font-size:14px;font-weight:700}.message-row.user .message-avatar{background:#334155}.message-body{max-width:min(88%,780px)}.message-row.user .message-body{max-width:min(78%,720px);display:flex;flex-direction:column;align-items:flex-end}.message-bubble{padding:14px 16px;color:#1f2937;background:#fff;border:1px solid var(--line);border-radius:5px 14px 14px 14px;box-shadow:0 4px 16px rgba(15,23,42,.035);font-size:16px;line-height:1.75;white-space:pre-wrap;overflow-wrap:anywhere}.message-row.user .message-bubble{color:#fff;background:var(--primary);border-color:var(--primary);border-radius:14px 5px 14px 14px;box-shadow:none}.message-meta{margin-top:6px;padding:0 4px;display:flex;align-items:center;gap:12px;color:#64748b;font-size:12px}.copy-button{padding:4px 0;display:inline-flex;align-items:center;gap:4px;color:#64748b;background:none;border:0;font:inherit;cursor:pointer}.copy-button:hover{color:var(--primary)}
.markdown-body{white-space:normal}.markdown-body :deep(h1),.markdown-body :deep(h2),.markdown-body :deep(h3){margin:18px 0 8px;color:#172033;font-weight:600;line-height:1.5}.markdown-body :deep(h1:first-child),.markdown-body :deep(h2:first-child),.markdown-body :deep(h3:first-child){margin-top:0}.markdown-body :deep(h1){font-size:20px}.markdown-body :deep(h2){font-size:18px}.markdown-body :deep(h3){font-size:17px}.markdown-body :deep(p){margin:0 0 12px}.markdown-body :deep(p:last-child){margin-bottom:0}.markdown-body :deep(ul),.markdown-body :deep(ol){margin:8px 0 14px;padding-left:1.5em}.markdown-body :deep(li){margin:5px 0}.markdown-body :deep(blockquote){margin:12px 0;padding:8px 14px;color:#475569;background:#f8fafc;border-left:3px solid #93c5fd}.markdown-body :deep(code){padding:2px 6px;color:#9f1239;background:#fdf2f8;border-radius:5px;font-family:Consolas,"SFMono-Regular",monospace;font-size:.9em}.markdown-body :deep(pre){max-width:100%;margin:12px 0;padding:14px;overflow:auto;color:#e2e8f0;background:#0f172a;border-radius:10px;white-space:pre}.markdown-body :deep(pre code){padding:0;color:inherit;background:transparent}.markdown-body :deep(table){display:block;max-width:100%;margin:14px 0;overflow-x:auto;border-collapse:collapse}.markdown-body :deep(th),.markdown-body :deep(td){min-width:120px;padding:8px 10px;border:1px solid var(--line);text-align:left}.markdown-body :deep(th){background:#f8fafc;font-weight:600}.markdown-body :deep(a){color:var(--primary);text-decoration:underline;text-underline-offset:3px}
.typing{min-width:160px;display:flex;align-items:center;gap:5px}.typing span{width:6px;height:6px;border-radius:50%;background:#8090a6;animation:typing 1.2s infinite ease-in-out}.typing span:nth-child(2){animation-delay:.15s}.typing span:nth-child(3){animation-delay:.3s}.typing em{margin-left:5px;color:var(--muted);font-size:13px;font-style:normal}@keyframes typing{0%,60%,100%{transform:translateY(0);opacity:.45}30%{transform:translateY(-4px);opacity:1}}
.error-card{width:100%;max-width:960px;margin:0 auto 20px;padding:13px 15px;display:flex;align-items:center;gap:11px;color:#991b1b;background:#fff7f7;border:1px solid #fecaca;border-radius:12px}.error-card>.el-icon{flex:0 0 auto;font-size:19px}.error-card div{min-width:0;flex:1;display:flex;flex-direction:column;gap:3px}.error-card strong{font-size:14px}.error-card span{font-size:13px;line-height:1.5}
.scroll-latest{position:absolute;z-index:5;left:50%;bottom:142px;transform:translateX(-50%);padding:8px 12px;display:flex;align-items:center;gap:6px;color:#334155;background:#fff;border:1px solid var(--line);border-radius:999px;box-shadow:0 6px 20px rgba(15,23,42,.12);font:inherit;font-size:13px;cursor:pointer}.scroll-latest:hover{color:var(--primary);border-color:#93c5fd}
.composer{flex:0 0 auto;padding:14px 22px 18px;border-top:1px solid var(--line);background:#fff}.composer-inner{width:100%;max-width:960px;margin:0 auto}.composer-inner>label{display:block;margin:0 0 7px 2px;color:#475569;font-size:13px;font-weight:600}.composer-box{border:1px solid #cbd5e1;border-radius:14px;overflow:hidden;transition:border-color 180ms,box-shadow 180ms}.composer-box.focused{border-color:var(--primary);box-shadow:0 0 0 3px rgba(25,118,210,.11)}.composer-box :deep(.el-textarea__inner){min-height:64px!important;padding:13px 15px 5px;border:0;border-radius:0;box-shadow:none;color:var(--ink);font-size:16px;line-height:1.65}.composer-actions{padding:7px 8px 8px 14px;display:flex;align-items:center;justify-content:space-between;gap:12px}.composer-actions>span{color:#64748b;font-size:12px}.composer-actions .el-button{min-width:92px;min-height:40px;border-radius:9px;font-size:15px;font-weight:500}
.messages::-webkit-scrollbar,.assistant-panel::-webkit-scrollbar{width:6px}.messages::-webkit-scrollbar-thumb,.assistant-panel::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:6px}
@media(max-width:980px){.ai-page{padding:14px}.workspace{min-height:0;grid-template-columns:1fr}.assistant-panel{position:absolute;z-index:20;inset:0 auto 0 0;width:min(300px,86vw);display:flex;transform:translateX(-102%);transition:transform 200ms ease;box-shadow:12px 0 28px rgba(15,23,42,.14)}.assistant-panel.open{transform:translateX(0)}.sidebar-close,.mobile-sidebar-toggle{width:36px;height:36px;display:grid;place-items:center;border-radius:9px}.sidebar-close:hover,.mobile-sidebar-toggle:hover{background:#eff6ff;color:var(--primary)}.sidebar-backdrop{position:absolute;z-index:15;inset:0;display:block;border:0;background:rgba(15,23,42,.32);cursor:pointer}.chat-card{min-height:0}}
@media(max-width:640px){.workspace{border-radius:13px}.chat-toolbar{padding:8px 12px}.conversation-title>.el-icon{display:none}.service-status{min-width:0;padding:8px}.service-status div{display:flex}.service-status strong{font-size:12px;white-space:nowrap}.service-status span:last-child{display:none}.toolbar-actions{gap:2px}.toolbar-actions .el-button{padding:8px}.messages{padding:20px 12px}.prompt-grid{grid-template-columns:1fr}.message-body,.message-row.user .message-body{max-width:86%}.message-bubble{padding:12px 14px;font-size:15px}.composer{padding:12px}.composer-actions>span{display:none}.composer-actions{justify-content:flex-end}.scroll-latest{bottom:128px}}
@media(prefers-reduced-motion:reduce){.typing span{animation:none}*{scroll-behavior:auto!important}}
</style>
