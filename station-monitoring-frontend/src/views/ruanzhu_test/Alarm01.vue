<template>
  <div class="alarm-container">
    <!-- 顶部标题栏 -->
    <div class="alarm-header">
      <div class="header-left">
        <h1 class="alarm-title">
          <el-icon class="title-icon"><Warning /></el-icon>
          报警管理系统
        </h1>
        <p class="alarm-subtitle">实时监控与处理安全报警信息</p>
      </div>
      <div class="header-stats">
        <div class="stat-item danger">
          <el-icon><WarningFilled /></el-icon>
          <div class="stat-content">
            <span class="stat-value">{{ alarmSummary.danger }}</span>
            <span class="stat-label">危险警告</span>
          </div>
        </div>
        <div class="stat-item camera">
          <el-icon><VideoCameraFilled /></el-icon>
          <div class="stat-content">
            <span class="stat-value">{{ alarmSummary.camera }}</span>
            <span class="stat-label">摄像头警告</span>
          </div>
        </div>
        <div class="stat-item total">
          <el-icon><BellFilled /></el-icon>
          <div class="stat-content">
            <span class="stat-value">{{ alarmSummary.total }}</span>
            <span class="stat-label">未处理总数</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 标签页导航 -->
    <div class="alarm-tabs">
      <div
          v-for="tab in tabs"
          :key="tab.key"
          :class="['tab-item', { active: activeTab === tab.key }]"
          @click="switchTab(tab.key)"
      >
        <el-icon class="tab-icon">
          <component :is="tab.icon" />
        </el-icon>
        <span class="tab-label">{{ tab.label }}</span>
        <span v-if="tab.badge" class="tab-badge">{{ tab.badge }}</span>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="alarm-content">
      <!-- 危险警告 -->
      <div v-if="activeTab === 'danger'" class="tab-pane">
        <div class="tab-header">
          <div class="tab-title">
            <h2><el-icon><Warning /></el-icon> 危险警告管理</h2>
            <p class="tab-description">监控人员/车辆非法进入等危险情况</p>
          </div>
          <div class="tab-actions">
            <el-button @click="refreshAlarmData" :icon="Refresh" circle />
            <el-button @click="handleBatchProcess" type="primary" :icon="Operation">
              批量处理
            </el-button>
          </div>
        </div>

        <div class="filter-card">
          <div class="filter-header">
            <h3><el-icon><Filter /></el-icon> 筛选条件</h3>
            <div class="filter-actions">
              <el-button @click="searchAlarmInfoBtn" type="primary" :icon="Search">
                搜索
              </el-button>
              <el-button @click="clearFilters" :icon="Refresh">
                重置
              </el-button>
            </div>
          </div>

          <div class="filter-form">
            <div class="form-row">
              <div class="form-item">
                <label class="form-label"><el-icon><VideoCamera /></el-icon> 摄像头</label>
                <el-select-v2
                    v-model="searchData.cameraName"
                    filterable
                    :options="cameraOptions"
                    placeholder="请选择摄像头"
                    class="filter-select"
                />
              </div>
              <div class="form-item">
                <label class="form-label"><el-icon><Clock /></el-icon> 时间范围</label>
                <el-select
                    v-model="searchData.day"
                    placeholder="请选择时间"
                    class="filter-select"
                >
                  <el-option
                      v-for="item in dayOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                  />
                </el-select>
              </div>
              <div class="form-item">
                <label class="form-label"><el-icon><Collection /></el-icon> 报警类型</label>
                <el-select
                    v-model="searchData.type"
                    placeholder="请选择类型"
                    class="filter-select"
                >
                  <el-option
                      v-for="item in typeOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                  />
                </el-select>
              </div>
            </div>
          </div>
        </div>

        <div class="table-card">
          <div class="table-header">
            <h3>危险警告列表</h3>
            <div class="table-info">
              <span class="total-count">共 {{ alarmInfo.length }} 条记录</span>
              <el-button
                  v-if="selectedAlarms.length > 0"
                  @click="clearSelection"
                  type="text"
                  size="small"
              >
                清空选择 ({{ selectedAlarms.length }})
              </el-button>
            </div>
          </div>

          <el-table
              :data="alarmInfo"
              style="width: 100%"
              height="500"
              stripe
              @selection-change="handleSelectionChange"
              class="data-table"
          >
            <el-table-column type="selection" width="50" align="center" />
            <el-table-column prop="index" label="序号" width="80" align="center">
              <template #default="{ $index }">
                <div class="index-badge">{{ $index + 1 }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="cameraName" label="摄像头" width="140" align="center" />
            <el-table-column prop="content" label="报警内容" min-width="180" align="center">
              <template #default="{ row }">
                <div class="alarm-content-text">
                  <el-icon class="content-icon" :class="getAlarmTypeClass(row.type)">
                    <component :is="getAlarmTypeIcon(row.type)" />
                  </el-icon>
                  <span class="content-text">{{ row.content }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="120" align="center">
              <template #default="{ row }">
                <el-tag
                    :type="row.type == 1 ? 'primary' : row.type == 2 ? 'danger' : 'info'"
                    class="type-tag"
                    size="small"
                >
                  <el-icon class="tag-icon">
                    <component :is="getAlarmTypeIcon(row.type)" />
                  </el-icon>
                  {{ row.type == 1 ? '人员进入' : row.type == 2 ? '车辆进入' : row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="level" label="危险级别" width="120" align="center">
              <template #default="{ row }">
                <div :class="['level-badge', getLevelClass(row.level)]">
                  {{ row.level }}
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="createTime" label="报警时间" width="180" align="center">
              <template #default="{ row }">
                <div class="time-cell">
                  <el-icon><Clock /></el-icon>
                  <span>{{ formatTime(row.createTime) }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <div class="action-buttons">
                  <el-button
                      @click="handleProcessAlarm(row.id)"
                      type="primary"
                      size="small"
                      class="process-btn"
                  >
                    <el-icon><Check /></el-icon>
                    处理
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 摄像头警告 -->
      <div v-if="activeTab === 'camera'" class="tab-pane">
        <div class="tab-header">
          <div class="tab-title">
            <h2><el-icon><VideoCamera /></el-icon> 摄像头警告管理</h2>
            <p class="tab-description">监控摄像头设备异常与掉线情况</p>
          </div>
          <div class="tab-actions">
            <el-button @click="refreshCameraAlarmData" :icon="Refresh" circle />
            <el-button @click="handleBatchProcessCamera" type="primary" :icon="Operation">
              批量处理
            </el-button>
          </div>
        </div>

        <div class="filter-card">
          <div class="filter-header">
            <h3><el-icon><Filter /></el-icon> 筛选条件</h3>
            <div class="filter-actions">
              <el-button @click="searchCameraAlarmBtn" type="primary" :icon="Search">
                搜索
              </el-button>
              <el-button @click="clearFilters" :icon="Refresh">
                重置
              </el-button>
            </div>
          </div>

          <div class="filter-form">
            <div class="form-row">
              <div class="form-item">
                <label class="form-label"><el-icon><VideoCamera /></el-icon> 摄像头</label>
                <el-select-v2
                    v-model="searchData.cameraName"
                    filterable
                    :options="cameraOptions"
                    placeholder="请选择摄像头"
                    class="filter-select"
                />
              </div>
              <div class="form-item">
                <label class="form-label"><el-icon><Clock /></el-icon> 时间范围</label>
                <el-select
                    v-model="searchData.day"
                    placeholder="请选择时间"
                    class="filter-select"
                >
                  <el-option
                      v-for="item in dayOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                  />
                </el-select>
              </div>
            </div>
          </div>
        </div>

        <div class="table-card">
          <div class="table-header">
            <h3>摄像头警告列表</h3>
            <div class="table-info">
              <span class="total-count">共 {{ cameraAlarmData.length }} 条记录</span>
              <el-button
                  v-if="selectedCameraAlarms.length > 0"
                  @click="clearCameraSelection"
                  type="text"
                  size="small"
              >
                清空选择 ({{ selectedCameraAlarms.length }})
              </el-button>
            </div>
          </div>

          <el-table
              :data="cameraAlarmData"
              style="width: 100%"
              height="500"
              stripe
              @selection-change="handleCameraSelectionChange"
              class="data-table"
          >
            <el-table-column type="selection" width="50" align="center" />
            <el-table-column prop="index" label="序号" width="80" align="center">
              <template #default="{ $index }">
                <div class="index-badge">{{ $index + 1 }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="cameraName" label="摄像头名称" width="160" align="center" />
            <el-table-column prop="productNumber" label="产品编号" width="140" align="center" />
            <el-table-column label="设备信息" width="200" align="center">
              <template #default="{ row }">
                <div class="device-info">
                  <div class="ip-info">
                    <el-icon><Monitor /></el-icon>
                    <span class="ip-text">{{ row.ip }}</span>
                  </div>
                  <div class="port-info">
                    <el-icon><Connection /></el-icon>
                    <span class="port-text">:{{ row.port }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="警告类型" width="120" align="center">
              <template #default>
                <el-tag type="danger" class="type-tag" size="small">
                  <el-icon><Warning /></el-icon>
                  设备掉线
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createTime" label="发生时间" width="180" align="center">
              <template #default="{ row }">
                <div class="time-cell">
                  <el-icon><Clock /></el-icon>
                  <span>{{ formatTime(row.createTime) }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="设备状态" width="120" align="center">
              <template #default>
                <div class="status-badge offline">
                  <el-icon><CircleCloseFilled /></el-icon>
                  <span>离线</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <div class="action-buttons">
                  <el-button
                      @click="handleProcessCameraAlarm(row.id)"
                      type="primary"
                      size="small"
                      class="process-btn"
                  >
                    <el-icon><Check /></el-icon>
                    处理
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <!-- 加载遮罩 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <p>正在加载数据...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from 'vue'
import {
  Warning,
  VideoCamera,
  Refresh,
  Search,
  Filter,
  Clock,
  Collection,
  Operation,
  Check,
  Monitor,
  Connection,
  CircleCloseFilled,
  WarningFilled,
  VideoCameraFilled,
  BellFilled,
  Loading,
  UserFilled,
  Van
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCurrentInstance } from 'vue'

// API 引入
import {
  getUndisposedCameraAlarm,
  updateCameraAlarmById,
  search
} from '@/http/api/camerAlarm.js'
import { getAllCameras } from '@/http/api/camera'
import {
  getUndisposedAlarmInfo,
  searchAlarmInfo,
  updateAlarmInfoById
} from '@/http/api/alarm.js'

// 获取全局方法
const { appContext } = getCurrentInstance()
const formatDate = appContext.config.globalProperties.$formatDate

// 标签页配置
const tabs = [
  { key: 'danger', label: '危险警告', icon: Warning, badge: 0 },
  { key: 'camera', label: '摄像头警告', icon: VideoCamera, badge: 0 }
]

// 状态管理
const activeTab = ref('danger')
const loading = ref(false)
const selectedAlarms = ref([])
const selectedCameraAlarms = ref([])

// 报警数据
const alarmInfo = reactive([])
const cameraAlarmData = reactive([])
const cameraOptions = reactive([])

// 搜索数据
const searchData = reactive({
  cameraName: '',
  day: '',
  type: '',
})

// 选项配置
const dayOptions = [
  { value: 0, label: '全部时间段' },
  { value: 1, label: '今天' },
  { value: 3, label: '近三天' },
  { value: 7, label: '近七天' },
  { value: 15, label: '近半月' }
]

const typeOptions = [
  { value: 0, label: '全部类型' },
  { value: 1, label: '人员进入' },
  { value: 2, label: '车辆进入' },
]

// 报警统计
const alarmSummary = reactive({
  danger: 0,
  camera: 0,
  total: 0
})

// 计算属性
const formatTime = (time) => {
  if (!time) return '时间未知'
  return formatDate(time, 'YYYY-MM-DD HH:mm:ss')
}

const getAlarmTypeIcon = (type) => {
  return type == 1 ? UserFilled : Van
}

const getAlarmTypeClass = (type) => {
  return type == 1 ? 'person' : 'vehicle'
}

const getLevelClass = (level) => {
  const levelMap = {
    '高': 'high',
    '中': 'medium',
    '低': 'low'
  }
  return levelMap[level] || 'default'
}

// 标签页切换
const switchTab = (tabKey) => {
  activeTab.value = tabKey
  if (tabKey === 'danger') {
    getAllAlarmData()
  } else {
    getAllCameraAlarmData()
  }
}

// 更新统计信息
const updateAlarmSummary = () => {
  alarmSummary.danger = alarmInfo.length
  alarmSummary.camera = cameraAlarmData.length
  alarmSummary.total = alarmInfo.length + cameraAlarmData.length

  // 更新标签页徽章
  tabs[0].badge = alarmInfo.length
  tabs[1].badge = cameraAlarmData.length
}

// 获取摄像头列表
const getCameraList = async () => {
  try {
    const response = await getAllCameras()
    cameraOptions.splice(0, cameraOptions.length, ...response.data.map(camera => ({
      label: camera.name,
      value: camera.name,
    })))
  } catch (error) {
    console.error('获取摄像头列表失败:', error)
    ElMessage.error('摄像头列表加载失败')
  }
}

// ==================== 危险警告相关 ====================
const getAllAlarmData = async () => {
  loading.value = true
  try {
    const response = await getUndisposedAlarmInfo()
    alarmInfo.splice(0, alarmInfo.length, ...response.data.data)
    updateAlarmSummary()
  } catch (error) {
    console.error('获取危险警告失败', error)
    ElMessage.error('危险警告加载失败')
  } finally {
    loading.value = false
  }
}

const searchAlarmInfoBtn = async () => {
  if (!searchData.cameraName && !searchData.day && !searchData.type) {
    ElMessage.warning('请至少选择一个筛选条件')
    return
  }

  loading.value = true
  try {
    const response = await searchAlarmInfo(
        searchData.cameraName,
        searchData.day,
        searchData.type,
        '0'
    )
    alarmInfo.splice(0, alarmInfo.length, ...response.data.data)
    updateAlarmSummary()
    ElMessage.success(`搜索到 ${alarmInfo.length} 条记录`)
  } catch (error) {
    console.error('搜索失败', error)
    ElMessage.error('搜索失败')
  } finally {
    loading.value = false
  }
}

const handleProcessAlarm = async (id) => {
  try {
    await ElMessageBox.confirm(
        '确认处理该危险警告？',
        '处理确认',
        {
          confirmButtonText: '确认处理',
          cancelButtonText: '取消',
          type: 'warning',
          icon: Warning
        }
    )

    loading.value = true
    try {
      const response = await updateAlarmInfoById(id)
      if (response.data.success) {
        ElMessage.success('处理成功')
        await getAllAlarmData()
      } else {
        ElMessage.error('处理失败')
      }
    } catch (error) {
      console.error('处理失败', error)
      ElMessage.error('网络错误，请重试')
    }
  } catch {
    // 用户取消处理
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedAlarms.value = selection.map(item => item.id)
}

const handleBatchProcess = async () => {
  if (selectedAlarms.value.length === 0) {
    ElMessage.warning('请先选择要处理的警告')
    return
  }

  try {
    await ElMessageBox.confirm(
        `确认批量处理 ${selectedAlarms.value.length} 条警告？`,
        '批量处理确认',
        {
          confirmButtonText: '确认处理',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    loading.value = true
    let successCount = 0
    for (const id of selectedAlarms.value) {
      try {
        const response = await updateAlarmInfoById(id)
        if (response.data.success) {
          successCount++
        }
      } catch (error) {
        console.error(`处理警告 ${id} 失败`, error)
      }
    }

    ElMessage.success(`成功处理 ${successCount} 条警告`)
    await getAllAlarmData()
    selectedAlarms.value = []
  } catch {
    // 用户取消
  } finally {
    loading.value = false
  }
}

const clearSelection = () => {
  selectedAlarms.value = []
}

const refreshAlarmData = () => {
  getAllAlarmData()
  ElMessage.success('数据已刷新')
}

// ==================== 摄像头警告相关 ====================
const getAllCameraAlarmData = async () => {
  loading.value = true
  try {
    const response = await getUndisposedCameraAlarm()
    cameraAlarmData.splice(0, cameraAlarmData.length, ...response.data)
    updateAlarmSummary()
  } catch (error) {
    console.error('获取摄像头警告失败', error)
    ElMessage.error('摄像头警告加载失败')
  } finally {
    loading.value = false
  }
}

const searchCameraAlarmBtn = async () => {
  if (!searchData.cameraName && !searchData.day) {
    ElMessage.warning('请至少选择一个筛选条件')
    return
  }

  loading.value = true
  try {
    const response = await search(
        searchData.cameraName,
        searchData.day,
        searchData.type,
        '0'
    )
    cameraAlarmData.splice(0, cameraAlarmData.length, ...response.data.data)
    updateAlarmSummary()
    ElMessage.success(`搜索到 ${cameraAlarmData.length} 条记录`)
  } catch (error) {
    console.error('搜索失败', error)
    ElMessage.error('搜索失败')
  } finally {
    loading.value = false
  }
}

const handleProcessCameraAlarm = async (id) => {
  try {
    await ElMessageBox.confirm(
        '确认处理该摄像头警告？',
        '处理确认',
        {
          confirmButtonText: '确认处理',
          cancelButtonText: '取消',
          type: 'warning',
          icon: VideoCamera
        }
    )

    loading.value = true
    try {
      const response = await updateCameraAlarmById(id)
      if (response.data.success) {
        ElMessage.success('处理成功')
        await getAllCameraAlarmData()
      } else {
        ElMessage.error('处理失败')
      }
    } catch (error) {
      console.error('处理失败', error)
      ElMessage.error('网络错误，请重试')
    }
  } catch {
    // 用户取消处理
  } finally {
    loading.value = false
  }
}

const handleCameraSelectionChange = (selection) => {
  selectedCameraAlarms.value = selection.map(item => item.id)
}

const handleBatchProcessCamera = async () => {
  if (selectedCameraAlarms.value.length === 0) {
    ElMessage.warning('请先选择要处理的警告')
    return
  }

  try {
    await ElMessageBox.confirm(
        `确认批量处理 ${selectedCameraAlarms.value.length} 条摄像头警告？`,
        '批量处理确认',
        {
          confirmButtonText: '确认处理',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    loading.value = true
    let successCount = 0
    for (const id of selectedCameraAlarms.value) {
      try {
        const response = await updateCameraAlarmById(id)
        if (response.data.success) {
          successCount++
        }
      } catch (error) {
        console.error(`处理摄像头警告 ${id} 失败`, error)
      }
    }

    ElMessage.success(`成功处理 ${successCount} 条摄像头警告`)
    await getAllCameraAlarmData()
    selectedCameraAlarms.value = []
  } catch {
    // 用户取消
  } finally {
    loading.value = false
  }
}

const clearCameraSelection = () => {
  selectedCameraAlarms.value = []
}

const refreshCameraAlarmData = () => {
  getAllCameraAlarmData()
  ElMessage.success('数据已刷新')
}

// ==================== 通用方法 ====================
const clearFilters = () => {
  searchData.cameraName = ''
  searchData.day = ''
  searchData.type = ''

  if (activeTab.value === 'danger') {
    getAllAlarmData()
  } else {
    getAllCameraAlarmData()
  }

  ElMessage.info('筛选条件已重置')
}

// 初始化
onMounted(() => {
  getAllAlarmData()
  getCameraList()
})
</script>

<style scoped>
.alarm-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  box-sizing: border-box;
  /* 修复滚动问题 */
  overflow-x: hidden;
  width: 100%;
}

/* 修复右侧空白问题 */
.alarm-content,
.filter-card,
.table-card,
.tab-pane {
  width: 100%;
  box-sizing: border-box;
}

.alarm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  width: 100%;
  box-sizing: border-box;
}

.header-left {
  flex: 1;
  min-width: 0; /* 防止内容溢出 */
}

.alarm-title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.title-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.alarm-subtitle {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-stats {
  display: flex;
  gap: 24px;
  flex-shrink: 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  min-width: 160px;
}

.stat-item .el-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-label {
  font-size: 12px;
  opacity: 0.9;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.alarm-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  background: #ffffff;
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  width: 100%;
  box-sizing: border-box;
  overflow-x: auto;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px 24px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #606266;
  position: relative;
  min-width: 120px;
  flex-shrink: 0;
}

.tab-item:hover {
  background: rgba(64, 158, 255, 0.08);
  color: #409eff;
}

.tab-item.active {
  background: #409eff;
  color: white;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.3);
}

.tab-icon {
  font-size: 20px;
  margin-right: 8px;
  flex-shrink: 0;
}

.tab-label {
  font-size: 16px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tab-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #f56c6c;
  color: white;
  font-size: 12px;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  flex-shrink: 0;
}

.alarm-content {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

.tab-pane {
  padding: 24px;
  width: 100%;
  box-sizing: border-box;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
  width: 100%;
  box-sizing: border-box;
}

.tab-title h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.tab-title h2 .el-icon {
  flex-shrink: 0;
}

.tab-description {
  margin: 0;
  font-size: 14px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tab-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.filter-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid #e4e7ed;
  width: 100%;
  box-sizing: border-box;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  width: 100%;
}

.filter-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.filter-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.filter-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.form-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  width: 100%;
}

.form-item {
  flex: 1;
  min-width: 200px;
  max-width: 100%;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 6px;
  overflow: hidden;
}

.filter-select {
  width: 100%;
  box-sizing: border-box;
}

.table-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #ebeef5;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 16px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #ebeef5;
  width: 100%;
  box-sizing: border-box;
}

.table-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
}

.table-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.total-count {
  font-size: 14px;
  color: #606266;
}

.data-table {
  border-radius: 0 0 12px 12px;
  width: 100% !important;
}

.index-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #f0f9ff;
  color: #409eff;
  border-radius: 50%;
  font-weight: 600;
  font-size: 14px;
  margin: 0 auto;
}

.alarm-content-text {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  width: 100%;
}

.content-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.content-icon.person {
  color: #409eff;
}

.content-icon.vehicle {
  color: #67c23a;
}

.content-text {
  text-align: left;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.type-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.tag-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.level-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.level-badge.high {
  background: #fef0f0;
  color: #f56c6c;
}

.level-badge.medium {
  background: #fdf6ec;
  color: #e6a23c;
}

.level-badge.low {
  background: #f0f9eb;
  color: #67c23a;
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: center;
  color: #606266;
  white-space: nowrap;
}

.device-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
}

.ip-info, .port-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
}

.ip-text, .port-text {
  font-family: 'SF Mono', Monaco, 'Courier New', monospace;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.status-badge.offline {
  background: #fef0f0;
  color: #f56c6c;
}

.action-buttons {
  display: flex;
  justify-content: center;
}

.process-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.loading-content {
  text-align: center;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.loading-icon {
  font-size: 48px;
  color: #409eff;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .header-stats {
    flex-direction: column;
    gap: 12px;
  }

  .stat-item {
    min-width: 180px;
  }
}

@media (max-width: 992px) {
  .alarm-header {
    flex-wrap: wrap;
    gap: 20px;
  }

  .header-left {
    flex-basis: 100%;
    text-align: center;
  }

  .header-stats {
    width: 100%;
    justify-content: center;
    flex-direction: row;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .alarm-container {
    padding: 12px;
  }

  .alarm-header {
    padding: 16px;
    gap: 16px;
  }

  .alarm-tabs {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding: 6px;
  }

  .tab-item {
    flex: 1 0 auto;
    padding: 12px 16px;
  }

  .form-row {
    flex-direction: column;
    gap: 16px;
  }

  .form-item {
    min-width: 100%;
    max-width: 100%;
  }

  .table-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .tab-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .tab-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .filter-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .filter-actions {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (max-width: 480px) {
  .alarm-title {
    font-size: 22px;
  }

  .title-icon {
    font-size: 26px;
  }

  .stat-item {
    min-width: 140px;
    padding: 12px 16px;
  }

  .stat-value {
    font-size: 24px;
  }
}
</style>