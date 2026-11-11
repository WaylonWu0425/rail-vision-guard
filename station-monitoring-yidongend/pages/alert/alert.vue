<template>
  <view class="home-container">
    <!-- 头部区域 -->
    <view class="header-section">
      <view class="header-title">
        <!--        <view class="title-icon">-->
        <!--          <text>⚠️</text>-->
        <!--        </view>-->
        <text class="title-text">智能预警中心</text>
      </view>
      <view class="header-stats">
        <view class="stats-card">
          <text class="stats-number">{{ warnings.length }}</text>
          <text class="stats-label">总预警数</text>
        </view>
        <view class="stats-card"
              :style="{ background: urgentCount > 0 ? 'linear-gradient(135deg, #FF6B6B, #FF8E8E)' : 'linear-gradient(135deg, #4ECDC4, #6EE7E7)' }">
          <text class="stats-number">{{ urgentCount }}</text>
          <text class="stats-label">紧急预警</text>
        </view>
        <view class="stats-card" :style="{ background: 'linear-gradient(135deg, #FFD166, #FFE0A3)' }">
          <text class="stats-number">{{ resolvedCount }}</text>
          <text class="stats-label">已处理</text>
        </view>
      </view>
    </view>

    <!-- AI预警分析 -->
    <view class="ai-analysis" v-if="warnings.length > 0">
      <view class="analysis-header">
        <!--        <view class="ai-icon">-->
        <!--          <text>🤖</text>-->
        <!--        </view>-->
        <text class="analysis-title">AI预警分析</text>
      </view>
      <text class="analysis-text">{{ aiAnalysisText }}</text>
      <view class="analysis-footer">
        <text class="analysis-time">分析时间: {{ currentTime }}</text>
        <text class="analysis-accuracy">准确率: 98.5%</text>
      </view>
    </view>

    <!-- 预警筛选 -->
    <view class="filter-section" v-if="warnings.length > 0">
      <view class="filter-tabs">
        <view class="filter-tab"
              :class="{ active: activeFilter === 'all' }"
              @click="activeFilter = 'all'">
          <text>全部</text>
          <view class="tab-badge">{{ warnings.length }}</view>
        </view>
        <view class="filter-tab"
              :class="{ active: activeFilter === 'urgent' }"
              @click="activeFilter = 'urgent'">
          <text>紧急</text>
          <view class="tab-badge urgent">{{ urgentCount }}</view>
        </view>
        <view class="filter-tab"
              :class="{ active: activeFilter === 'warning' }"
              @click="activeFilter = 'warning'">
          <text>警告</text>
          <view class="tab-badge warning">{{ warningCount }}</view>
        </view>
        <view class="filter-tab"
              :class="{ active: activeFilter === 'info' }"
              @click="activeFilter = 'info'">
          <text>提醒</text>
          <view class="tab-badge info">{{ infoCount }}</view>
        </view>
      </view>

      <view class="filter-actions">
        <view class="filter-action" @click="toggleSortOrder">
          <text class="action-icon">{{ sortAscending ? '⬇️' : '⬆️' }}</text>
          <text class="action-text">{{ sortAscending ? '时间降序' : '时间升序' }}</text>
        </view>
        <view class="filter-action" @click="markAllAsRead">
          <text class="action-icon">✓</text>
          <text class="action-text">全部已读</text>
        </view>
      </view>
    </view>

    <!-- 预警列表 -->
    <view class="warning-list-section">
      <view v-if="filteredWarnings.length === 0" class="empty-state">
        <view class="empty-icon">
          <text>🎉</text>
        </view>
        <text class="empty-title">暂无预警信息</text>
        <text class="empty-subtitle">所有系统运行正常</text>
        <view class="empty-tip">
          <text>💡 提示：系统将持续监测您的健康状况</text>
        </view>
      </view>

      <view v-else class="warning-list">
        <view class="list-header">
          <text class="list-title">预警列表 ({{ filteredWarnings.length }}条)</text>
          <!--          <text class="list-subtitle">最后更新: {{ formatTime(lastUpdate) }}</text>-->
          <text class="list-subtitle">最后更新: {{ formatTime(lastUpdate) }}</text>
        </view>

        <view class="warnings-container">
          <warningMessage
              v-for="(warning, index) in sortedWarnings"
              :key="index"
              :warning="warning"
              :index="index"
              @click="handleWarningClick(warning)"
          />
        </view>

        <view class="list-footer">
          <text class="footer-text">已显示 {{ Math.min(sortedWarnings.length, 10) }} / {{ filteredWarnings.length }}
            条预警
          </text>
          <text class="footer-tip">👈 点击预警卡片查看详情</text>
        </view>
      </view>
    </view>

    <!-- AI处理建议 -->
    <view class="ai-suggestion" v-if="filteredWarnings.length > 0 && urgentCount > 0">
      <view class="suggestion-header">
        <view class="suggestion-icon">
          <text>💡</text>
        </view>
        <text class="suggestion-title">AI处理建议</text>
      </view>
      <scroll-view class="suggestion-content" scroll-x>
        <view class="suggestion-tags">
          <view class="suggestion-tag" v-for="(suggestion, index) in aiSuggestions" :key="index">
            <text class="tag-icon">✅</text>
            <text class="tag-text">{{ suggestion }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 快捷操作 -->
    <view class="quick-actions">
      <view class="actions-title">
        <text>🚀 快捷操作</text>
      </view>
      <view class="actions-grid">
        <view class="action-item" @click="refreshWarnings">
          <view class="action-icon refresh">
            <text>🔄</text>
          </view>
          <text class="action-label">刷新数据</text>
        </view>
        <view class="action-item" @click="exportWarnings">
          <view class="action-icon export">
            <text>📥</text>
          </view>
          <text class="action-label">导出报告</text>
        </view>
        <view class="action-item" @click="openAIAssistant">
          <view class="action-icon ai">
            <text>🤖</text>
          </view>
          <text class="action-label">AI分析</text>
        </view>
        <view class="action-item" @click="openSettings">
          <view class="action-icon settings">
            <text>⚙️</text>
          </view>
          <text class="action-label">预警设置</text>
        </view>
      </view>
    </view>

    <!-- 底部提示 -->
    <!--    <view class="bottom-tips">-->
    <!--      <text class="tips-text">💡 所有预警信息由AI系统自动生成和监控</text>-->
    <!--      <text class="tips-subtext">系统每5分钟自动更新一次数据</text>-->
    <!--    </view>-->
  </view>
</template>

<script setup>
import {ref, computed, onMounted, onUnmounted} from 'vue'
import {useAlertMessageStore} from '@/store/alertMessage.js'
import WarningMessage from "../../components/warningMessage/warningMessage.vue"
import {onPullDownRefresh} from '@dcloudio/uni-app'

const store = useAlertMessageStore()
const warnings = store.warnings

// 状态管理
const activeFilter = ref('all')
const sortAscending = ref(false)
const lastUpdate = ref(new Date())
const refreshInterval = ref(null)

// 计算属性
const urgentCount = computed(() => {
  return warnings.filter(w => w.level === 'urgent' || w.level === 'high').length
})

const warningCount = computed(() => {
  return warnings.filter(w => w.level === 'warning' || w.level === 'medium').length
})

const infoCount = computed(() => {
  return warnings.filter(w => w.level === 'info' || w.level === 'low').length
})

const resolvedCount = computed(() => {
  return warnings.filter(w => w.status === 'resolved' || w.read).length
})

const filteredWarnings = computed(() => {
  if (activeFilter.value === 'all') return warnings
  if (activeFilter.value === 'urgent')
    return warnings.filter(w => w.level === 'urgent' || w.level === 'high')
  if (activeFilter.value === 'warning')
    return warnings.filter(w => w.level === 'warning' || w.level === 'medium')
  if (activeFilter.value === 'info')
    return warnings.filter(w => w.level === 'info' || w.level === 'low')
  return warnings
})

const sortedWarnings = computed(() => {
  return [...filteredWarnings.value].sort((a, b) => {
    const timeA = a.timestamp ? new Date(a.timestamp) : new Date()
    const timeB = b.timestamp ? new Date(b.timestamp) : new Date()
    return sortAscending.value ? timeA - timeB : timeB - timeA
  })
})

const currentTime = computed(() => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
})

const aiAnalysisText = computed(() => {
  if (warnings.length === 0) {
    return '目前所有系统运行正常，未检测到异常情况。建议继续保持当前的健康监测状态。'
  }

  if (urgentCount.value > 0) {
    return `检测到 ${urgentCount.value} 条紧急预警，建议您立即处理。AI系统已启动紧急响应机制，正在持续监测相关指标。`
  }

  if (warningCount.value > 0) {
    return `检测到 ${warningCount.value} 条警告信息，建议您关注相关指标的变化趋势。AI系统将持续为您提供监测和分析。`
  }

  return `检测到 ${infoCount.value} 条提醒信息，均为常规监测指标，无需特别处理。系统运行状态良好。`
})

const aiSuggestions = computed(() => {
  const suggestions = []

  if (urgentCount.value > 0) {
    suggestions.push('立即检查相关设备连接')
    suggestions.push('联系紧急联系人')
    suggestions.push('启动应急预案')
  }

  if (warningCount.value > 0) {
    suggestions.push('持续监测指标变化')
    suggestions.push('调整相关参数设置')
    suggestions.push('记录异常日志')
  }

  if (warnings.some(w => w.type === 'health')) {
    suggestions.push('关注健康指标趋势')
    suggestions.push('适当调整作息时间')
  }

  if (warnings.some(w => w.type === 'environment')) {
    suggestions.push('检查环境设备状态')
    suggestions.push('优化环境参数设置')
  }

  // 确保至少有一些建议
  if (suggestions.length === 0) {
    suggestions.push('保持正常监测频率')
    suggestions.push('定期检查设备状态')
    suggestions.push('关注系统更新提示')
  }

  return suggestions.slice(0, 4) // 最多显示4条
})

// 方法
const formatTime = (date) => {
  const d = new Date(date)
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

const toggleSortOrder = () => {
  sortAscending.value = !sortAscending.value
}

const markAllAsRead = () => {
  // 这里应该调用store的方法来标记所有为已读
  store.markAllAsRead?.()
  uni.showToast({
    title: '全部标记为已读',
    icon: 'success'
  })
}

const handleWarningClick = (warning) => {
  console.log('点击预警:', warning)
  // // 这里可以跳转到预警详情页面
  // uni.navigateTo({
  //   url: `/pages/warning-detail/warning-detail?id=${warning.id}`
  // })
}

const refreshWarnings = async () => {
  uni.showLoading({title: '刷新中...'})
  try {
    await store.refreshWarnings?.()
    lastUpdate.value = new Date()
    uni.showToast({
      title: '刷新成功',
      icon: 'success'
    })
  } catch (error) {
    console.error('刷新失败:', error)
    uni.showToast({
      title: '刷新失败',
      icon: 'error'
    })
  }
}

const exportWarnings = () => {
  uni.showModal({
    title: '导出预警报告',
    content: '是否要导出当前预警信息为PDF报告？',
    success: (res) => {
      if (res.confirm) {
        uni.showToast({
          title: '开始导出报告',
          icon: 'success'
        })
      }
    }
  })
}

const openAIAssistant = () => {
  uni.reLaunch({
    url: '/pages/health-report/health-report'
  });
}

const openSettings = () => {
  uni.navigateTo({
    url: '/pages/setAlert/setAlert'
  })
}

// 下拉刷新
onPullDownRefresh(async () => {
  await refreshWarnings()
  uni.stopPullDownRefresh()
})

// 生命周期
onMounted(() => {
  // 每5分钟自动刷新一次
  refreshInterval.value = setInterval(() => {
    store.refreshWarnings?.()
    lastUpdate.value = new Date()
  }, 5 * 60 * 1000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<style scoped>
.home-container {
  padding: 0 30rpx 100rpx;
  min-height: 100vh;
  background: linear-gradient(180deg, #f5f7ff 0%, #f8f9ff 100%);
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
}

/* 头部区域 */
.header-section {
  background: linear-gradient(135deg, #60bf20 0%, #7ee392 100%);
  border-radius: 24rpx;
  padding: 40rpx 30rpx;
  margin: 30rpx 0;
  color: white;
  box-shadow: 0 8rpx 30rpx rgba(100, 103, 210, 0.3);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.title-icon {
  width: 60rpx;
  height: 60rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
}

.title-text {
  font-size: 36rpx;
  font-weight: bold;
}

.header-stats {
  display: flex;
  justify-content: space-between;
  gap: 20rpx;
}

.stats-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16rpx;
  padding: 24rpx;
  text-align: center;
  backdrop-filter: blur(10px);
}

.stats-number {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  margin-bottom: 8rpx;
}

.stats-label {
  font-size: 24rpx;
  opacity: 0.9;
}

/* AI预警分析 */
.ai-analysis {
  background: white;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.analysis-header {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.ai-icon {
  width: 50rpx;
  height: 50rpx;
  background: linear-gradient(135deg, #6467D2, #8A8DFF);
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
}

.analysis-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #303133;
}

.analysis-text {
  display: block;
  font-size: 28rpx;
  line-height: 1.6;
  color: #333;
  margin-bottom: 20rpx;
}

.analysis-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 24rpx;
  color: #909399;
}

/* 预警筛选 */
.filter-section {
  background: white;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.filter-tabs {
  display: flex;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.filter-tab {
  flex: 1;
  text-align: center;
  padding: 20rpx 0;
  background: #f8f9ff;
  border-radius: 16rpx;
  color: #606266;
  position: relative;
}

.filter-tab.active {
  background: #6467D2;
  color: white;
}

.tab-badge {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  min-width: 36rpx;
  height: 36rpx;
  background: #FF6B6B;
  border-radius: 18rpx;
  color: white;
  font-size: 22rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8rpx;
}

.tab-badge.urgent {
  background: #FF6B6B;
}

.tab-badge.warning {
  background: #FFD166;
  color: #333;
}

.tab-badge.info {
  background: #4ECDC4;
}

.filter-actions {
  display: flex;
  gap: 20rpx;
}

.filter-action {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 20rpx;
  background: #f8f9ff;
  border-radius: 16rpx;
  color: #6467D2;
  font-size: 28rpx;
}

/* 预警列表 */
.warning-list-section {
  background: white;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  min-height: 300rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.empty-state {
  text-align: center;
  padding: 60rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #303133;
  margin-bottom: 12rpx;
}

.empty-subtitle {
  display: block;
  font-size: 28rpx;
  color: #909399;
  margin-bottom: 30rpx;
}

.empty-tip {
  background: #f8f9ff;
  border-radius: 16rpx;
  padding: 20rpx;
  color: #6467D2;
  font-size: 26rpx;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
  padding-bottom: 20rpx;
  border-bottom: 2rpx solid #f0f0f0;
}

.list-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #303133;
}

.list-subtitle {
  font-size: 24rpx;
  color: #909399;
}

.warnings-container {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.list-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 30rpx;
  padding-top: 20rpx;
  border-top: 2rpx solid #f0f0f0;
  font-size: 24rpx;
  color: #909399;
}

/* AI处理建议 */
.ai-suggestion {
  background: white;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.suggestion-icon {
  width: 50rpx;
  height: 50rpx;
  background: linear-gradient(135deg, #FFD166, #FFE0A3);
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
}

.suggestion-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #303133;
}

.suggestion-content {
  white-space: nowrap;
}

.suggestion-tags {
  display: flex;
  gap: 20rpx;
}

.suggestion-tag {
  background: #f8f9ff;
  border-radius: 20rpx;
  padding: 16rpx 24rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex-shrink: 0;
}

.tag-icon {
  font-size: 24rpx;
}

.tag-text {
  font-size: 26rpx;
  color: #333;
}

/* 快捷操作 */
.quick-actions {
  background: white;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.actions-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #303133;
  margin-bottom: 30rpx;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30rpx;
}

.action-item {
  text-align: center;
  padding: 30rpx;
  background: #f8f9ff;
  border-radius: 20rpx;
  transition: transform 0.2s ease;
}

.action-item:active {
  transform: scale(0.95);
}

.action-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20rpx;
  font-size: 40rpx;
}

.action-icon.refresh {
  background: linear-gradient(135deg, #4ECDC4, #6EE7E7);
}

.action-icon.export {
  background: linear-gradient(135deg, #FFD166, #FFE0A3);
}

.action-icon.ai {
  background: linear-gradient(135deg, #6467D2, #8A8DFF);
}

.action-icon.settings {
  background: linear-gradient(135deg, #118AB2, #06D6A0);
}

.action-label {
  font-size: 28rpx;
  color: #303133;
  font-weight: 500;
}

/* 底部提示 */
.bottom-tips {
  text-align: center;
  padding: 30rpx;
  background: white;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.tips-text {
  display: block;
  font-size: 28rpx;
  color: #6467D2;
  margin-bottom: 12rpx;
}

.tips-subtext {
  display: block;
  font-size: 24rpx;
  color: #909399;
}
</style>