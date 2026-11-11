<template>
  <div class="stats-dashboard">
    <!-- 顶部筛选栏 -->
    <div class="stats-header">
      <h1 class="stats-title">数据统计中心</h1>
      <div class="global-filter">
        <el-date-picker
            v-model="globalDateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            :shortcuts="dateShortcuts"
            class="global-date-picker"
        />
        <el-button type="primary" @click="handleGlobalFilter" :icon="Search" round>
          应用筛选
        </el-button>
      </div>
    </div>

    <!-- 标签页导航 -->
    <div class="stats-tabs-nav">
      <div
          v-for="tab in tabs"
          :key="tab.key"
          :class="['tab-item', { active: activeTab === tab.key }]"
          @click="switchTab(tab.key)"
      >
        <el-icon class="tab-icon">
          <component :is="tab.icon"/>
        </el-icon>
        <span class="tab-label">{{ tab.label }}</span>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="stats-content">
      <!-- 设备统计 -->
      <div v-if="activeTab === 'device'" class="tab-content">
        <div class="data-section">
          <div class="section-header">
            <h2>
              <el-icon>
                <Monitor/>
              </el-icon>
              设备运行统计
            </h2>
            <div class="section-actions">
              <el-button @click="fetchDeviceStats" :icon="Refresh" circle/>
              <el-button @click="exportDeviceReport" type="primary" :icon="Download">
                导出报告
              </el-button>
            </div>
          </div>

          <div class="stats-grid">
            <!-- 指标卡片 -->
            <div class="metric-cards">
              <div class="metric-card">
                <div class="metric-value">{{ deviceMetrics.totalDevices }}</div>
                <div class="metric-label">设备总数</div>
              </div>
              <div class="metric-card success">
                <div class="metric-value">{{ deviceMetrics.avgRuntime }}h</div>
                <div class="metric-label">平均运行时间</div>
              </div>
              <div class="metric-card warning">
                <div class="metric-value">{{ deviceMetrics.totalFailures }}</div>
                <div class="metric-label">总故障次数</div>
              </div>
              <div class="metric-card danger">
                <div class="metric-value">{{ deviceMetrics.avgFailureRate }}%</div>
                <div class="metric-label">平均故障率</div>
              </div>
            </div>

            <!-- 图表区域 -->
            <div class="charts-container">
              <div class="chart-card">
                <div class="chart-header">
                  <h3>设备运行时间统计</h3>
                  <el-tag type="info">小时</el-tag>
                </div>
                <div id="deviceRunningChart" class="chart-canvas"></div>
              </div>
              <div class="chart-card">
                <div class="chart-header">
                  <h3>设备故障率统计</h3>
                  <el-tag type="danger">百分比</el-tag>
                </div>
                <div id="deviceFailureChart" class="chart-canvas"></div>
              </div>
            </div>

            <!-- 数据表格 -->
            <div class="table-card">
              <div class="table-header">
                <h3>设备运行详情</h3>
                <el-input
                    v-model="deviceSearch"
                    placeholder="搜索设备..."
                    :prefix-icon="Search"
                    clearable
                    class="search-input"
                />
              </div>
              <el-table
                  :data="filteredDeviceData"
                  height="400"
                  stripe
                  class="data-table"
                  border
              >
                <el-table-column prop="deviceName" label="设备名称" width="180" align="center"/>
                <el-table-column prop="runningTime" label="运行时间(小时)" width="140" align="center"/>
                <el-table-column prop="failureCount" label="故障次数" width="120" align="center"/>
                <el-table-column prop="failureRate" label="故障率" width="120" align="center">
                  <template #default="{ row }">
                    <span :class="['rate-badge', parseFloat(row.failureRate) > 5 ? 'high' : 'low']">
                      {{ row.failureRate }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="当前状态" width="120" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.status === '正常' ? 'success' : 'danger'" size="small">
                      {{ row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </div>
      </div>

      <!-- 报警统计 -->
      <div v-if="activeTab === 'alarm'" class="tab-content">
        <div class="data-section">
          <div class="section-header">
            <h2>
              <el-icon>
                <Warning/>
              </el-icon>
              报警信息统计
            </h2>
            <div class="section-actions">
              <el-button-group>
                <el-button @click="fetchAlarmStats" :icon="Refresh"/>
                <el-button @click="exportAlarmReport" type="primary" :icon="Download">
                  导出报告
                </el-button>
              </el-button-group>
            </div>
          </div>

          <div class="stats-grid">
            <!-- 报警概览 -->
            <div class="overview-cards">
              <div class="overview-card critical">
                <div class="overview-icon">
                  <el-icon>
                    <WarningFilled/>
                  </el-icon>
                </div>
                <div class="overview-content">
                  <div class="overview-value">{{ alarmSummary.total }}</div>
                  <div class="overview-label">报警总数</div>
                </div>
              </div>
              <div class="overview-card warning">
                <div class="overview-icon">
                  <el-icon>
                    <Warning/>
                  </el-icon>
                </div>
                <div class="overview-content">
                  <div class="overview-value">{{ alarmSummary.unhandled }}</div>
                  <div class="overview-label">未处理</div>
                </div>
              </div>
              <div class="overview-card handled">
                <div class="overview-icon">
                  <el-icon>
                    <CircleCheckFilled/>
                  </el-icon>
                </div>
                <div class="overview-content">
                  <div class="overview-value">{{ alarmSummary.handled }}</div>
                  <div class="overview-label">已处理</div>
                </div>
              </div>
            </div>

            <!-- 报警图表 -->
            <div class="charts-container">
              <div class="chart-card full-width">
                <div class="chart-header">
                  <h3>报警类型分布</h3>
                  <el-select v-model="alarmTypeFilter" placeholder="筛选类型" size="small">
                    <el-option label="全部类型" value=""/>
                    <el-option label="设备故障" value="device"/>
                    <el-option label="环境异常" value="environment"/>
                    <el-option label="安全警告" value="security"/>
                  </el-select>
                </div>
                <div id="alarmTypeChart" class="chart-canvas"></div>
              </div>
            </div>

            <!-- 报警趋势 -->
            <div class="chart-card full-width">
              <div class="chart-header">
                <h3>报警趋势 (近7天)</h3>
                <div class="trend-legend">
                  <span class="legend-item danger"><div class="legend-dot"></div> 危险报警</span>
                  <span class="legend-item warning"><div class="legend-dot"></div> 摄像头警告</span>
                </div>
              </div>
              <div id="alarmTrendChart" class="chart-canvas"></div>
            </div>

            <!-- 报警表格 -->
            <div class="table-card">
              <div class="table-header">
                <h3>报警信息详情</h3>
                <el-input
                    v-model="alarmSearch"
                    placeholder="搜索报警..."
                    :prefix-icon="Search"
                    clearable
                    class="search-input"
                />
              </div>
              <el-table :data="filteredAlarmData" height="350" class="data-table" border>
                <el-table-column prop="alarmType" label="报警类型" width="150" align="center"/>
                <el-table-column prop="alarmCount" label="报警次数" width="120" align="center"/>
                <el-table-column prop="handledCount" label="已处理" width="120" align="center"/>
                <el-table-column prop="unhandledCount" label="未处理" width="120" align="center"/>
                <el-table-column prop="handlingRate" label="处理率" width="120" align="center">
                  <template #default="{ row }">
                    <el-progress
                        :percentage="parseFloat(row.handlingRate)"
                        :show-text="false"
                        :color="parseFloat(row.handlingRate) > 90 ? '#67c23a' : parseFloat(row.handlingRate) > 70 ? '#e6a23c' : '#f56c6c'"
                    />
                    <span class="rate-text">{{ row.handlingRate }}%</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </div>
      </div>

      <!-- 任务统计 -->
      <div v-if="activeTab === 'task'" class="tab-content">
        <div class="data-section">
          <div class="section-header">
            <h2>
              <el-icon>
                <List/>
              </el-icon>
              任务完成统计
            </h2>
            <div class="section-actions">
              <el-button @click="fetchTaskStats" :icon="Refresh" circle/>
              <el-button @click="exportTaskReport" type="primary" :icon="Download">
                导出报告
              </el-button>
            </div>
          </div>

          <div class="stats-grid">
            <!-- 任务概览 -->
            <div class="metric-cards">
              <div class="metric-card success">
                <div class="metric-value">{{ taskMetrics.completionRate }}%</div>
                <div class="metric-label">平均完成率</div>
              </div>
              <div class="metric-card warning">
                <div class="metric-value">{{ taskMetrics.avgDuration }}m</div>
                <div class="metric-label">平均耗时</div>
              </div>
              <div class="metric-card info">
                <div class="metric-value">{{ taskMetrics.totalTasks }}</div>
                <div class="metric-label">总任务数</div>
              </div>
              <div class="metric-card">
                <div class="metric-value">{{ taskMetrics.completedTasks }}</div>
                <div class="metric-label">已完成任务</div>
              </div>
            </div>

            <!-- 任务图表 -->
            <div class="charts-container">
              <div class="chart-card">
                <div class="chart-header">
                  <h3>任务完成率</h3>
                  <el-tag :type="taskMetrics.completionRate > 90 ? 'success' : 'warning'">
                    {{ taskMetrics.completionRate > 90 ? '优秀' : '需改进' }}
                  </el-tag>
                </div>
                <div id="taskCompletionChart" class="chart-canvas"></div>
              </div>
              <div class="chart-card">
                <div class="chart-header">
                  <h3>任务耗时统计</h3>
                  <el-tag type="info">分钟</el-tag>
                </div>
                <div id="taskDurationChart" class="chart-canvas"></div>
              </div>
            </div>

            <!-- 任务表格 -->
            <div class="table-card">
              <div class="table-header">
                <h3>任务详情</h3>
                <div class="table-filters">
                  <el-select v-model="taskTypeFilter" placeholder="任务类型" size="small">
                    <el-option label="全部类型" value=""/>
                    <el-option label="巡检任务" value="inspection"/>
                    <el-option label="维修任务" value="maintenance"/>
                    <el-option label="保养任务" value="servicing"/>
                  </el-select>
                </div>
              </div>
              <el-table :data="filteredTaskData" height="350" class="data-table" border>
                <el-table-column prop="taskType" label="任务类型" width="150" align="center"/>
                <el-table-column prop="totalTasks" label="总任务数" width="120" align="center"/>
                <el-table-column prop="completedTasks" label="已完成" width="120" align="center"/>
                <el-table-column prop="completionRate" label="完成率" width="120" align="center">
                  <template #default="{ row }">
                    <span
                        :class="['completion-badge', parseFloat(row.completionRate) >= 90 ? 'high' : parseFloat(row.completionRate) >= 70 ? 'medium' : 'low']">
                      {{ row.completionRate }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="avgDuration" label="平均耗时(分钟)" width="140" align="center"/>
              </el-table>
            </div>
          </div>
        </div>
      </div>

      <!-- 报表导出 -->
      <div v-if="activeTab === 'export'" class="tab-content">
        <div class="export-center">
          <div class="export-header">
            <h2>
              <el-icon>
                <Document/>
              </el-icon>
              报表导出中心
            </h2>
            <p class="export-description">选择统计范围和格式，导出详细分析报告</p>
          </div>

          <div class="export-config">
            <div class="config-section">
              <h3>导出配置</h3>
              <div class="config-form">
                <div class="form-item">
                  <label>日期范围</label>
                  <el-date-picker
                      v-model="exportDateRange"
                      type="datetimerange"
                      range-separator="至"
                      start-placeholder="开始日期"
                      end-placeholder="结束日期"
                      format="YYYY-MM-DD HH:mm:ss"
                      value-format="YYYY-MM-DD HH:mm:ss"
                      :shortcuts="dateShortcuts"
                      class="date-range-picker"
                  />
                </div>
                <div class="form-item">
                  <label>报表类型</label>
                  <el-select v-model="reportType" placeholder="请选择">
                    <el-option
                        v-for="item in reportOptions"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                    />
                  </el-select>
                </div>
                <div class="form-item">
                  <label>导出格式</label>
                  <el-radio-group v-model="exportFormat">
                    <el-radio label="pdf">PDF 文档</el-radio>
                    <el-radio label="excel">Excel 表格</el-radio>
                  </el-radio-group>
                </div>
              </div>
            </div>

            <div class="preview-section">
              <h3>报表预览</h3>
              <div class="preview-content">
                <div class="preview-card">
                  <div class="preview-header">
                    <el-icon>
                      <Document/>
                    </el-icon>
                    <span class="preview-title">{{ getReportTypeLabel(reportType) }}</span>
                  </div>
                  <div class="preview-info">
                    <div class="preview-item">
                      <span class="label">时间范围：</span>
                      <span class="value">{{ exportDateRange[0] }} 至 {{ exportDateRange[1] }}</span>
                    </div>
                    <div class="preview-item">
                      <span class="label">导出格式：</span>
                      <span class="value">{{ exportFormat === 'pdf' ? 'PDF文档' : 'Excel表格' }}</span>
                    </div>
                    <div class="preview-item">
                      <span class="label">包含内容：</span>
                      <span class="value">统计数据、图表分析、详细表格</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="export-actions">
            <el-button
                @click="exportToPDF"
                type="primary"
                size="large"
                :loading="exportLoading"
                class="export-btn"
                v-if="exportFormat === 'pdf'"
            >
              <el-icon>
                <Document/>
              </el-icon>
              导出PDF报告
            </el-button>
            <el-button
                @click="exportToExcel"
                type="success"
                size="large"
                :loading="exportLoading"
                class="export-btn"
                v-if="exportFormat === 'excel'"
            >
              <el-icon>
                <List/>
              </el-icon>
              导出Excel报告
            </el-button>
            <el-button @click="resetExportConfig" size="large">
              重置配置
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载遮罩 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <el-icon class="loading-icon">
          <Loading/>
        </el-icon>
        <p>正在加载数据...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive, computed, onMounted, onUnmounted, nextTick} from 'vue'
import * as echarts from 'echarts'
import {
  Search,
  Refresh,
  Download,
  Monitor,
  Warning,
  List,
  Document,
  Loading,
  WarningFilled,
  CircleCheckFilled
} from '@element-plus/icons-vue'
import {ElMessage} from 'element-plus'
import {
  getDeviceRunningStats,
  getAlarmStats,
  getTaskStats,
  exportStatisticsPDF,
  exportStatisticsExcel
} from '@/http/api/statistics.js'

// 标签页配置
const tabs = [
  {key: 'device', label: '设备统计', icon: Monitor},
  {key: 'alarm', label: '报警分析', icon: Warning},
  {key: 'task', label: '任务管理', icon: List},
  {key: 'export', label: '报表导出', icon: Document}
]

// 全局状态
const activeTab = ref('device')
const globalDateRange = ref([])
const loading = ref(false)

// 日期快捷选项
const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    },
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    },
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    },
  },
]

// ==================== 设备统计 ====================
const deviceSearch = ref('')
const deviceRunningData = ref([])
const deviceMetrics = reactive({
  totalDevices: 0,
  avgRuntime: 0,
  totalFailures: 0,
  avgFailureRate: 0
})

let deviceRunningChart = null
let deviceFailureChart = null

// 计算属性
const filteredDeviceData = computed(() => {
  if (!deviceSearch.value) return deviceRunningData.value
  return deviceRunningData.value.filter(item =>
      item.deviceName.toLowerCase().includes(deviceSearch.value.toLowerCase())
  )
})

// 获取设备运行统计数据
const fetchDeviceStats = async () => {
  console.log('开始获取设备运行统计数据...')

  if (!globalDateRange.value || globalDateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  loading.value = true
  try {
    const [startDate, endDate] = globalDateRange.value
    console.log('查询日期范围:', startDate, '至', endDate)

    const response = await getDeviceRunningStats(startDate, endDate)
    deviceRunningData.value = response.data.deviceRunningData || []
    console.log('获取设备运行数据成功:', deviceRunningData.value)

    // 计算指标
    if (deviceRunningData.value.length > 0) {
      deviceMetrics.totalDevices = deviceRunningData.value.length
      deviceMetrics.avgRuntime = Math.round(
          deviceRunningData.value.reduce((sum, item) => sum + item.runningTime, 0) / deviceRunningData.value.length
      )
      deviceMetrics.totalFailures = deviceRunningData.value.reduce((sum, item) => sum + item.failureCount, 0)
      deviceMetrics.avgFailureRate = parseFloat(
          (deviceRunningData.value.reduce((sum, item) => sum + parseFloat(item.failureRate), 0) / deviceRunningData.value.length).toFixed(2)
      )
    }

    // 渲染图表
    nextTick(() => {
      renderDeviceRunningChart()
      renderDeviceFailureChart()
    })
  } catch (error) {
    console.error('获取设备统计数据失败', error)
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

// 渲染设备运行时间图表
const renderDeviceRunningChart = () => {
  if (deviceRunningChart) {
    deviceRunningChart.dispose()
  }
  deviceRunningChart = echarts.init(document.getElementById('deviceRunningChart'))

  const deviceNames = deviceRunningData.value.map(item => item.deviceName)
  const runningTimes = deviceRunningData.value.map(item => item.runningTime)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: deviceNames,
      axisLabel: {
        interval: 0,
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '运行时间(小时)',
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: '运行时间',
        type: 'bar',
        barWidth: '60%',
        data: runningTimes,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: '#83bff6'},
            {offset: 0.5, color: '#5470c6'},
            {offset: 1, color: '#3b5998'}
          ])
        }
      }
    ]
  }

  deviceRunningChart.setOption(option)
}

// 渲染设备故障率图表
const renderDeviceFailureChart = () => {
  if (deviceFailureChart) {
    deviceFailureChart.dispose()
  }
  deviceFailureChart = echarts.init(document.getElementById('deviceFailureChart'))

  const deviceNames = deviceRunningData.value.map(item => item.deviceName)
  const failureRates = deviceRunningData.value.map(item => parseFloat(item.failureRate))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}%'
    },
    legend: {
      orient: 'horizontal',
      bottom: 'bottom',
      textStyle: {
        color: '#666'
      }
    },
    series: [
      {
        name: '故障率',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: deviceNames.map((name, index) => ({
          name: name,
          value: failureRates[index],
          itemStyle: {
            color: [
              '#5470c6', '#91cc75', '#fac858', '#ee6666',
              '#73c0de', '#3ba272', '#fc8452', '#9a60b4'
            ][index % 8]
          }
        }))
      }
    ]
  }

  deviceFailureChart.setOption(option)
}

const exportDeviceReport = async () => {
  exportLoading.value = true
  try {
    const [startDate, endDate] = globalDateRange.value
    const response = await exportStatisticsPDF(startDate, endDate, '1')
    downloadFile(response.data, `设备运行报告_${startDate}_${endDate}.pdf`)
    ElMessage.success('设备报告导出成功')
  } catch (error) {
    console.error('设备报告导出失败', error)
    ElMessage.error('设备报告导出失败')
  } finally {
    exportLoading.value = false
  }
}

// ==================== 报警统计 ====================
const alarmSearch = ref('')
const alarmTypeFilter = ref('')
const alarmStatsData = ref([])
const alarmSummary = reactive({
  total: 0,
  handled: 0,
  unhandled: 0,
  handlingRate: 0
})

let alarmTypeChart = null
let alarmTrendChart = null

// 计算属性
const filteredAlarmData = computed(() => {
  let data = alarmStatsData.value
  if (alarmSearch.value) {
    data = data.filter(item =>
        item.alarmType.toLowerCase().includes(alarmSearch.value.toLowerCase())
    )
  }
  return data
})

// 获取报警统计数据
const fetchAlarmStats = async () => {
  if (!globalDateRange.value || globalDateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  loading.value = true
  try {
    const [startDate, endDate] = globalDateRange.value

    const response = await getAlarmStats(startDate, endDate)
    alarmStatsData.value = response.data.alarmStatsData || []
    const alarmTrendData = response.data.alarmTrendData || []

    // 计算报警摘要
    if (alarmStatsData.value.length > 0) {
      alarmSummary.total = alarmStatsData.value.reduce((sum, item) => sum + item.alarmCount, 0)
      alarmSummary.handled = alarmStatsData.value.reduce((sum, item) => sum + item.handledCount, 0)
      alarmSummary.unhandled = alarmStatsData.value.reduce((sum, item) => sum + item.unhandledCount, 0)
      alarmSummary.handlingRate = parseFloat(
          (alarmSummary.handled / alarmSummary.total * 100).toFixed(2)
      )
    }

    // 渲染图表
    nextTick(() => {
      renderAlarmTypeChart()
      renderAlarmTrendChart(alarmTrendData)
    })
  } catch (error) {
    console.error('获取报警统计数据失败', error)
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

// 渲染报警类型分布图表
const renderAlarmTypeChart = () => {
  if (alarmTypeChart) {
    alarmTypeChart.dispose()
  }
  alarmTypeChart = echarts.init(document.getElementById('alarmTypeChart'))

  const alarmTypes = alarmStatsData.value.map(item => item.alarmType)
  const alarmCounts = alarmStatsData.value.map(item => item.alarmCount)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: {
        color: '#666'
      }
    },
    series: [
      {
        name: '报警类型',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          position: 'outside',
          formatter: '{b}\n{c}次',
          fontSize: 14,
          fontWeight: 'bold'
        },
        data: alarmTypes.map((type, index) => ({
          name: type,
          value: alarmCounts[index],
          itemStyle: {
            color: [
              '#ee6666', '#fac858', '#91cc75', '#73c0de'
            ][index % 4]
          }
        }))
      }
    ]
  }

  alarmTypeChart.setOption(option)
}

// 渲染报警趋势图表
const renderAlarmTrendChart = (trendData) => {
  if (alarmTrendChart) {
    alarmTrendChart.dispose()
  }
  alarmTrendChart = echarts.init(document.getElementById('alarmTrendChart'))

  const dates = trendData.map(item => item.date)
  const dangerAlarms = trendData.map(item => item.dangerAlarmCount)
  const cameraAlarms = trendData.map(item => item.cameraAlarmCount)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: ['危险报警', '摄像头警告'],
      textStyle: {
        color: '#666'
      },
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: dates,
        axisLine: {
          lineStyle: {
            color: '#999'
          }
        },
        axisLabel: {
          rotate: 45
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '报警次数',
        nameTextStyle: {
          color: '#666'
        },
        splitLine: {
          lineStyle: {
            type: 'dashed',
            color: '#DDD'
          }
        }
      }
    ],
    series: [
      {
        name: '危险报警',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#ee6666'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: 'rgba(255, 99, 97, 0.8)'},
            {offset: 1, color: 'rgba(255, 99, 97, 0.1)'}
          ])
        },
        data: dangerAlarms
      },
      {
        name: '摄像头警告',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#73c0de'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: 'rgba(115, 192, 222, 0.8)'},
            {offset: 1, color: 'rgba(115, 192, 222, 0.1)'}
          ])
        },
        data: cameraAlarms
      }
    ]
  }

  alarmTrendChart.setOption(option)
}

const exportAlarmReport = async () => {
  exportLoading.value = true
  try {
    const [startDate, endDate] = globalDateRange.value
    const response = await exportStatisticsPDF(startDate, endDate, '2')
    downloadFile(response.data, `报警信息报告_${startDate}_${endDate}.pdf`)
    ElMessage.success('报警报告导出成功')
  } catch (error) {
    console.error('报警报告导出失败', error)
    ElMessage.error('报警报告导出失败')
  } finally {
    exportLoading.value = false
  }
}

// ==================== 任务统计 ====================
const taskTypeFilter = ref('')
const taskStatsData = ref([])
const taskMetrics = reactive({
  totalTasks: 0,
  completedTasks: 0,
  completionRate: 0,
  avgDuration: 0
})

let taskCompletionChart = null
let taskDurationChart = null

// 计算属性
const filteredTaskData = computed(() => {
  let data = taskStatsData.value
  if (taskTypeFilter.value) {
    data = data.filter(item => item.taskType === taskTypeFilter.value)
  }
  return data
})

// 获取任务统计数据
const fetchTaskStats = async () => {
  if (!globalDateRange.value || globalDateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  loading.value = true
  try {
    const [startDate, endDate] = globalDateRange.value

    const response = await getTaskStats(startDate, endDate)
    taskStatsData.value = response.data.taskStatsData || []

    // 计算任务指标
    if (taskStatsData.value.length > 0) {
      taskMetrics.totalTasks = taskStatsData.value.reduce((sum, item) => sum + item.totalTasks, 0)
      taskMetrics.completedTasks = taskStatsData.value.reduce((sum, item) => sum + item.completedTasks, 0)
      taskMetrics.completionRate = parseFloat(
          (taskMetrics.completedTasks / taskMetrics.totalTasks * 100).toFixed(2)
      )
      taskMetrics.avgDuration = parseFloat(
          (taskStatsData.value.reduce((sum, item) => sum + parseFloat(item.avgDuration), 0) / taskStatsData.value.length).toFixed(2)
      )
    }

    // 渲染图表
    nextTick(() => {
      renderTaskCompletionChart()
      renderTaskDurationChart()
    })
  } catch (error) {
    console.error('获取任务统计数据失败', error)
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

// 渲染任务完成率图表
const renderTaskCompletionChart = () => {
  if (taskCompletionChart) {
    taskCompletionChart.dispose()
  }
  taskCompletionChart = echarts.init(document.getElementById('taskCompletionChart'))

  const taskTypes = taskStatsData.value.map(item => item.taskType)
  const completionRates = taskStatsData.value.map(item => parseFloat(item.completionRate))

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#DDD'
        }
      }
    },
    yAxis: {
      type: 'category',
      data: taskTypes,
      axisLine: {
        lineStyle: {
          color: '#999'
        }
      },
      axisLabel: {
        color: '#666'
      }
    },
    series: [
      {
        name: '完成率',
        type: 'bar',
        data: completionRates.map((rate, index) => ({
          value: rate,
          itemStyle: {
            color: rate >= 90 ? '#67c23a' : rate >= 70 ? '#e6a23c' : '#f56c6c'
          }
        })),
        label: {
          show: true,
          position: 'right',
          formatter: '{c}%',
          fontSize: 14,
          fontWeight: 'bold'
        }
      }
    ]
  }

  taskCompletionChart.setOption(option)
}

// 渲染任务耗时图表
const renderTaskDurationChart = () => {
  if (taskDurationChart) {
    taskDurationChart.dispose()
  }
  taskDurationChart = echarts.init(document.getElementById('taskDurationChart'))

  const taskTypes = taskStatsData.value.map(item => item.taskType)
  const avgDurations = taskStatsData.value.map(item => parseFloat(item.avgDuration))

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c} 分钟'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: taskTypes,
      axisLine: {
        lineStyle: {
          color: '#999'
        }
      },
      axisLabel: {
        color: '#666'
      }
    },
    yAxis: {
      type: 'value',
      name: '平均耗时(分钟)',
      nameTextStyle: {
        color: '#666'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#DDD'
        }
      }
    },
    series: [
      {
        name: '平均耗时',
        type: 'line',
        data: avgDurations,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#73c0de'
        },
        lineStyle: {
          width: 3
        },
        areaStyle: {
          opacity: 0.3,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: 'rgba(115, 192, 222, 0.5)'},
            {offset: 1, color: 'rgba(115, 192, 222, 0.1)'}
          ])
        }
      }
    ]
  }

  taskDurationChart.setOption(option)
}

const exportTaskReport = async () => {
  exportLoading.value = true
  try {
    const [startDate, endDate] = globalDateRange.value
    const response = await exportStatisticsPDF(startDate, endDate, '3')
    downloadFile(response.data, `任务完成报告_${startDate}_${endDate}.pdf`)
    ElMessage.success('任务报告导出成功')
  } catch (error) {
    console.error('任务报告导出失败', error)
    ElMessage.error('任务报告导出失败')
  } finally {
    exportLoading.value = false
  }
}

// ==================== 报表导出 ====================
const exportDateRange = ref([])
const reportType = ref('1')
const exportFormat = ref('pdf')
const exportLoading = ref(false)
const reportOptions = [
  {value: '1', label: '设备运行报表'},
  {value: '2', label: '报警信息报表'},
  {value: '3', label: '任务完成报表'},
  {value: '4', label: '综合统计报表'},
]

const getReportTypeLabel = (value) => {
  const option = reportOptions.find(item => item.value === value)
  return option ? option.label : '未知报表类型'
}

// 导出PDF
const exportToPDF = async () => {
  if (!exportDateRange.value || exportDateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  if (!reportType.value) {
    ElMessage.warning('请选择报表类型')
    return
  }

  try {
    exportLoading.value = true
    const [startDate, endDate] = exportDateRange.value

    const response = await exportStatisticsPDF(startDate, endDate, reportType.value)

    // 处理二进制数据并下载
    const blob = new Blob([response.data], {type: 'application/pdf'})
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `统计报表_${startDate}_${endDate}.pdf`
    link.click()
    URL.revokeObjectURL(link.href)

    ElMessage.success('PDF导出成功')
  } catch (error) {
    console.error('PDF导出失败', error)
    ElMessage.error('PDF导出失败')
  } finally {
    exportLoading.value = false
  }
}

// 导出Excel
const exportToExcel = async () => {
  if (!exportDateRange.value || exportDateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  if (!reportType.value) {
    ElMessage.warning('请选择报表类型')
    return
  }

  try {
    exportLoading.value = true
    const [startDate, endDate] = exportDateRange.value

    const response = await exportStatisticsExcel(startDate, endDate, reportType.value)

    // 处理二进制数据并下载
    const blob = new Blob([response.data], {type: 'application/vnd.ms-excel'})
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `统计报表_${startDate}_${endDate}.xlsx`
    link.click()
    URL.revokeObjectURL(link.href)

    ElMessage.success('Excel导出成功')
  } catch (error) {
    console.error('Excel导出失败', error)
    ElMessage.error('Excel导出失败')
  } finally {
    exportLoading.value = false
  }
}

// 重置导出配置
const resetExportConfig = () => {
  exportDateRange.value = []
  reportType.value = '1'
  exportFormat.value = 'pdf'
}

// ==================== 通用方法 ====================
const switchTab = (tabKey) => {
  activeTab.value = tabKey
  if (tabKey !== 'export') {
    loadTabData(tabKey)
  }
}

const handleGlobalFilter = () => {
  loadTabData(activeTab.value)
}

const loadTabData = async (tabKey) => {
  switch (tabKey) {
    case 'device':
      await fetchDeviceStats()
      break
    case 'alarm':
      await fetchAlarmStats()
      break
    case 'task':
      await fetchTaskStats()
      break
  }
}

const downloadFile = (blobData, filename) => {
  const blob = new Blob([blobData])
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
  URL.revokeObjectURL(link.href)
}

// 初始化
onMounted(() => {
  // 设置默认日期范围（最近7天）
  const end = new Date()
  const start = new Date()
  start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)

  // 格式化日期
  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    const seconds = date.getSeconds().toString().padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }

  globalDateRange.value = [formatDate(start), formatDate(end)]
  exportDateRange.value = [formatDate(start), formatDate(end)]

  // 加载初始数据
  fetchDeviceStats()
})

onUnmounted(() => {
  // 清理图表实例
  const charts = [
    deviceRunningChart, deviceFailureChart,
    alarmTypeChart, alarmTrendChart,
    taskCompletionChart, taskDurationChart
  ]
  charts.forEach(chart => chart && chart.dispose())
})

// 响应窗口大小变化
window.addEventListener('resize', () => {
  const charts = [
    deviceRunningChart, deviceFailureChart,
    alarmTypeChart, alarmTrendChart,
    taskCompletionChart, taskDurationChart
  ]
  charts.filter(chart => chart).forEach(chart => chart.resize())
})
</script>

<style scoped>
.stats-dashboard {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stats-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
}

.global-filter {
  display: flex;
  gap: 12px;
  align-items: center;
}

.global-date-picker {
  width: 400px;
}

.stats-tabs-nav {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  background: #ffffff;
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #606266;
}

.tab-item:hover {
  background: rgba(64, 158, 255, 0.05);
  color: #409eff;
}

.tab-item.active {
  background: #409eff;
  color: white;
  box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.3);
}

.tab-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.tab-label {
  font-size: 14px;
  font-weight: 500;
}

.stats-content {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.tab-content {
  padding: 24px;
}

.data-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.stats-grid {
  display: grid;
  gap: 24px;
}

.metric-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.metric-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-left: 4px solid #409eff;
  transition: transform 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.metric-card.success {
  border-left-color: #67c23a;
}

.metric-card.warning {
  border-left-color: #e6a23c;
}

.metric-card.danger {
  border-left-color: #f56c6c;
}

.metric-card.info {
  border-left-color: #909399;
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 14px;
  color: #606266;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.overview-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 8px;
  color: white;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.overview-card.critical {
  background: linear-gradient(135deg, #ff6b6b, #ff4757);
}

.overview-card.warning {
  background: linear-gradient(135deg, #ffa502, #ff7f00);
}

.overview-card.handled {
  background: linear-gradient(135deg, #2ed573, #1dd1a1);
}

.overview-icon {
  font-size: 32px;
  opacity: 0.9;
}

.overview-value {
  font-size: 28px;
  font-weight: 700;
}

.overview-label {
  font-size: 14px;
  opacity: 0.9;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.chart-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart-canvas {
  height: 300px;
  width: 100%;
}

.table-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.search-input {
  width: 200px;
}

.data-table {
  border-radius: 4px;
  overflow: hidden;
}

.rate-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.rate-badge.high {
  background: #fff2f0;
  color: #f56c6c;
}

.rate-badge.low {
  background: #f6ffed;
  color: #67c23a;
}

.completion-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.completion-badge.high {
  background: #f6ffed;
  color: #67c23a;
}

.completion-badge.medium {
  background: #fdf6ec;
  color: #e6a23c;
}

.completion-badge.low {
  background: #fff2f0;
  color: #f56c6c;
}

.rate-text {
  margin-left: 8px;
  font-size: 12px;
  color: #606266;
}

.export-center {
  max-width: 1200px;
  margin: 0 auto;
}

.export-header {
  text-align: center;
  margin-bottom: 40px;
}

.export-description {
  color: #606266;
  margin-top: 8px;
}

.export-config {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 40px;
}

.config-section,
.preview-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item label {
  font-weight: 500;
  color: #303133;
}

.date-range-picker {
  width: 100%;
}

.preview-content {
  height: 300px;
}

.preview-card {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.preview-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.preview-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-item {
  display: flex;
}

.preview-item .label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.preview-item .value {
  color: #303133;
  flex: 1;
}

.export-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding-top: 30px;
  border-top: 1px solid #ebeef5;
}

.export-btn {
  padding: 12px 32px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.loading-content {
  text-align: center;
}

.loading-icon {
  font-size: 48px;
  color: #409eff;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.trend-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #606266;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-item.danger .legend-dot {
  background: #f56c6c;
}

.legend-item.warning .legend-dot {
  background: #e6a23c;
}

@media (max-width: 768px) {
  .stats-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .global-filter {
    flex-direction: column;
  }

  .global-date-picker {
    width: 100%;
  }

  .stats-tabs-nav {
    flex-wrap: wrap;
  }

  .tab-item {
    flex: 1 0 calc(50% - 8px);
  }

  .export-config {
    grid-template-columns: 1fr;
  }

  .charts-container {
    grid-template-columns: 1fr;
  }

  .metric-cards,
  .overview-cards {
    grid-template-columns: 1fr;
  }
}
</style>