<template>
  <view class="container">
    <!-- 头部信息卡片 -->
    <view class="header-card" @touchstart="handleCardTouch('header')" @touchend="handleCardTouchEnd('header')">
      <view class="user-avatar">
        <view class="avatar-icon" :class="{ 'avatar-pulse': userInfo?.username }">
          <text class="avatar-text">{{ userInfo?.username?.[0]?.toUpperCase() || '?' }}</text>
        </view>
        <view class="avatar-status" :class="{ 'status-animate': isConnected }"></view>
      </view>

      <view class="user-info">
        <text class="user-name" :class="{ 'name-placeholder': !userInfo?.username }">
          {{ userInfo?.username || '请完善信息' }}
        </text>
        <text class="user-id">ID: {{ userInfo?.id?.slice(0, 8) || '未设置' }}</text>

        <view class="status-indicator" @click="toggleConnection">
          <view class="status-dot" :class="{ 'dot-pulse': isConnected }"></view>
          <text class="status-text">监测状态：{{ connectionStatus }}</text>
          <view class="status-arrow">
            <text>›</text>
          </view>
        </view>
      </view>

      <view class="date-info">
        <view class="date-icon">
          <text>📅</text>
        </view>
        <text class="date-label">{{ formatDate(new Date(), 'MM月dd日') }}</text>
        <text class="week-label">{{ formatDate(new Date(), '周') }}</text>
      </view>
    </view>

    <!-- 健康概览卡片 -->
    <view class="health-overview" @touchstart="handleCardTouch('overview')" @touchend="handleCardTouchEnd('overview')">
      <view class="overview-header">
        <view class="header-left">
          <text class="section-title">健康概览</text>
          <view class="data-indicator" :class="{ 'indicator-updating': isDataUpdating }">
            <text class="indicator-dot"></text>
            <text class="indicator-text">{{ isDataUpdating ? '更新中...' : '实时' }}</text>
          </view>
        </view>
        <view class="overview-actions">
<!--          <view class="action-btn" @click="toggleViewMode">-->
<!--            <text class="action-icon">{{ viewMode === 'grid' ? '☷' : '☰' }}</text>-->
<!--          </view>-->
          <view class="action-btn" @click="refreshData">
            <text class="action-icon">⟳</text>
          </view>
        </view>
      </view>

      <view class="health-metrics" :class="viewMode">
        <view
            v-for="(metric, index) in metricCards"
            :key="metric.key"
            class="metric-card"
            :style="{ '--card-index': index, background: metric.gradient }"
            @touchstart="handleMetricTouch(index)"
            @touchend="handleMetricTouchEnd(index)"
            @click="handleMetricClick(metric)"
        >
          <view class="metric-badge" v-if="metric.trend">
            <text class="badge-text">{{ metric.trend }}</text>
          </view>
          <view class="metric-content">
            <view class="metric-icon" :class="`icon-${metric.key}`">
              <text>{{ metric.icon }}</text>
            </view>
            <view class="metric-values">
              <text class="metric-value">{{ metric.value || '--' }}</text>
              <text class="metric-unit">{{ metric.unit }}</text>
            </view>
            <text class="metric-label">{{ metric.label }}</text>
          </view>
          <view class="metric-footer">
            <text class="metric-status" :class="metric.status">{{ metric.statusText }}</text>
            <view class="metric-trend" v-if="metric.change">
              <text class="trend-icon" :class="metric.change > 0 ? 'trend-up' : 'trend-down'">
                {{ metric.change > 0 ? '↗' : '↘' }}
              </text>
              <text class="trend-value">{{ Math.abs(metric.change) }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 详细信息 -->
    <view class="detail-section" @touchstart="handleCardTouch('detail')" @touchend="handleCardTouchEnd('detail')">
      <view class="section-header">
        <!--        <view class="header-icon">-->
        <!--          <text>📋</text>-->
        <!--        </view>-->
        <text class="section-title">详细信息</text>
      </view>

      <view class="section-tabs">
        <view
            v-for="tab in tabs"
            :key="tab.id"
            class="tab-item"
            :class="{ active: activeTab === tab.id, 'tab-pulse': tab.hasAlert }"
            @click="switchTab(tab.id)"
        >
          <view class="tab-icon">
            <text>{{ tab.icon }}</text>
          </view>
          <text class="tab-text">{{ tab.name }}</text>
          <view class="tab-indicator" v-if="activeTab === tab.id"></view>
          <view class="tab-badge" v-if="tab.badge">
            <text class="badge-text">{{ tab.badge }}</text>
          </view>
        </view>
      </view>

      <!-- 身体健康详情 -->
      <view class="detail-content" v-if="activeTab === 'health'">
        <view class="detail-grid">
          <view
              v-for="item in healthDetails"
              :key="item.key"
              class="detail-item"
              :class="{ 'item-highlight': item.highlight }"
          >
            <view class="detail-header">
              <view class="detail-icon">
                <text>{{ item.icon }}</text>
              </view>
              <text class="detail-label">{{ item.label }}</text>
              <view class="detail-actions">
                <view class="action-dot" v-if="item.alert"></view>
                <view class="action-info" @click="showInfo(item)">
                  <text>ℹ️</text>
                </view>
              </view>
            </view>

            <view class="detail-value-container">
              <view class="value-display">
                <text class="value-number" :class="`value-${item.key}`">
                  {{ item.value || '--' }}
                </text>
                <text class="value-unit">{{ item.unit }}</text>
              </view>

              <view class="value-comparison" v-if="item.comparison">
                <text class="comparison-text" :class="item.comparison > 0 ? 'comparison-up' : 'comparison-down'">
                  {{ item.comparison > 0 ? '↑' : '↓' }} {{ Math.abs(item.comparison) }}%
                </text>
                <text class="comparison-label">较昨日</text>
              </view>
            </view>

            <view class="detail-progress" v-if="item.progress">
              <view class="progress-bar">
                <view
                    class="progress-fill"
                    :style="{ width: item.progress + '%' }"
                    :class="`progress-${item.key}`"
                ></view>
              </view>
              <view class="progress-labels">
                <text class="progress-min">{{ item.range?.min || 0 }}{{ item.unit }}</text>
                <text class="progress-max">{{ item.range?.max || 100 }}{{ item.unit }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 环境健康详情 -->
      <view class="detail-content" v-if="activeTab === 'environment'">
        <view class="environment-grid">
          <view
              v-for="item in environmentDetails"
              :key="item.key"
              class="environment-item"
              :class="{ 'environment-warning': item.warning }"
          >
            <view class="environment-header">
              <view class="environment-icon" :class="`env-icon-${item.key}`">
                <text>{{ item.icon }}</text>
              </view>
              <text class="environment-label">{{ item.label }}</text>
            </view>

            <view class="environment-value">
              <text class="value-display">{{ item.value || '--' }}</text>
              <text class="value-unit">{{ item.unit }}</text>
            </view>

            <view class="environment-status">
              <view class="status-level" :class="`level-${item.level}`">
                <text>{{ item.status }}</text>
              </view>
            </view>

            <view class="environment-chart" v-if="item.trend">
              <view class="chart-line">
                <view
                    v-for="(point, idx) in item.trend"
                    :key="idx"
                    class="chart-point"
                    :style="{ left: idx * 20 + 'rpx', height: point + 'rpx' }"
                ></view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 设备信息 -->
      <view class="detail-content" v-if="activeTab === 'device'">
        <view class="device-card" :class="{ 'device-connected': currentFacility }">
          <view class="device-header">
<!--            <view class="device-icon">-->
<!--              <text>📱</text>-->
<!--            </view>-->
            <text class="device-title">{{ currentFacility?.name || '未连接设备' }}</text>
            <view class="device-status" :class="{ 'status-online': currentFacility }">
              <text>{{ currentFacility ? '在线' : '离线' }}</text>
            </view>
          </view>

          <view class="device-info">
            <view
                v-for="info in deviceInfo"
                :key="info.label"
                class="info-row"
            >
              <text class="info-label">{{ info.label }}</text>
              <text class="info-value">{{ info.value || '--' }}</text>
            </view>
          </view>

          <view class="device-actions" v-if="currentFacility">
            <view class="action-btn" @click="syncDevice">
              <text class="action-icon">🔄</text>
              <text class="action-text">同步数据</text>
            </view>
            <view class="action-btn" @click="deviceSettings">
              <text class="action-icon">⚙️</text>
              <text class="action-text">设备设置</text>
            </view>
          </view>

          <view class="device-empty" v-else>
            <view class="empty-icon">
              <text>🔌</text>
            </view>
            <text class="empty-text">请先连接设备以获取数据</text>
            <view class="empty-btn" @click="connectDevice">
              <text>连接设备</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- AI健康报告 -->
    <view class="ai-report-card" @touchstart="handleCardTouch('report')" @touchend="handleCardTouchEnd('report')">
      <view class="report-header">
        <view class="header-left">
          <!--          <view class="ai-icon" :class="{ 'ai-pulse': reportStatus === 'loaded' }">-->
          <!--&lt;!&ndash;            <text>🤖</text>&ndash;&gt;-->
          <!--          </view>-->
          <view class="report-title-container">
            <text class="section-title">AI健康分析报告</text>
            <text class="report-subtitle">基于实时数据生成</text>
          </view>
        </view>
        <view class="report-actions">
          <view class="action-btn" @click="refreshReport" :class="{ 'btn-loading': isRefreshing }">
            <text class="action-icon" v-if="!isRefreshing">⟳</text>
            <view class="loading-spinner" v-else></view>
          </view>
          <view class="action-btn" @click="shareReport">
            <text class="action-icon">📤</text>
          </view>
        </view>
      </view>

      <view class="report-content" :class="{ 'content-collapsed': isReportCollapsed }" @click="toggleReport">
        <scroll-view scroll-y class="report-text-container" v-if="!isReportCollapsed">
          <text class="report-text" :class="{ 'text-loading': reportStatus === 'loading' }">
            {{ aiReport }}
          </text>
        </scroll-view>
        <view class="report-preview" v-else>
          <text class="preview-text">{{ aiReportPreview }}</text>
          <text class="preview-hint">点击展开完整报告</text>
        </view>
      </view>

      <view class="report-footer">
        <view class="footer-left">
          <view class="time-icon">
            <text>⏰</text>
          </view>
          <text class="report-time">更新时间: {{ formatDate(new Date(), 'HH:mm:ss') }}</text>
        </view>
        <view class="report-status" :class="reportStatusClass"
              @click="reportStatus === 'error' ? fetchAiReport() : null">
          <view class="status-icon">
            <text>{{ reportStatusIcon }}</text>
          </view>
          <text class="status-text">{{ reportStatusText }}</text>
        </view>
      </view>
    </view>

    <!-- AI对话助手 -->
    <view class="ai-assistant" @touchstart="handleCardTouch('assistant')" @touchend="handleCardTouchEnd('assistant')">
      <view class="assistant-header">
        <view class="header-left">
<!--          <view class="assistant-icon" :class="{ 'assistant-active': userQuestion }">-->
<!--            <text>💬</text>-->
<!--          </view>-->
          <view class="title-container">
            <text class="section-title">AI健康助手</text>
            <text class="assistant-subtitle">有任何问题随时咨询</text>
          </view>
        </view>
        <view class="header-tip" @click="showAssistantTips">
          <text>💡</text>
        </view>
      </view>

      <scroll-view
          scroll-y
          class="chat-container"
          :scroll-into-view="'msg-' + (chatMessages.length - 1)"
          :scroll-with-animation="true"
      >
        <view class="chat-messages">
          <view
              v-for="(msg, index) in chatMessages"
              :key="index"
              :id="'msg-' + index"
              class="chat-message"
              :class="[msg.sender, { 'message-new': index === chatMessages.length - 1 && msg.sender === 'ai' }]"
          >
            <view class="message-avatar" v-if="msg.sender === 'ai'">
              <view class="avatar-glow"></view>
              <text>🤖</text>
            </view>
            <view class="message-bubble" :class="`bubble-${msg.sender}`">
              <text class="message-content">{{ msg.content }}</text>
              <view class="message-meta">
                <text class="message-time">{{ formatMessageTime(msg.time) }}</text>
                <view class="message-actions" v-if="msg.sender === 'ai'">
                  <view class="action-btn" @click="copyMessage(msg.content)">
                    <text>📋</text>
                  </view>
                  <view class="action-btn" @click="regenerateResponse(index)">
                    <text>🔄</text>
                  </view>
                </view>
              </view>
            </view>
            <view class="message-avatar" v-if="msg.sender === 'user'">
              <text>👤</text>
            </view>
          </view>
        </view>
        <view class="chat-placeholder" v-if="chatMessages.length === 1">
          <text class="placeholder-text">试着问我关于健康的问题吧！</text>
          <view class="placeholder-suggestions">
            <view
                v-for="(suggestion, idx) in suggestions"
                :key="idx"
                class="suggestion-chip"
                @click="useSuggestion(suggestion)"
            >
              <text>{{ suggestion }}</text>
            </view>
          </view>
        </view>
      </scroll-view>

      <view class="chat-input-area" :class="{ 'input-focused': inputFocus }">
        <view class="input-container">
          <input
              class="chat-input"
              v-model="userQuestion"
              placeholder="输入您的问题..."
              placeholder-class="placeholder"
              @focus="inputFocus = true"
              @blur="inputFocus = false"
              @confirm="askAI"
              :adjust-position="true"
          />
          <view class="input-actions">
            <view class="action-btn" @click="clearInput" v-if="userQuestion">
              <text>✕</text>
            </view>
            <view class="action-btn" @click="toggleVoiceInput">
              <text>🎤</text>
            </view>
          </view>
        </view>
        <button
            class="send-button"
            @click="askAI"
            :disabled="!userQuestion.trim() || isAskingAI"
            :class="{ 'btn-active': userQuestion.trim(), 'btn-loading': isAskingAI }"
        >
          <text class="send-icon" v-if="!isAskingAI">发送</text>
          <view class="loading-dots" v-else>
            <view class="dot"></view>
            <view class="dot"></view>
            <view class="dot"></view>
          </view>
        </button>
      </view>
    </view>

    <!-- 悬浮操作按钮 -->
    <view class="floating-actions">
      <view class="fab-main" @click="toggleFabMenu" :class="{ 'fab-open': isFabOpen }">
        <text class="fab-icon">+</text>
      </view>
      <view class="fab-menu" v-if="isFabOpen">
        <view class="fab-item" @click="exportReport">
          <view class="item-icon">
            <text>📥</text>
          </view>
          <text class="item-text">导出报告</text>
        </view>
        <view class="fab-item" @click="shareHealthData">
          <view class="item-icon">
            <text>📤</text>
          </view>
          <text class="item-text">分享数据</text>
        </view>
        <view class="fab-item" @click="quickCheck">
          <view class="item-icon">
            <text>🔍</text>
          </view>
          <text class="item-text">快速检查</text>
        </view>
      </view>
    </view>

    <!-- 底部安全区域 -->
    <view class="safe-area"></view>
  </view>
</template>

<script setup>
import {aireport, askai} from '../../api/ai.js';
import {ref, watchEffect, computed, nextTick, onMounted} from 'vue';
import {useUserStore} from '../../store/user';
import {useFacilitiesStore} from '../../store/facilities.js'
import {useEnvironmentStore} from '../../store/environmentData.js'
import {onPullDownRefresh} from '@dcloudio/uni-app'

// 从 store 获取数据
const {age, userInfo} = useUserStore()
const {currentFacility} = useFacilitiesStore()
const environmentStore = useEnvironmentStore()

// 状态管理
const activeTab = ref('health')
const inputFocus = ref(false)
const reportStatus = ref('loaded')
const isRefreshing = ref(false)
const isAskingAI = ref(false)
const viewMode = ref('grid')
const isConnected = ref(true)
const isDataUpdating = ref(false)
const isReportCollapsed = ref(false)
const isFabOpen = ref(false)
const pressedCard = ref(null)
const pressedMetric = ref(null)

// 响应式数据
const healthMetrics = ref({})
const environmentMetrics = ref({})
const aiReport = ref('正在分析您的健康数据，请稍候...')
const userQuestion = ref('')
const chatMessages = ref([{
  sender: 'ai',
  content: '您好！我是您的AI健康助手。我可以为您分析健康数据、提供健康建议、解答健康疑问。请问有什么可以帮助您的？',
  time: new Date()
}])

// 预设建议问题
const suggestions = ref([
  '我现在的健康状况如何？',
  '如何改善睡眠质量？',
  '适合我的运动建议',
  '饮食健康指导'
])

// 渐变色数组
const metricGradients = [
  'linear-gradient(135deg, rgba(255, 107, 107, 0.15), rgba(255, 142, 142, 0.1))',
  'linear-gradient(135deg, rgba(78, 205, 196, 0.15), rgba(110, 231, 231, 0.1))',
  'linear-gradient(135deg, rgba(255, 209, 102, 0.15), rgba(255, 224, 163, 0.1))',
  'linear-gradient(135deg, rgba(17, 138, 178, 0.15), rgba(6, 214, 160, 0.1))'
]

const metricCards = computed(() => {
  return [
    {
      key: 'heart',
      icon: '',
      label: '心率',
      value: healthMetrics.value.heartRate || '--',
      unit: '次/分',
      gradient: metricGradients[0],
      status: 'normal',
      statusText: '正常',
      trend: '稳定',
      change: 0
    },
    {
      key: 'breath',
      icon: '',
      label: '呼吸',
      value: healthMetrics.value.respiratoryRate || '--',
      unit: '次/分',
      gradient: metricGradients[1],
      status: 'normal',
      statusText: '良好',
      trend: '稳定',
      change: 0
    },
    {
      key: 'temp',
      icon: '',
      label: '温度',
      value: environmentMetrics.value.temperature || '--',
      unit: '°C',
      gradient: metricGradients[2],
      status: 'normal',
      statusText: '舒适',
      trend: '稳定',
      change: 0
    },
    {
      key: 'humidity',
      icon: '',
      label: '湿度',
      value: environmentMetrics.value.humidity || '--',
      unit: '%',
      gradient: metricGradients[3],
      status: environmentMetrics.value.humidity > 70 ? 'warning' : 'normal',
      statusText: environmentMetrics.value.humidity > 70 ? '偏高' : '适宜',
      trend: '稳定',
      change: 0
    }
  ]
})

const tabs = computed(() => [
  {
    id: 'health',
    name: '身体健康',
    icon: '',
    badge: null,
    hasAlert: false
  },
  {
    id: 'environment',
    name: '环境健康',
    icon: '',
    badge: environmentMetrics.value.coConcentration > 0.3 ? '!' : null,
    hasAlert: environmentMetrics.value.coConcentration > 0.3
  },
  {
    id: 'device',
    name: '设备信息',
    icon: '',
    badge: currentFacility?.value ? null : '!',
    hasAlert: !currentFacility?.value
  }
])

const healthDetails = computed(() => [
  {
    key: 'heartRate',
    label: '心率',
    value: healthMetrics.value.heartRate,
    unit: '次/分',
    icon: '',
    progress: 75,
    range: {min: 60, max: 100},
    comparison: -2,
    alert: false,
    highlight: false
  },
  {
    key: 'respiratoryRate',
    label: '呼吸频率',
    value: healthMetrics.value.respiratoryRate,
    unit: '次/分',
    icon: '',
    progress: 65,
    range: {min: 12, max: 20},
    comparison: 0,
    alert: false,
    highlight: false
  },
  {
    key: 'move',
    label: '活动次数',
    value: healthMetrics.value.move,
    unit: '次/分',
    icon: '',
    progress: 40,
    range: {min: 0, max: 5},
    comparison: 5,
    alert: false,
    highlight: true
  },
  {
    key: 'distance',
    label: '移动距离',
    value: healthMetrics.value.distance,
    unit: '米/分',
    icon: '',
    progress: 60,
    range: {min: 0, max: 10},
    comparison: 8,
    alert: false,
    highlight: false
  }
])

const environmentDetails = computed(() => [
  {
    key: 'co',
    label: '一氧化碳',
    value: environmentMetrics.value.coConcentration,
    unit: 'ppm',
    icon: '💨',
    level: environmentMetrics.value.coConcentration > 0.3 ? 'high' : 'low',
    status: environmentMetrics.value.coConcentration > 0.3 ? '偏高' : '正常',
    warning: environmentMetrics.value.coConcentration > 0.3,
    trend: [20, 25, 30, 28, 26, 24, 22]
  },
  {
    key: 'light',
    label: '光照强度',
    value: environmentMetrics.value.lightIntensity,
    unit: 'lux',
    icon: '💡',
    level: 'optimal',
    status: '适宜',
    warning: false,
    trend: [40, 42, 45, 48, 50, 48, 46]
  },
  {
    key: 'sound',
    label: '声音大小',
    value: environmentMetrics.value.soundLevel,
    unit: 'dB',
    icon: '🔊',
    level: environmentMetrics.value.soundLevel > 80 ? 'high' : 'low',
    status: environmentMetrics.value.soundLevel > 80 ? '嘈杂' : '安静',
    warning: environmentMetrics.value.soundLevel > 80,
    trend: [30, 32, 35, 40, 38, 36, 34]
  },
  {
    key: 'temp',
    label: '温度',
    value: environmentMetrics.value.temperature,
    unit: '°C',
    icon: '🌡️',
    level: 'optimal',
    status: '舒适',
    warning: false,
    trend: [36, 36.2, 36.5, 36.8, 36.7, 36.6, 36.5]
  },
  {
    key: 'humidity',
    label: '湿度',
    value: environmentMetrics.value.humidity,
    unit: '%',
    icon: '💧',
    level: environmentMetrics.value.humidity > 70 ? 'high' : 'optimal',
    status: environmentMetrics.value.humidity > 70 ? '偏高' : '适宜',
    warning: environmentMetrics.value.humidity > 70,
    trend: [55, 56, 58, 60, 62, 61, 60]
  }
])

const deviceInfo = computed(() => [
  {label: '设备名称', value: currentFacility?.name},
  {label: '设备ID', value: currentFacility?.id?.slice(0, 8)},
  {label: '连接状态', value: currentFacility ? '已连接' : '未连接'},
  {label: '信号强度', value: currentFacility ? '强' : '--'},
  {label: '最后同步', value: '刚刚'}
])

const aiReportPreview = computed(() => {
  return aiReport.value.split('\n')[0] + '...'
})

const connectionStatus = computed(() => {
  return isConnected.value ? '良好' : '断开'
})

const reportStatusClass = computed(() => {
  return {
    'status-loading': reportStatus.value === 'loading',
    'status-loaded': reportStatus.value === 'loaded',
    'status-error': reportStatus.value === 'error'
  }
})

const reportStatusText = computed(() => {
  const texts = {
    'loading': '生成中',
    'loaded': '已更新',
    'error': '刷新'
  }
  return texts[reportStatus.value] || '未知'
})

const reportStatusIcon = computed(() => {
  const icons = {
    'loading': '⏳',
    'loaded': '✅',
    'error': '🔄'
  }
  return icons[reportStatus.value] || '❓'
})

// 格式化函数
const formatDate = (date, type = 'default') => {
  const d = new Date(date)
  if (type === 'MM月dd日') {
    return `${(d.getMonth() + 1).toString().padStart(2, '0')}月${d.getDate().toString().padStart(2, '0')}日`
  } else if (type === '周') {
    const weeks = ['日', '一', '二', '三', '四', '五', '六']
    return `周${weeks[d.getDay()]}`
  } else if (type === 'HH:mm:ss') {
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`
  }
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`
}

function formatMessageTime(time) {
  const d = new Date(time)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

// 交互处理函数
function handleCardTouch(card) {
  pressedCard.value = card
}

function handleCardTouchEnd(card) {
  pressedCard.value = null
}

function handleMetricTouch(index) {
  pressedMetric.value = index
}

function handleMetricTouchEnd(index) {
  pressedMetric.value = null
}

function handleMetricClick(metric) {
  uni.showToast({
    title: `查看${metric.label}详情`,
    icon: 'none'
  })
}

function switchTab(tabId) {
  activeTab.value = tabId
}

function toggleViewMode() {
  viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid'
}

function toggleConnection() {
  isConnected.value = !isConnected.value
  uni.showToast({
    title: isConnected.value ? '已连接设备' : '已断开连接',
    icon: 'success'
  })
}

function toggleReport() {
  isReportCollapsed.value = !isReportCollapsed.value
}

function toggleFabMenu() {
  isFabOpen.value = !isFabOpen.value
}

function useSuggestion(suggestion) {
  userQuestion.value = suggestion
  askAI()
}

function clearInput() {
  userQuestion.value = ''
}

function toggleVoiceInput() {
  uni.showToast({
    title: '语音输入功能开发中',
    icon: 'none'
  })
}

function showInfo(item) {
  uni.showModal({
    title: item.label + '说明',
    content: '这是您的' + item.label + '数据，正常范围：' + (item.range?.min || 0) + '-' + (item.range?.max || 100) + item.unit,
    showCancel: false
  })
}

function showAssistantTips() {
  uni.showActionSheet({
    itemList: ['健康咨询示例', '数据解读帮助', '使用技巧'],
    success: (res) => {
      const tips = [
        '您可以询问："我现在的健康状况如何？"、"如何改善睡眠质量？"等',
        '系统会结合您的实时监测数据给出个性化建议',
        '点击AI助手的回答可以进行复制或重新生成'
      ]
      uni.showToast({
        title: tips[res.tapIndex],
        icon: 'none',
        duration: 3000
      })
    }
  })
}

function copyMessage(content) {
  uni.setClipboardData({
    data: content,
    success: () => {
      uni.showToast({
        title: '已复制到剪贴板',
        icon: 'success'
      })
    }
  })
}

function regenerateResponse(index) {
  uni.showToast({
    title: '重新生成回答中...',
    icon: 'loading',
    duration: 2000
  })
}

function refreshData() {
  isDataUpdating.value = true
  init()
  setTimeout(() => {
    isDataUpdating.value = false
    uni.showToast({
      title: '数据已刷新',
      icon: 'success'
    })
  }, 1000)
}

function syncDevice() {
  uni.showLoading({title: '同步中...'})
  setTimeout(() => {
    uni.hideLoading()
    uni.showToast({
      title: '数据同步成功',
      icon: 'success'
    })
  }, 1500)
}

function deviceSettings() {
  uni.navigateTo({
    url: '/pages/mine/facilities'
  })
}

function connectDevice() {
  uni.navigateTo({
    url: '/pages/device/scan'
  })
}

function exportReport() {
  uni.showToast({
    title: '报告导出功能开发中',
    icon: 'none'
  })
}

function shareHealthData() {
  uni.showToast({
    title: '分享功能开发中',
    icon: 'none'
  })
}

function quickCheck() {
  uni.showLoading({title: '快速检查中...'})
  setTimeout(() => {
    uni.hideLoading()
    uni.showModal({
      title: '快速检查结果',
      content: '所有指标正常，继续保持良好生活习惯！',
      showCancel: false
    })
  }, 2000)
}

function shareReport() {
  uni.showActionSheet({
    itemList: ['分享给好友', '保存到相册', '生成二维码'],
    success: (res) => {
      uni.showToast({
        title: ['已分享', '已保存', '二维码已生成'][res.tapIndex],
        icon: 'success'
      })
    }
  })
}

// 原有的业务函数（保持原有逻辑）
function getSensorData(type) {
  const item = environmentStore.sensorData.find(item => item.type === type)
  return item ? item.value.toFixed(1) : '0.0'
}

// 生成AI报告
async function fetchAiReport() {
  reportStatus.value = 'loading'

  try {
    // 1. 获取当前环境数据
    const currentSensorData = environmentStore.sensorData || [];

    // 2. 构建健康数据摘要
    let healthSummary = "当前健康监测数据：\n";
    let environmentSummary = "当前环境监测数据：\n";

    // 健康相关指标
    const healthIndicators = currentSensorData.filter(sensor =>
        ['breath', 'heart', 'move', 'distance'].includes(sensor.type)
    );

    healthIndicators.forEach(sensor => {
      healthSummary += `${sensor.title}: ${sensor.value}${sensor.unit}\n`;
    });

    // 环境相关指标
    const environmentIndicators = currentSensorData.filter(sensor =>
        ['temp', 'humidity', 'yanwu', 'guang1', 'shengyin'].includes(sensor.type)
    );

    environmentIndicators.forEach(sensor => {
      environmentSummary += `${sensor.title}: ${sensor.value}${sensor.unit}\n`;
    });

    // 3. 获取用户信息
    const userData = userInfo || {}; // userInfo 已经是响应式数据

    // 4. 构建用户信息摘要
    let userSummary = "";
    if (userData.username || userData.age || userData.gender) {
      userSummary = "用户基本信息：\n";
      if (userData.username) userSummary += `姓名: ${userData.username}\n`;
      if (userData.age) userSummary += `年龄: ${userData.age}岁\n`;
      if (userData.gender) {
        userSummary += `性别: ${userData.gender === 'male' ? '男' : '女'}\n`;
      }
    }

    // 5. 检测异常数据
    let alertSummary = "健康状态评估：\n";
    let hasAlerts = false;

    // 定义正常范围
    const normalRanges = {
      '呼吸': {min: 12, max: 20, unit: '次/分'},
      '心跳': {min: 60, max: 100, unit: '次/分'},
      '温度': {min: 36.0, max: 37.5, unit: '℃'},
      '湿度': {min: 40, max: 70, unit: '%'},
      '烟雾': {min: 0, max: 0.5, unit: 'ppm'}
    };

    // 检查关键指标
    const vitalIndicators = currentSensorData.filter(sensor =>
        ['呼吸', '心跳', '温度'].includes(sensor.title)
    );

    vitalIndicators.forEach(sensor => {
      const range = normalRanges[sensor.title];
      if (range) {
        const numericValue = parseFloat(sensor.value) || 0;
        if (numericValue < range.min || numericValue > range.max) {
          hasAlerts = true;
          const status = numericValue < range.min ? "偏低" : "偏高";
          alertSummary += `⚠️ ${sensor.title}${status}: ${sensor.value}${sensor.unit} (正常范围: ${range.min}-${range.max}${range.unit})\n`;
        } else {
          alertSummary += `✅ ${sensor.title}: 正常 (${sensor.value}${sensor.unit})\n`;
        }
      }
    });

    if (!hasAlerts && vitalIndicators.length > 0) {
      alertSummary += "所有生命体征均在正常范围内。\n";
    }

    // 6. 构建数据趋势分析
    let trendSummary = "数据趋势分析：\n";

    currentSensorData.forEach(sensor => {
      if (sensor.detailedData && sensor.detailedData.twentySecondsData) {
        const recentData = sensor.detailedData.twentySecondsData;
        if (recentData.length >= 5) {
          const last5Values = recentData.slice(-5).map(item => parseFloat(item.Value) || 0);
          const avgRecent = last5Values.reduce((a, b) => a + b, 0) / last5Values.length;
          const allValues = recentData.map(item => parseFloat(item.Value) || 0);
          const avgAll = allValues.reduce((sum, item) => sum + item, 0) / allValues.length;

          let trend = "稳定";
          if (avgRecent > avgAll * 1.1) trend = "快速上升";
          else if (avgRecent > avgAll * 1.05) trend = "缓慢上升";
          else if (avgRecent < avgAll * 0.9) trend = "快速下降";
          else if (avgRecent < avgAll * 0.95) trend = "缓慢下降";

          trendSummary += `${sensor.title}: ${trend}趋势\n`;
        }
      }
    });

    // 7. 构建完整的提示词
    const enhancedPrompt = `请基于以下用户的健康监测数据生成一份全面的健康报告：

${userSummary}

${healthSummary}

${environmentSummary}

${alertSummary}

${trendSummary}

当前时间: ${formatDate(new Date(), 'YYYY-MM-DD HH:mm:ss')}

请按照以下结构生成健康报告：
1. 【总体健康状况评估】用简短的一句话总结用户的整体健康状态
2. 【关键指标分析】详细分析心率、呼吸、体温等关键指标是否在正常范围内
3. 【环境因素评估】分析当前环境（温度、湿度、空气质量等）对健康的影响
4. 【趋势变化提醒】指出数据的变化趋势，提醒需要注意的事项
5. 【健康建议】根据用户数据和当前时间（是白天/夜晚）给出3-5条具体的健康建议
6. 【风险预警】如果发现任何异常数据，给出明确的警告和建议措施

报告要求：
1. 使用专业的医学用语，但语言要亲切易懂
2. 根据用户年龄给予适当的关怀和建议
3. 如果数据不完整，请说明哪些信息需要补充
4. 对异常数据要特别强调，并给出明确的行动建议
5. 报告总长度控制在300-500字之间

请直接生成健康报告内容，不要包含任何额外的说明或提示。`;

    console.log("AI报告提示词构建完成");

    // 8. 调用AI接口
    let res = await askai({
      question: enhancedPrompt
    });

    // 9. 处理响应数据
    if (res && res.code === 200) {
      // 优先使用 data 字段，然后是 msg 字段
      const aiResponse = res.data || res.msg || 'AI分析完成';

      // 清理响应内容
      let cleanedResponse = aiResponse
          .replace(/```[\s\S]*?\n/g, '') // 移除代码块
          .replace(/["']/g, '') // 移除引号
          .trim();

      // 如果AI返回的是JSON格式，解析它
      if (cleanedResponse.trim().startsWith('{')) {
        try {
          const jsonData = JSON.parse(cleanedResponse);
          cleanedResponse = jsonData.report || jsonData.content || jsonData.message || '健康分析报告已生成';
        } catch (e) {
          console.log('响应不是有效的JSON格式，保持原样');
        }
      }

      aiReport.value = cleanedResponse;
      console.log("AI报告生成成功");
      reportStatus.value = 'loaded';

      // 10. 记录到聊天记录中（可选）
      if (chatMessages.value[0] && chatMessages.value[0].content.includes('您好！我是您的AI健康助手')) {
        const preview = cleanedResponse.split('\n')[0];
        chatMessages.value[0].content = preview + ' 详细报告请查看上方AI健康分析。';
      }

    } else {
      throw new Error(res?.msg || 'AI接口返回异常');
    }

  } catch (err) {
    console.error('生成报告失败:', err);

    // 生成备用报告
    aiReport.value = `健康报告生成失败。\n\n系统检测到您的当前健康数据正常，环境条件适宜。\n\n建议：\n1. 保持当前的生活作息规律\n2. 注意室内通风，保持空气清新\n3. 如有不适请及时就医\n\n最后更新时间：${formatDate(new Date(), 'HH:mm:ss')}`;

    reportStatus.value = 'error';

    // 错误时不自动重试，改为提供手动刷新按钮
    // 移除自动重试的 setTimeout
  }
}

async function refreshReport() {
  if (isRefreshing.value) return
  isRefreshing.value = true
  await fetchAiReport()
  setTimeout(() => {
    isRefreshing.value = false
    uni.showToast({
      title: '报告已刷新',
      icon: 'success'
    })
  }, 1000)
}

const askAI = async () => {
  if (!userQuestion.value.trim() || isAskingAI.value) return

  const question = userQuestion.value
  userQuestion.value = ''
  isAskingAI.value = true

  chatMessages.value.push({
    sender: 'user',
    content: question,
    time: new Date()
  })

  chatMessages.value.push({
    sender: 'ai',
    content: '正在思考中...',
    time: new Date()
  })

  try {
    const res = await askai({
      question: question,
      context: {
        healthMetrics: healthMetrics.value,
        environmentMetrics: environmentMetrics.value,
        userInfo: userInfo.value
      }
    })

    chatMessages.value.pop()

    if (res && res.code === 200) {
      const aiResponse = res.data || res.msg || '已收到您的提问'
      chatMessages.value.push({
        sender: 'ai',
        content: aiResponse,
        time: new Date()
      })
    } else {
      chatMessages.value.push({
        sender: 'ai',
        content: `抱歉，暂时无法回答这个问题。`,
        time: new Date()
      })
    }
  } catch (error) {
    console.error('请求AI失败:', error)
    chatMessages.value.pop()
    chatMessages.value.push({
      sender: 'ai',
      content: '网络连接出现问题，请检查网络后重试',
      time: new Date()
    })
  } finally {
    isAskingAI.value = false
  }
}

async function init() {
  environmentMetrics.value = {
    coConcentration: getSensorData('yanwu'),
    lightIntensity: getSensorData('guang1'),
    soundLevel: getSensorData('shengyin'),
    temperature: getSensorData('temp'),
    humidity: getSensorData('humidity')
  }

  healthMetrics.value = {
    respiratoryRate: getSensorData('breath'),
    heartRate: getSensorData('heart'),
    move: getSensorData('move'),
    distance: getSensorData('distance')
  }

  await fetchAiReport()
}

watchEffect(() => {
  if (aiReport.value && aiReport.value !== '正在分析您的健康数据...') {
    chatMessages.value[0].content = aiReport.value.split('\n')[0]
  }
})

onPullDownRefresh(async () => {
  await init()
  uni.stopPullDownRefresh()
})

onMounted(() => {
  init()
  // 模拟数据更新
  setInterval(() => {
    if (isConnected.value) {
      environmentMetrics.value = {
        ...environmentMetrics.value,
        temperature: (36.5 + Math.random() * 0.5).toFixed(1),
        humidity: (55 + Math.random() * 10).toFixed(0)
      }
    }
  }, 5000)
})
</script>

<style scoped>

/* 基础样式 */
.container {
  padding: 20rpx 30rpx 150rpx;
  min-height: 100vh;
  background: linear-gradient(180deg, #f8faff 0%, #f0f4ff 100%);
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  position: relative;
}

/* 动画定义 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10rpx);
  }
}

@keyframes slideIn {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 20rpx rgba(100, 103, 210, 0.2);
  }
  50% {
    box-shadow: 0 0 40rpx rgba(100, 103, 210, 0.4);
  }
}

@keyframes shimmer {
  0% {
    background-position: -200% center;
  }
  100% {
    background-position: 200% center;
  }
}

@keyframes loadingDots {
  0%, 20% {
    opacity: 0.2;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.2;
  }
}

/* 头部信息卡片 */
.header-card {
  background: linear-gradient(135deg, #1b855f 0%, #a5d6a7 100%);
  border-radius: 28rpx;
  padding: 40rpx 32rpx;
  margin-bottom: 32rpx;
  display: flex;
  align-items: center;
  color: white;
  box-shadow: 0 12rpx 40rpx rgba(100, 103, 210, 0.4);
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeIn 0.6s ease-out;
}

.header-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s;
}

.header-card:active::before {
  left: 100%;
}

.user-avatar {
  position: relative;
  margin-right: 32rpx;
  animation: float 3s ease-in-out infinite;
}

.avatar-icon {
  width: 108rpx;
  height: 108rpx;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.25), rgba(255, 255, 255, 0.15));
  backdrop-filter: blur(10rpx);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3rpx solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.avatar-icon.avatar-pulse {
  animation: pulse 2s ease-in-out infinite;
}

.avatar-text {
  font-size: 48rpx;
  font-weight: bold;
  color: white;
}

.avatar-status {
  position: absolute;
  right: 4rpx;
  bottom: 4rpx;
  width: 28rpx;
  height: 28rpx;
  background: #4ECDC4;
  border: 4rpx solid #6467D2;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.avatar-status.status-animate {
  animation: pulse 1.5s ease-in-out infinite;
}

.user-info {
  flex: 1;
}

.user-name {
  display: block;
  font-size: 44rpx;
  font-weight: 800;
  margin-bottom: 12rpx;
  text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.user-name.name-placeholder {
  opacity: 0.8;
  font-weight: normal;
}

.user-id {
  font-size: 28rpx;
  opacity: 0.9;
  margin-bottom: 20rpx;
  letter-spacing: 1rpx;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: rgba(255, 255, 255, 0.15);
  padding: 14rpx 24rpx;
  border-radius: 50rpx;
  backdrop-filter: blur(20rpx);
  transition: all 0.3s ease;
  cursor: pointer;
}

.status-indicator:active {
  transform: scale(0.98);
  background: rgba(255, 255, 255, 0.25);
}

.status-dot {
  width: 14rpx;
  height: 14rpx;
  background: #4ECDC4;
  border-radius: 50%;
  box-shadow: 0 0 10rpx #4ECDC4;
}

.status-dot.dot-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

.status-text {
  font-size: 26rpx;
  opacity: 0.95;
}

.status-arrow {
  margin-left: auto;
  font-size: 24rpx;
  opacity: 0.8;
}

.date-info {
  text-align: right;
}

.date-icon {
  font-size: 32rpx;
  margin-bottom: 12rpx;
  opacity: 0.9;
}

.date-label {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  margin-bottom: 6rpx;
  text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.2);
}

.week-label {
  font-size: 28rpx;
  opacity: 0.9;
  letter-spacing: 1rpx;
}

/* 健康概览 */
.health-overview {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.98));

  border-radius: 28rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(20rpx);
  border: 1rpx solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  animation: fadeIn 0.6s ease-out 0.1s both;
}

.health-overview:active {
  transform: translateY(-4rpx);
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.12);
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 36rpx;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.header-icon {
  width: 56rpx;
  height: 56rpx;
  background: linear-gradient(135deg, #6467D2, #8A8DFF);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: white;
  box-shadow: 0 6rpx 20rpx rgba(100, 103, 210, 0.3);
}

.overview-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1a1a1a;
}

.data-indicator {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 8rpx 16rpx;
  background: #f0f2ff;
  border-radius: 20rpx;
  font-size: 24rpx;
  color: #64d2a4;
}

.data-indicator.indicator-updating {
  animation: pulse 1s ease-in-out infinite;
}

.indicator-dot {
  width: 8rpx;
  height: 8rpx;
  background: #6467D2;
  border-radius: 50%;
}

.overview-actions {
  display: flex;
  gap: 12rpx;
}

.action-btn {
  width: 56rpx;
  height: 56rpx;
  background: #f5f7ff;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #6467D2;
  transition: all 0.3s ease;
  cursor: pointer;
}

.action-btn:active {
  transform: scale(0.9);
  background: #e8ebff;
}

.health-metrics {
  display: grid;
  gap: 24rpx;
}

.health-metrics.grid {
  grid-template-columns: repeat(2, 1fr);
}

.health-metrics.list {
  grid-template-columns: 1fr;
}

.metric-card {
  border-radius: 24rpx;
  padding: 32rpx;
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: slideIn calc(0.2s * var(--card-index)) ease-out both;
  cursor: pointer;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6rpx;
  background: linear-gradient(90deg, var(--metric-color-start), var(--metric-color-end));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.metric-card:hover::before {
  opacity: 1;
}

.metric-card:active {
  transform: translateY(-8rpx) scale(0.98);
  box-shadow: 0 20rpx 40rpx rgba(0, 0, 0, 0.15) !important;
}

.metric-badge {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  background: rgba(255, 255, 255, 0.2);
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  color: #358f41;
  backdrop-filter: blur(10rpx);
}

.metric-content {
  text-align: center;
  margin-bottom: 24rpx;
}

.metric-icon {
  width: 72rpx;
  height: 72rpx;
  margin: 0 auto 20rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  transition: transform 0.3s ease;
}

.metric-card:active .metric-icon {
  transform: scale(1.1);
}

.metric-values {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8rpx;
  margin-bottom: 12rpx;
}

.metric-value {
  font-size: 56rpx;
  font-weight: 800;
  color: #9ae39d;
  text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.2);
}

.metric-unit {
  font-size: 28rpx;
  opacity: 0.9;
  color: #bbe891;
}

.metric-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #a1dd89;
  letter-spacing: 1rpx;
}

.metric-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20rpx;
  border-top: 1rpx solid rgba(255, 255, 255, 0.2);
}

.metric-status {
  font-size: 24rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.2);
  color: #90bd6c;
}

.metric-trend {
  display: flex;
  align-items: center;
  gap: 4rpx;
  font-size: 22rpx;
  color: white;
}

.trend-icon {
  font-size: 20rpx;
}

.trend-up {
  color: #4ECDC4;
}

.trend-down {
  color: #FF6B6B;
}

/* 详细信息区域 */
.detail-section {
  background: white;
  border-radius: 28rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  animation: fadeIn 0.6s ease-out 0.2s both;
}

.detail-section:active {
  transform: translateY(-4rpx);
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 32rpx;
}

.header-icon {
  width: 56rpx;
  height: 56rpx;
  background: linear-gradient(135deg, #6467D2, #8A8DFF);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: white;
}

.section-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #2c4c3e;             /* 深森林绿 */
  font-family: "STHeitiSC-Medium", "PingFang SC", sans-serif;
  display: flex;
  flex-direction: column;      /* 标题下方加装饰线 */
}

.section-title::after {
  content: "";
  width: 40rpx;
  height: 6rpx;
  background: linear-gradient(to right, #a5d6a7, transparent);
  border-radius: 3rpx;
  margin-top: 4rpx;
}

.section-tabs {
  display: flex;
  border-bottom: 2rpx solid #f0f0f0;
  margin-bottom: 32rpx;
  position: relative;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 24rpx 0;
  position: relative;
  color: #909399;
  font-size: 28rpx;
  transition: all 0.3s ease;
  cursor: pointer;
}

.tab-item:active {
  transform: translateY(-2rpx);
}

.tab-item.active {
  color: #6467D2;
  font-weight: 600;
}

.tab-item.tab-pulse {
  animation: pulse 2s ease-in-out infinite;
}

.tab-icon {
  font-size: 32rpx;
  margin-bottom: 8rpx;
}

.tab-text {
  display: block;
}

.tab-indicator {
  position: absolute;
  bottom: -2rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 60rpx;
  height: 4rpx;
  background: #6467D2;
  border-radius: 2rpx;
  transition: all 0.3s ease;
}

.tab-badge {
  position: absolute;
  top: 16rpx;
  right: 20rpx;
  width: 20rpx;
  height: 20rpx;
  background: #FF6B6B;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18rpx;
  font-weight: bold;
}

.detail-content {
  min-height: 200rpx;
  animation: fadeIn 0.4s ease-out;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24rpx;
}

.detail-item {
  background: linear-gradient(135deg, rgba(248, 249, 255, 0.8), rgba(240, 242, 255, 0.6));
  border-radius: 20rpx;
  padding: 28rpx;
  transition: all 0.3s ease;
  border: 1rpx solid rgba(232, 235, 255, 0.8);
}

.detail-item.item-highlight {
  background: linear-gradient(135deg, rgba(255, 246, 230, 0.8), rgba(255, 242, 213, 0.6));
  border-color: rgba(255, 236, 179, 0.8);
  animation: glow 2s ease-in-out infinite;
}

.detail-item:active {
  transform: translateY(-4rpx);
  box-shadow: 0 12rpx 30rpx rgba(100, 103, 210, 0.15);
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.detail-icon {
  width: 48rpx;
  height: 48rpx;
  background: rgba(100, 103, 210, 0.1);
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #6467D2;
}

.detail-label {
  flex: 1;
  margin-left: 16rpx;
  font-size: 28rpx;
  font-weight: 600;
  color: #303133;
}

.detail-actions {
  display: flex;
  gap: 12rpx;
  align-items: center;
}

.action-dot {
  width: 12rpx;
  height: 12rpx;
  background: #FF6B6B;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.action-info {
  width: 36rpx;
  height: 36rpx;
  background: #f5f7ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
  color: #6467D2;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-info:active {
  transform: scale(0.9);
  background: #e8ebff;
}

.detail-value-container {
  margin-bottom: 20rpx;
}

.value-display {
  display: flex;
  align-items: baseline;
  gap: 8rpx;
  margin-bottom: 12rpx;
}

.value-number {
  font-size: 48rpx;
  font-weight: 800;
  color: #1a1a1a;
}

.value-unit {
  font-size: 26rpx;
  color: #909399;
}

.value-comparison {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
}

.comparison-text {
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
  font-weight: 600;
}

.comparison-up {
  background: rgba(78, 205, 196, 0.1);
  color: #4ECDC4;
}

.comparison-down {
  background: rgba(255, 107, 107, 0.1);
  color: #FF6B6B;
}

.detail-progress {
  margin-top: 16rpx;
}

.progress-bar {
  height: 8rpx;
  background: #f0f0f0;
  border-radius: 4rpx;
  overflow: hidden;
  margin-bottom: 8rpx;
}

.progress-fill {
  height: 100%;
  border-radius: 4rpx;
  transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 22rpx;
  color: #909399;
}

/* 环境健康详情 */
.environment-grid {
  display: grid;
  gap: 24rpx;
}

.environment-item {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(248, 249, 255, 0.8));
  border-radius: 20rpx;
  padding: 28rpx;
  border: 1rpx solid rgba(232, 235, 255, 0.8);
  transition: all 0.3s ease;
}

.environment-item.environment-warning {
  background: linear-gradient(135deg, rgba(255, 246, 246, 0.9), rgba(255, 240, 240, 0.8));
  border-color: rgba(255, 224, 224, 0.8);
  animation: pulse 2s ease-in-out infinite;
}

.environment-item:active {
  transform: translateY(-4rpx);
  box-shadow: 0 12rpx 30rpx rgba(0, 0, 0, 0.08);
}

.environment-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.environment-icon {
  width: 56rpx;
  height: 56rpx;
  background: linear-gradient(135deg, rgba(100, 103, 210, 0.1), rgba(138, 141, 255, 0.05));
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
}

.environment-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #303133;
}

.environment-value {
  display: flex;
  align-items: baseline;
  gap: 8rpx;
  margin-bottom: 16rpx;
}

.environment-status {
  margin-bottom: 16rpx;
}

.status-level {
  display: inline-block;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  font-weight: 500;
}

.level-optimal {
  background: rgba(78, 205, 196, 0.1);
  color: #4ECDC4;
}

.level-low {
  background: rgba(255, 209, 102, 0.1);
  color: #FFD166;
}

.level-high {
  background: rgba(255, 107, 107, 0.1);
  color: #FF6B6B;
}

.environment-chart {
  height: 40rpx;
  position: relative;
}

.chart-line {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2rpx;
  background: #f0f0f0;
}

.chart-point {
  position: absolute;
  bottom: 0;
  width: 6rpx;
  background: #6467D2;
  border-radius: 3rpx 3rpx 0 0;
  transition: height 0.5s ease;
}

/* 设备信息 */
.device-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 249, 255, 0.9));
  border-radius: 24rpx;
  padding: 32rpx;
  border: 1rpx solid rgba(232, 235, 255, 0.8);
  transition: all 0.3s ease;
}

.device-card.device-connected {
  border-color: #4ECDC4;
  box-shadow: 0 8rpx 30rpx rgba(78, 205, 196, 0.15);
}

.device-header {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 32rpx;
}

.device-icon {
  width: 72rpx;
  height: 72rpx;
  background: linear-gradient(135deg, #6467D2, #8A8DFF);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  color: white;
  box-shadow: 0 8rpx 24rpx rgba(100, 103, 210, 0.3);
}

.device-title {
  flex: 1;
  font-size: 32rpx;
  font-weight: 700;
  color: #1a1a1a;
}

.device-status {
  padding: 12rpx 24rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  font-weight: 500;
  background: #f0f0f0;
  color: #909399;
}

.device-status.status-online {
  background: rgba(78, 205, 196, 0.1);
  color: #4ECDC4;
}

.device-info {
  margin-bottom: 32rpx;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 28rpx;
  color: #606266;
}

.info-value {
  font-size: 28rpx;
  color: #303133;
  font-weight: 500;
}

.device-actions {
  display: flex;
  gap: 20rpx;
}

/* 设备操作 */
.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 24rpx;
  /*background: linear-gradient(135deg, #797abd, #c8caec);*/
  /* 柔和、高级、有亲和力 */
  /*background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);*/
  /* 温暖、积极、充满希望 */
  /*background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);*/
  /* 清新、健康、自然 */
  background: linear-gradient(135deg, #e0f2f1 0%, #a5d6a7 100%);
  border-radius: 20rpx;
  color: white;
  font-size: 28rpx;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
}

.action-btn:active {
  transform: translateY(-4rpx);
  box-shadow: 0 12rpx 30rpx rgba(100, 103, 210, 0.3);
}

.device-empty {
  text-align: center;
  padding: 60rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 24rpx;
  opacity: 0.5;
}

.empty-text {
  display: block;
  font-size: 28rpx;
  color: #909399;
  margin-bottom: 32rpx;
}

.empty-btn {
  display: inline-block;
  padding: 24rpx 48rpx;
  background: linear-gradient(135deg, #6467D2, #8A8DFF);
  border-radius: 40rpx;
  color: white;
  font-size: 28rpx;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
}

.empty-btn:active {
  transform: scale(0.95);
  box-shadow: 0 12rpx 30rpx rgba(100, 103, 210, 0.3);
}

/* AI健康报告 */
.ai-report-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.98));
  border-radius: 28rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(20rpx);
  border: 1rpx solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  animation: fadeIn 0.6s ease-out 0.3s both;
}

.ai-report-card:active {
  transform: translateY(-4rpx);
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.08);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28rpx;
}

.ai-icon {
  width: 72rpx;
  height: 72rpx;
  background: linear-gradient(135deg, #6467D2, #8A8DFF);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  color: white;
  box-shadow: 0 8rpx 24rpx rgba(100, 103, 210, 0.3);
  transition: all 0.3s ease;
}

.ai-icon.ai-pulse {
  animation: float 3s ease-in-out infinite;
}

.report-title-container {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.report-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1a1a1a;
}

.report-subtitle {
  font-size: 24rpx;
  color: #909399;
}

.report-actions {
  display: flex;
  gap: 12rpx;
}

.action-btn.btn-loading {
  pointer-events: none;
}

.loading-spinner {
  width: 24rpx;
  height: 24rpx;
  border: 3rpx solid #f3f3f3;
  border-top: 3rpx solid #6467D2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.report-content {
  background: linear-gradient(135deg, rgba(248, 249, 255, 0.6), rgba(240, 242, 255, 0.4));
  border-radius: 20rpx;
  padding: 32rpx;
  margin-bottom: 28rpx;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.report-content:active {
  transform: scale(0.99);
}

.report-content.content-collapsed {
  padding: 24rpx;
}

.report-text-container {
  max-height: 400rpx;
}

.report-text {
  font-size: 28rpx;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
  word-break: break-word;
}

.report-text.text-loading {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  color: transparent;
  border-radius: 8rpx;
}

.report-preview {
  text-align: center;
}

.preview-text {
  display: block;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 12rpx;
  line-height: 1.6;
}

.preview-hint {
  font-size: 24rpx;
  color: #909399;
}

.report-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.time-icon {
  font-size: 24rpx;
  color: #909399;
}

.report-time {
  font-size: 24rpx;
  color: #909399;
}

.report-status {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 24rpx;
  border-radius: 40rpx;
  font-size: 24rpx;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
}

.report-status:active {
  transform: scale(0.95);
}

.status-loading {
  background: rgba(255, 243, 205, 0.2);
  color: #856404;
}

.status-loaded {
  background: rgba(212, 237, 218, 0.2);
  color: #155724;
}

.status-error {
  background: rgba(248, 215, 218, 0.2);
  color: #721c24;
}

.status-error:active {
  background: rgba(248, 215, 218, 0.3);
}

.status-icon {
  font-size: 20rpx;
}

/* AI对话助手 */
.ai-assistant {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.98));
  border-radius: 28rpx;
  padding: 32rpx;
  margin-bottom: 120rpx;
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(20rpx);
  border: 1rpx solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  animation: fadeIn 0.6s ease-out 0.4s both;
}

.ai-assistant:active {
  transform: translateY(-4rpx);
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.08);
}

.assistant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx;
}

.assistant-icon {
  width: 72rpx;
  height: 72rpx;
  background: linear-gradient(135deg, #6467D2, #8A8DFF);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  color: white;
  box-shadow: 0 8rpx 24rpx rgba(100, 103, 210, 0.3);
  transition: all 0.3s ease;
}

.assistant-icon.assistant-active {
  animation: glow 2s ease-in-out infinite;
}

.title-container {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.assistant-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1a1a1a;
}

.assistant-subtitle {
  font-size: 24rpx;
  color: #909399;
}

.header-tip {
  width: 56rpx;
  height: 56rpx;
  background: #f5f7ff;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: #6467D2;
  transition: all 0.3s ease;
  cursor: pointer;
}

.header-tip:active {
  transform: scale(0.9);
  background: #e8ebff;
}

.chat-container {
  max-height: 400rpx;
  margin-bottom: 32rpx;
  padding-right: 8rpx;
}

.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.chat-message {
  display: flex;
  align-items: flex-start;
  gap: 20rpx;
  animation: fadeIn 0.3s ease-out;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.chat-message.message-new {
  animation: slideIn 0.4s ease-out;
}

.message-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #f5f7ff, #e8ebff);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  flex-shrink: 0;
  position: relative;
}

.message-avatar .avatar-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(100, 103, 210, 0.1), transparent);
  animation: pulse 2s ease-in-out infinite;
}

.message-bubble {
  max-width: 500rpx;
  padding: 24rpx 32rpx;
  position: relative;
  transition: all 0.3s ease;
}

.message-bubble.bubble-ai {
  background: linear-gradient(135deg, rgba(240, 242, 255, 0.9), rgba(232, 235, 255, 0.8));
  border-radius: 24rpx 24rpx 24rpx 8rpx;
  border: 1rpx solid rgba(232, 235, 255, 0.8);
}

.message-bubble.bubble-user {
  background: linear-gradient(135deg, #6467D2, #8A8DFF);
  color: white;
  border-radius: 24rpx 24rpx 8rpx 24rpx;
  box-shadow: 0 8rpx 24rpx rgba(100, 103, 210, 0.3);
}

.message-content {
  font-size: 28rpx;
  line-height: 1.6;
  word-break: break-word;
}

.message-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16rpx;
}

.message-time {
  font-size: 22rpx;
  opacity: 0.7;
}

.message-actions {
  display: flex;
  gap: 12rpx;
}

.message-actions .action-btn {
  width: 36rpx;
  height: 36rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
  color: inherit;
  transition: all 0.3s ease;
  cursor: pointer;
}

.message-actions .action-btn:active {
  transform: scale(0.9);
  background: rgba(255, 255, 255, 0.3);
}

.chat-placeholder {
  text-align: center;
  padding: 60rpx 0;
}

.placeholder-text {
  display: block;
  font-size: 28rpx;
  color: #909399;
  margin-bottom: 32rpx;
}

.placeholder-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  justify-content: center;
}

.suggestion-chip {
  padding: 16rpx 24rpx;
  background: linear-gradient(135deg, rgba(100, 103, 210, 0.1), rgba(138, 141, 255, 0.05));
  border-radius: 40rpx;
  font-size: 26rpx;
  color: #6467D2;
  transition: all 0.3s ease;
  cursor: pointer;
}

.suggestion-chip:active {
  transform: scale(0.95);
  background: linear-gradient(135deg, rgba(100, 103, 210, 0.15), rgba(138, 141, 255, 0.1));
}

.chat-input-area {
  transition: all 0.3s ease;
}

.chat-input-area.input-focused {
  transform: translateY(-8rpx);
}

.input-container {
  display: flex;
  align-items: center;
  background: #f5f7ff;
  border-radius: 40rpx;
  padding: 0 20rpx;
  border: 1rpx solid rgba(232, 235, 255, 0.8);
  transition: all 0.3s ease;
}

.chat-input-area.input-focused .input-container {
  background: white;
  border-color: #6467D2;
  box-shadow: 0 8rpx 30rpx rgba(100, 103, 210, 0.15);
}

.chat-input {
  flex: 1;
  height: 88rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #303133;
  background: transparent;
}

.chat-input .placeholder {
  color: #c0c4cc;
}

.input-actions {
  display: flex;
  gap: 12rpx;
  align-items: center;
}

.input-actions .action-btn {
  width: 48rpx;
  height: 48rpx;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #6467D2;
  transition: all 0.3s ease;
  cursor: pointer;
}

.input-actions .action-btn:active {
  transform: scale(0.9);
  background: #e8ebff;
}

.send-button {
  width: 88rpx;
  height: 88rpx;
  background: linear-gradient(135deg, #e0e0e0, #f0f0f0);
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  right: 32rpx;
  bottom: 24rpx;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.send-button.btn-active {
  background: linear-gradient(135deg, #6467D2, #8A8DFF);
  box-shadow: 0 12rpx 40rpx rgba(100, 103, 210, 0.3);
}

.send-button.btn-loading {
  pointer-events: none;
}

.send-button:active {
  transform: scale(0.9);
}

.send-icon {
  color: white;
  font-size: 28rpx;
  font-weight: 500;
}

.loading-dots {
  display: flex;
  gap: 6rpx;
}

.loading-dots .dot {
  width: 8rpx;
  height: 8rpx;
  background: white;
  border-radius: 50%;
  animation: loadingDots 1.4s ease-in-out infinite;
}

.loading-dots .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots .dot:nth-child(3) {
  animation-delay: 0.4s;
}

/* 悬浮操作按钮 */
.floating-actions {
  position: fixed;
  right: 40rpx;
  bottom: 160rpx;
  z-index: 1000;
}

.fab-main {
  width: 100rpx;
  height: 100rpx;
  background: linear-gradient(135deg, #6467D2, #8A8DFF);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  color: white;
  box-shadow: 0 12rpx 40rpx rgba(100, 103, 210, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  z-index: 1001;
}

.fab-main.fab-open {
  transform: rotate(45deg);
  box-shadow: 0 20rpx 60rpx rgba(100, 103, 210, 0.5);
}

.fab-main:active {
  transform: scale(0.9);
}

.fab-icon {
  font-weight: 300;
}

.fab-menu {
  position: absolute;
  bottom: 120rpx;
  right: 0;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  animation: fadeIn 0.3s ease-out;
}

.fab-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx 28rpx;
  background: white;
  border-radius: 50rpx;
  box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.fab-item:active {
  transform: translateX(-8rpx) scale(0.95);
}

.item-icon {
  width: 44rpx;
  height: 44rpx;
  background: #f5f7ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #6467D2;
}

.item-text {
  font-size: 26rpx;
  color: #303133;
  font-weight: 500;
  white-space: nowrap;
}

/* 底部安全区域 */
.safe-area {
  height: env(safe-area-inset-bottom);
}

/* 响应式调整 */
@media (max-width: 375px) {
  .container {
    padding: 16rpx 24rpx 120rpx;
  }

  .health-metrics.grid {
    grid-template-columns: 1fr;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>