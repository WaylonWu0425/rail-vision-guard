<template>
  <div class="ai-chat">
    <div class="page-title">AI智能助手</div>

    <div class="chat-container">
      <!-- 左侧：功能面板 -->
      <div class="chat-sidebar">
        <div class="sidebar-card">
          <div class="card-header">
            <el-icon><MagicStick /></el-icon>
            <span>能力说明</span>
          </div>
          <div class="capability-list">
            <div class="capability-item" v-for="(item, index) in capabilities" :key="index">
              <el-icon><Check /></el-icon>
              <span>{{ item }}</span>
            </div>
          </div>
        </div>

        <div class="sidebar-card">
          <div class="card-header">
            <el-icon><ChatDotRound /></el-icon>
            <span>快捷提问</span>
          </div>
          <div class="quick-actions-list">
            <div
                v-for="(action, index) in quickActions"
                :key="index"
                class="quick-action-item"
                @click="handleQuickAction(action.prompt)"
            >
              <el-icon><Promotion /></el-icon>
              <span>{{ action.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：对话区域 -->
      <div class="chat-main">
        <div class="chat-header">
          <div class="status-info">
            <div class="status-dot"></div>
            <span>AI助手在线</span>
          </div>
        </div>

        <!-- 消息区域 - 这里独立滚动 -->
        <div class="messages-wrapper" ref="messagesContainer">
          <!-- 欢迎消息 -->
          <div v-if="messages.length === 0" class="welcome-content">
            <div class="welcome-icon">
              <el-icon :size="48"><MagicStick /></el-icon>
            </div>
            <div class="welcome-title">您好！我是AI助手</div>
            <div class="welcome-desc">我可以帮您解答关于监控系统的各种问题</div>
            <div class="example-questions">
              <div class="example-label">试试这样问：</div>
              <div class="example-list">
                <el-tag
                    v-for="(example, index) in exampleQuestions"
                    :key="index"
                    class="example-tag"
                    @click="handleQuickAction(example)"
                >
                  {{ example }}
                </el-tag>
              </div>
            </div>
          </div>

          <!-- 消息列表 -->
          <div v-else>
            <div
                v-for="(message, index) in messages"
                :key="index"
                :class="['message-item', message.type]"
            >
              <div class="message-avatar">
                <div class="avatar" :class="message.type">
                  <el-icon v-if="message.type === 'bot'"><MagicStick /></el-icon>
                  <span v-else>我</span>
                </div>
              </div>
              <div class="message-content">
                <div class="message-text" v-html="formatMessage(message.content)"></div>
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>
          </div>

          <!-- 加载中 -->
          <div v-if="loading" class="message-item bot">
            <div class="message-avatar">
              <div class="avatar bot">
                <el-icon><MagicStick /></el-icon>
              </div>
            </div>
            <div class="message-content">
              <div class="message-text loading-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="2"
              placeholder="输入您的问题，例如：什么是视频监控系统？"
              :disabled="loading"
              @keydown.enter.exact.prevent="sendMessage"
              class="chat-input"
          />
          <div class="input-actions">
            <el-button
                type="primary"
                @click="sendMessage"
                :loading="loading"
                :disabled="!inputMessage.trim()"
                round
            >
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import {
  ChatDotRound,
  Promotion,
  MagicStick,
  Check
} from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 状态
const inputMessage = ref('')
const messages = ref([])
const loading = ref(false)
const messagesContainer = ref(null)

// AI助手能力说明（科普百科类）
const capabilities = ref([
  '监控系统基础知识解答',
  '摄像头技术原理介绍',
  '视频监控行业标准',
  '智能分析算法说明',
  '监控设备选型建议',
  '监控系统运维知识'
])

// 快捷操作（科普问答类）
const quickActions = ref([
  { label: '什么是视频监控系统', prompt: '请介绍一下视频监控系统的基本组成和工作原理' },
  { label: '摄像头类型有哪些', prompt: '监控摄像头有哪些类型？各有什么特点？' },
  { label: '什么是AI智能分析', prompt: 'AI智能分析在视频监控中有哪些应用？' },
  { label: '如何选择监控摄像头', prompt: '如何根据场景选择合适的监控摄像头？' },
  { label: '视频存储技术', prompt: '监控视频的存储方式有哪些？各有何优缺点？' },
  { label: '监控系统维护', prompt: '视频监控系统日常维护需要注意什么？' }
])

// 示例问题（科普问答类）
const exampleQuestions = ref([
  '视频监控系统有哪些组成部分',
  '什么是高清监控',
  '智能分析有哪些功能',
  '如何选择摄像头分辨率',
  '监控录像保存多久',
  '什么是边缘计算'
])

// 发送消息
const sendMessage = async () => {
  const text = inputMessage.value.trim()
  if (!text) return
  if (loading.value) return

  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: text,
    timestamp: Date.now()
  })
  inputMessage.value = ''
  loading.value = true
  await nextTick(scrollToBottom)

  try {
    // 调用后端API
    const response = await axios.get('/spring/api/chat/ai', {
      params: { question: text }
    })

    if (response.data && response.data.data) {
      messages.value.push({
        type: 'bot',
        content: response.data.data,
        timestamp: Date.now()
      })
    } else {
      throw new Error('响应数据为空')
    }
  } catch (error) {
    console.error('AI助手错误:', error)
    ElMessage.error('AI助手服务暂时不可用，请稍后再试')
    messages.value.push({
      type: 'bot',
      content: '抱歉，服务暂时不可用。请稍后再试，或联系管理员处理。',
      timestamp: Date.now()
    })
  } finally {
    loading.value = false
    await nextTick(scrollToBottom)
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    const container = messagesContainer.value
    container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' })
  }
}

// 格式化消息内容
const formatMessage = (content) => {
  if (!content) return ''
  let formatted = content
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/^[•-]\s+(.*)/gm, '<span class="list-item">• $1</span>')
  return formatted
}

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

// 处理快捷操作
const handleQuickAction = (prompt) => {
  inputMessage.value = prompt
  sendMessage()
}
</script>

<style scoped>
.ai-chat {
  width: 98%;
  height: auto;
  min-height: 97%;
  margin: 1%;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  overflow: visible;
}

.page-title {
  font-size: 1.2rem;
  font-weight: 600;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  color: #303133;
  background-color: #fff;
  flex-shrink: 0;
}

.chat-container {
  display: flex;
  padding: 20px;
  gap: 20px;
  background-color: #f5f7fa;
  flex: 1;
}

/* 左侧边栏 */
.chat-sidebar {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex-shrink: 0;
}

.sidebar-card {
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  overflow: hidden;
}

.card-header {
  padding: 14px 16px;
  border-bottom: 1px solid #ebeef5;
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #fafafa;
}

.card-header .el-icon {
  font-size: 18px;
  color: #3d7d6f;
}

.capability-list {
  padding: 12px;
}

.capability-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 13px;
  color: #606266;
  border-bottom: 1px solid #f0f0f0;
}

.capability-item:last-child {
  border-bottom: none;
}

.capability-item .el-icon {
  font-size: 14px;
  color: #67c23a;
}

.quick-actions-list {
  padding: 12px;
}

.quick-action-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  margin-bottom: 8px;
  background-color: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 13px;
  color: #409eff;
}

.quick-action-item:hover {
  background-color: #ecf5ff;
  transform: translateX(4px);
}

.quick-action-item .el-icon {
  font-size: 14px;
}

/* 右侧主面板 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  overflow: hidden;
  min-width: 0;
  height: 600px;
}

.chat-header {
  padding: 12px 20px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fafafa;
  flex-shrink: 0;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #67c23a;
}

.status-dot {
  width: 8px;
  height: 8px;
  background-color: #67c23a;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 消息区域 - 这里独立滚动 */
.messages-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #fafbfc;
}

/* 欢迎内容 */
.welcome-content {
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #3d7d6f 0%, #2a5a4d 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.welcome-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.welcome-desc {
  font-size: 14px;
  color: #909399;
  margin-bottom: 30px;
}

.example-questions {
  margin-top: 20px;
}

.example-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
}

.example-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}

.example-tag {
  cursor: pointer;
  transition: all 0.3s;
  background-color: #f5f7fa;
  border: 1px solid #dcdfe6;
  color: #606266;
}

.example-tag:hover {
  background-color: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
  transform: translateY(-2px);
}

/* 消息项 */
.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-item.user .message-content {
  align-items: flex-end;
}

.message-item.user .message-text {
  background-color: #3d7d6f;
  color: #fff;
  border-radius: 12px 12px 4px 12px;
}

.message-item.bot .message-text {
  background-color: #f0f0f0;
  color: #303133;
  border-radius: 12px 12px 12px 4px;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
}

.avatar.bot {
  background: linear-gradient(135deg, #3d7d6f 0%, #2a5a4d 100%);
  color: #fff;
}

.avatar.user {
  background-color: #409eff;
  color: #fff;
}

.message-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 70%;
}

.message-text {
  padding: 10px 14px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}

.message-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 4px;
  padding: 0 4px;
}

.message-item.user .message-time {
  text-align: right;
}

/* 加载动画 */
.loading-dots {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 10px 14px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  background-color: #909399;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 输入区域 */
.input-area {
  border-top: 1px solid #ebeef5;
  padding: 16px 20px;
  background-color: #fff;
  flex-shrink: 0;
}

.chat-input {
  margin-bottom: 12px;
}

.chat-input :deep(.el-textarea__inner) {
  border-radius: 8px;
  font-size: 14px;
  resize: none;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}

/* 消息内容样式 */
:deep(.list-item) {
  display: block;
  padding-left: 16px;
  margin: 6px 0;
  color: inherit;
}

:deep(strong) {
  font-weight: 600;
  color: #3d7d6f;
}

/* 滚动条样式 */
.messages-wrapper::-webkit-scrollbar {
  width: 6px;
}

.messages-wrapper::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 3px;
}

.messages-wrapper::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.messages-wrapper::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 响应式适配 */
@media screen and (max-width: 1200px) {
  .chat-sidebar {
    width: 260px;
  }

  .message-content {
    max-width: 80%;
  }
}

@media screen and (max-width: 768px) {
  .chat-container {
    flex-direction: column;
  }

  .chat-sidebar {
    width: 100%;
    flex-direction: row;
  }

  .sidebar-card {
    flex: 1;
  }

  .message-content {
    max-width: 85%;
  }

  .chat-main {
    height: 500px;
  }
}
</style>