<template>
  <div class="data-statistics">
    <header class="ops-page-header"><div><span class="ops-eyebrow">OPERATIONS ANALYTICS / 数据分析</span><h1>数据统计</h1><p>按设备、告警和任务查看统计结果与报表。</p></div></header>
    <el-tabs v-model="activeTab" type="border-card" class="stats-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="设备运行统计" name="device">
        <div class="filter-section">
          <div class="date-filter">
            <span class="filter-label">日期范围：</span>
            <el-date-picker
                v-model="dateRange"
                type="datetimerange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                :shortcuts="dateShortcuts"
            />
          </div>
          <el-button type="primary" @click="fetchDeviceStats" round>查询</el-button>
          <el-button @click="resetDeviceFilters" round>重置</el-button>
        </div>

        <!-- 图表区域 -->
        <div class="chart-container">
          <div class="chart-wrapper">
            <h3>设备运行时间统计</h3>
            <div id="deviceRunningChart" class="chart"></div>
          </div>
          <div class="chart-wrapper">
            <h3>设备故障率统计</h3>
            <div id="deviceFailureChart" class="chart"></div>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="table-container">
          <h3>设备运行详情</h3>
          <el-table :data="deviceRunningData" style="width: 100%" border>
            <el-table-column prop="deviceName" label="设备名称" min-width="15%" align="center"/>
            <el-table-column prop="runningTime" label="运行时间(小时)" min-width="15%" align="center"/>
            <el-table-column prop="failureCount" label="故障次数" min-width="15%" align="center"/>
            <el-table-column prop="failureRate" label="故障率" min-width="15%" align="center"/>
            <el-table-column prop="status" label="当前状态" min-width="15%" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === '正常' ? 'success' : 'danger'">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="报警信息统计" name="alarm">
        <div class="filter-section">
          <div class="date-filter">
            <span class="filter-label">日期范围：</span>
            <el-date-picker
                v-model="alarmDateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                :shortcuts="dateShortcuts"
            />
          </div>
          <el-button type="primary" @click="fetchAlarmStats" round>查询</el-button>
          <el-button @click="resetAlarmFilters" round>重置</el-button>
        </div>

        <!-- 图表区域 -->
        <div class="chart-container">
          <div class="chart-wrapper">
            <h3>报警类型分布</h3>
            <div id="alarmTypeChart" class="chart"></div>
          </div>
          <div class="chart-wrapper">
            <h3>报警趋势(近7天)</h3>
            <div id="alarmTrendChart" class="chart"></div>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="table-container">
          <h3>报警信息详情</h3>
          <el-table :data="alarmStatsData" style="width: 100%" border>
            <el-table-column prop="alarmType" label="报警类型" min-width="15%" align="center"/>
            <el-table-column prop="alarmCount" label="报警次数" min-width="15%" align="center"/>
            <el-table-column prop="handledCount" label="已处理" min-width="15%" align="center"/>
            <el-table-column prop="unhandledCount" label="未处理" min-width="15%" align="center"/>
            <el-table-column prop="handlingRate" label="处理率" min-width="15%" align="center"/>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="任务完成统计" name="task">
        <!-- 任务完成情况统计内容 -->
        <div class="filter-section">
          <div class="date-filter">
            <span class="filter-label">日期范围：</span>
            <el-date-picker
                v-model="taskDateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                :shortcuts="dateShortcuts"
            />
          </div>
          <el-button type="primary" @click="fetchTaskStats" round>查询</el-button>
          <el-button @click="resetTaskFilters" round>重置</el-button>
        </div>

        <!-- 图表区域 -->
        <div class="chart-container">
          <div class="chart-wrapper">
            <h3>任务完成率</h3>
            <div id="taskCompletionChart" class="chart"></div>
          </div>
          <div class="chart-wrapper">
            <h3>任务耗时统计</h3>
            <div id="taskDurationChart" class="chart"></div>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="table-container">
          <h3>任务详情</h3>
          <el-table :data="taskStatsData" style="width: 100%" border>
            <el-table-column prop="taskType" label="任务类型" min-width="15%" align="center"/>
            <el-table-column prop="totalTasks" label="总任务数" min-width="15%" align="center"/>
            <el-table-column prop="completedTasks" label="已完成" min-width="15%" align="center"/>
            <el-table-column prop="completionRate" label="完成率" min-width="15%" align="center"/>
            <el-table-column prop="avgDuration" label="平均耗时(分钟)" min-width="15%" align="center"/>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="报表导出">
        <div class="export-section">
          <div class="filter-section">
            <div class="date-filter">
              <span class="filter-label">日期范围：</span>
              <el-date-picker
                  v-model="exportDateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  format="YYYY-MM-DD HH:mm:ss"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  :shortcuts="dateShortcuts"
              />
            </div>
            <div class="report-filter">
              <span class="filter-label">报表类型：</span>
              <el-select v-model="reportType" placeholder="请选择报表类型">
                <el-option
                    v-for="item in reportOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                />
              </el-select>
            </div>
          </div>

          <div class="export-buttons">
            <el-button type="primary" @click="exportToPDF" :loading="exportLoading">
              <el-icon>
                <Document/>
              </el-icon>
              导出PDF
            </el-button>
            <el-button type="success" @click="exportToExcel" :loading="exportLoading">
              <el-icon>
                <List/>
              </el-icon>
              导出Excel
            </el-button>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import {ref, reactive, onMounted, onUnmounted, nextTick} from 'vue'
import {Document, List} from '@element-plus/icons-vue'
import {ElMessage} from 'element-plus'
import * as echarts from 'echarts'
import '@/utils/railChartTheme'
import {
  getDeviceRunningStats,
  getAlarmStats,
  getTaskStats,
  exportStatisticsPDF,
  exportStatisticsExcel
} from '@/http/api/statistics.js'

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

// ==================== 设备运行统计 ====================
const dateRange = ref([])
const deviceRunningData = ref([])
let deviceRunningChart = null
let deviceFailureChart = null
let statisticsMounted = false
let resizeFrame = null

const resizeCharts = () => {
  if (!statisticsMounted || resizeFrame !== null) return

  resizeFrame = window.requestAnimationFrame(() => {
    resizeFrame = null
    [
      deviceRunningChart,
      deviceFailureChart,
      alarmTypeChart,
      alarmTrendChart,
      taskCompletionChart,
      taskDurationChart
    ].forEach((chart) => {
      if (!chart || chart.isDisposed()) return
      const container = chart.getDom()
      if (container?.clientWidth > 0 && container?.clientHeight > 0) chart.resize()
    })
  })
}

// 获取设备运行统计数据
const fetchDeviceStats = async () => {
  console.log('开始获取设备运行统计数据...')
  console.log('当前日期范围:', dateRange.value)

  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  try {
    const [startDate, endDate] = dateRange.value

    const response = await getDeviceRunningStats(startDate, endDate)
    if (!statisticsMounted) return
    deviceRunningData.value = response.data.deviceRunningData || []

    console.log('获取设备运行数据成功:', deviceRunningData.value)

    // 确保DOM已加载完成
    nextTick(() => {
      if (!statisticsMounted) return
      console.log('nextTick: 开始渲染图表...')
      // 更新图表
      renderDeviceRunningChart(deviceRunningData.value)
      renderDeviceFailureChart(deviceRunningData.value)
    })
  } catch (error) {
    console.error('获取设备统计数据失败', error)
    ElMessage.error('获取统计数据失败')
  }
}

// 渲染设备运行时间图表
const renderDeviceRunningChart = (data) => {
  const container = document.getElementById('deviceRunningChart')
  if (!container) return
  deviceRunningChart = echarts.getInstanceByDom(container) || echarts.init(container, 'rail-workspace')

  const deviceNames = data.map(item => item.deviceName)
  const runningTimes = data.map(item => item.runningTime)

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
      type: 'category',
      data: deviceNames,
      axisLabel: {
        interval: 0,
        rotate: 30
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
            {offset: 0, color: '#b3d4d9'},
            {offset: 0.5, color: '#75a6b1'},
            {offset: 1, color: '#426672'}
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {offset: 0, color: '#75a6b1'},
              {offset: 0.7, color: '#426672'},
              {offset: 1, color: '#304b57'}
            ])
          }
        }
      }
    ]
  }

  deviceRunningChart.setOption(option)
}

// 渲染设备故障率图表
const renderDeviceFailureChart = (data) => {
  const container = document.getElementById('deviceFailureChart')
  if (!container) return
  deviceFailureChart = echarts.getInstanceByDom(container) || echarts.init(container, 'rail-workspace')

  const deviceNames = data.map(item => item.deviceName)
  const failureRates = data.map(item => parseFloat(item.failureRate))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}%'
    },
    legend: {
      orient: 'horizontal',
      bottom: 'bottom',
      textStyle: {
        color: '#acbbc2'
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
              '#75a6b1', '#91cc75', '#fac858', '#ee6666',
              '#73c0de', '#3ba272', '#fc8452', '#9a60b4'
            ][index % 8]
          }
        }))
      }
    ]
  }

  deviceFailureChart.setOption(option)
}

// 重置设备筛选条件
const resetDeviceFilters = () => {
  dateRange.value = []
}

// ==================== 报警信息统计 ====================
const alarmDateRange = ref([])
const alarmStatsData = ref([])
let alarmTypeChart = null
let alarmTrendChart = null

// 获取报警统计数据
const fetchAlarmStats = async () => {
  if (!alarmDateRange.value || alarmDateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  try {
    const [startDate, endDate] = alarmDateRange.value

    // 获取报警统计信息
    const response = await getAlarmStats(startDate, endDate)
    if (!statisticsMounted) return
    alarmStatsData.value = response.data.alarmStatsData || []
    const alarmTrendData = response.data.alarmTrendData || []

    // 更新图表
    renderAlarmTypeChart(alarmStatsData.value)
    renderAlarmTrendChart(alarmTrendData)
  } catch (error) {
    console.error('获取报警统计数据失败', error)
    ElMessage.error('获取统计数据失败')
  }
}

// 渲染报警类型分布图表
const renderAlarmTypeChart = (data) => {
  const container = document.getElementById('alarmTypeChart')
  if (!container) return
  alarmTypeChart = echarts.getInstanceByDom(container) || echarts.init(container, 'rail-workspace')

  const alarmTypes = data.map(item => item.alarmType)
  const alarmCounts = data.map(item => item.alarmCount)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: {
        color: '#acbbc2'
      }
    },
    series: [
      {
        name: '报警类型',
        type: 'pie',
        radius: ['40%', '70%'],  // 改为环形图
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
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
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
const renderAlarmTrendChart = (data) => {
  const container = document.getElementById('alarmTrendChart')
  if (!container) return
  alarmTrendChart = echarts.getInstanceByDom(container) || echarts.init(container, 'rail-workspace')

  const dates = data.map(item => item.date)
  const dangerAlarms = data.map(item => item.dangerAlarmCount)
  const cameraAlarms = data.map(item => item.cameraAlarmCount)

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
        color: '#acbbc2'
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
            color: '#acbbc2'
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
          color: '#acbbc2'
        },
        splitLine: {
          lineStyle: {
            type: 'dashed',
            color: '#3b4c54'
          }
        },
        axisLine: {
          lineStyle: {
            color: '#acbbc2'
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
        sampling: 'average',
        itemStyle: {
          color: '#ee6666'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: 'rgba(255, 99, 97, 0.8)'},
            {offset: 1, color: 'rgba(255, 99, 97, 0.1)'}
          ])
        },
        data: dangerAlarms,
        markPoint: {
          data: [
            {type: 'max', name: '最大值'},
            {type: 'min', name: '最小值'}
          ]
        },
        markLine: {
          data: [
            {type: 'average', name: '平均值'}
          ]
        }
      },
      {
        name: '摄像头警告',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        sampling: 'average',
        itemStyle: {
          color: '#73c0de'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: 'rgba(115, 192, 222, 0.8)'},
            {offset: 1, color: 'rgba(115, 192, 222, 0.1)'}
          ])
        },
        data: cameraAlarms,
        markPoint: {
          data: [
            {type: 'max', name: '最大值'},
            {type: 'min', name: '最小值'}
          ]
        },
        markLine: {
          data: [
            {type: 'average', name: '平均值'}
          ]
        }
      }
    ]
  }

  alarmTrendChart.setOption(option)
}

// 重置报警筛选条件
const resetAlarmFilters = () => {
  alarmDateRange.value = []
}

// ==================== 任务完成统计 ====================
const taskDateRange = ref([])
const taskStatsData = ref([])
let taskCompletionChart = null
let taskDurationChart = null

// 获取任务统计数据
const fetchTaskStats = async () => {
  if (!taskDateRange.value || taskDateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  try {
    const [startDate, endDate] = taskDateRange.value

    // 获取任务完成情况
    const response = await getTaskStats(startDate, endDate)
    if (!statisticsMounted) return
    taskStatsData.value = response.data.taskStatsData || []

    // 更新图表
    renderTaskCompletionChart(taskStatsData.value)
    renderTaskDurationChart(taskStatsData.value)
  } catch (error) {
    console.error('获取任务统计数据失败', error)
    ElMessage.error('获取统计数据失败')
  }
}

// 渲染任务完成率图表
const renderTaskCompletionChart = (data) => {
  const container = document.getElementById('taskCompletionChart')
  if (!container) return
  taskCompletionChart = echarts.getInstanceByDom(container) || echarts.init(container, 'rail-workspace')

  const taskTypes = data.map(item => item.taskType)
  const completionRates = data.map(item => parseFloat(item.completionRate))

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
          color: '#3b4c54'
        }
      }
    },
    yAxis: {
      type: 'category',
      data: taskTypes,
      axisLine: {
        lineStyle: {
          color: '#acbbc2'
        }
      },
      axisLabel: {
        color: '#acbbc2'
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
        },
        showBackground: true,
        backgroundStyle: {
          color: 'rgba(180, 180, 180, 0.1)'
        }
      }
    ]
  }

  taskCompletionChart.setOption(option)
}

// 渲染任务耗时图表
const renderTaskDurationChart = (data) => {
  const container = document.getElementById('taskDurationChart')
  if (!container) return
  taskDurationChart = echarts.getInstanceByDom(container) || echarts.init(container, 'rail-workspace')

  const taskTypes = data.map(item => item.taskType)
  const avgDurations = data.map(item => parseFloat(item.avgDuration))

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
          color: '#acbbc2'
        }
      },
      axisLabel: {
        color: '#acbbc2'
      }
    },
    yAxis: {
      type: 'value',
      name: '平均耗时(分钟)',
      nameTextStyle: {
        color: '#acbbc2'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#3b4c54'
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
          width: 3,
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              {offset: 0, color: '#73c0de'},
              {offset: 1, color: '#75a6b1'}
            ]
          }
        },
        areaStyle: {
          opacity: 0.3,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: 'rgba(115, 192, 222, 0.5)'},
            {offset: 1, color: 'rgba(115, 192, 222, 0.1)'}
          ])
        },
        markPoint: {
          data: [
            {type: 'max', name: '最大值'},
            {type: 'min', name: '最小值'}
          ],
          itemStyle: {
            color: '#75a6b1'
          }
        },
        markLine: {
          data: [
            {type: 'average', name: '平均值'}
          ],
          lineStyle: {
            color: '#75a6b1',
            type: 'dashed'
          }
        }
      }
    ]
  }

  taskDurationChart.setOption(option)
}

// 重置任务筛选条件
const resetTaskFilters = () => {
  taskDateRange.value = []
}

// ==================== 报表导出 ====================
const exportDateRange = ref([])
const reportType = ref('')
const exportLoading = ref(false)
const reportOptions = [
  {value: '1', label: '设备运行报表'},
  {value: '2', label: '报警信息报表'},
  {value: '3', label: '任务完成报表'},
  {value: '4', label: '综合统计报表'},
]

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

// 当前激活的tab
const activeTab = ref('device')

// 处理tab切换事件
const handleTabChange = (tabName) => {
  activeTab.value = tabName
  disposeAllCharts();
  nextTick(() => {
    if (activeTab.value === 'device') {
      fetchDeviceStats();
    } else if (activeTab.value === 'alarm') {
      fetchAlarmStats();
    } else if (activeTab.value === 'task') {
      fetchTaskStats();
    }
  });
}

// 初始化设备运行图表
const initDeviceCharts = () => {
  console.log('初始化设备运行图表...')
  console.log('deviceRunningChart容器存在:', !!document.getElementById('deviceRunningChart'))
  console.log('deviceFailureChart容器存在:', !!document.getElementById('deviceFailureChart'))

  // 不要在这里创建图表实例，改为在渲染函数中处理
}

// 初始化报警信息图表
const initAlarmCharts = () => {
  if (!alarmTypeChart || alarmTypeChart.isDisposed()) {
    alarmTypeChart = echarts.init(document.getElementById('alarmTypeChart'), 'rail-workspace')
  }
  if (!alarmTrendChart || alarmTrendChart.isDisposed()) {
    alarmTrendChart = echarts.init(document.getElementById('alarmTrendChart'), 'rail-workspace')
  }
}

// 初始化任务完成图表
const initTaskCharts = () => {
  if (!taskCompletionChart || taskCompletionChart.isDisposed()) {
    taskCompletionChart = echarts.init(document.getElementById('taskCompletionChart'), 'rail-workspace')
  }
  if (!taskDurationChart || taskDurationChart.isDisposed()) {
    taskDurationChart = echarts.init(document.getElementById('taskDurationChart'), 'rail-workspace')
  }
}

// 页面加载时初始化
onMounted(() => {
  statisticsMounted = true
  console.log('页面挂载完成...')

  window.addEventListener('resize', resizeCharts)

  // 初始化一些默认数据，如最近7天
  const end = new Date()
  const start = new Date()
  start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)

  // 格式化日期为字符串：YYYY-MM-DD HH:mm:ss
  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    const seconds = date.getSeconds().toString().padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }

  // 设置默认日期范围
  dateRange.value = [formatDate(start), formatDate(end)]
  alarmDateRange.value = [formatDate(start), formatDate(end)]
  taskDateRange.value = [formatDate(start), formatDate(end)]

  // 初始化默认数据
  console.log('准备初始化默认图表...')
  fetchDeviceStats()
})

const disposeAllCharts = () => {
  if (deviceRunningChart) {
    deviceRunningChart.dispose();
    deviceRunningChart = null;
  }
  if (deviceFailureChart) {
    deviceFailureChart.dispose();
    deviceFailureChart = null;
  }
  if (alarmTypeChart) {
    alarmTypeChart.dispose();
    alarmTypeChart = null;
  }
  if (alarmTrendChart) {
    alarmTrendChart.dispose();
    alarmTrendChart = null;
  }
  if (taskCompletionChart) {
    taskCompletionChart.dispose();
    taskCompletionChart = null;
  }
  if (taskDurationChart) {
    taskDurationChart.dispose();
    taskDurationChart = null;
  }
}

onUnmounted(() => {
  statisticsMounted = false
  if (resizeFrame !== null) {
    window.cancelAnimationFrame(resizeFrame)
    resizeFrame = null
  }
  window.removeEventListener('resize', resizeCharts)
  disposeAllCharts()
})
</script>

<style scoped>
.data-statistics {
  width: 100%;
  height: 100%;
  padding: 15px;
}

.stats-tabs {
  margin-bottom: 20px;
  height: 100%;
}

.filter-section {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-label {
  font-weight: 500;
  margin-right: 5px;
}

.chart-container {
  display: flex;
  margin-bottom: 20px;
  gap: 20px;
  flex-wrap: wrap;
}

.chart-wrapper {
  flex: 1;
  min-width: 300px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 15px;
  background-color: #fff;
}

.chart {
  height: 300px;
}

.table-container {
  margin-top: 20px;
  margin-bottom: 30px;
}

.export-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.export-buttons {
  display: flex;
  gap: 15px;
}

.ops-page-header { flex:0 0 auto;min-height:80px;margin-bottom:12px;padding:6px 6px 14px;border-bottom:1px solid #cfdeeb; }
.ops-eyebrow { color:#157da6;font-size:11px;letter-spacing:1.4px;font-weight:700; }
.ops-page-header h1 { margin:4px 0 2px;color:#153b5b;font-size:24px;line-height:1.2; }
.ops-page-header p { margin:0;color:#6e879a;font-size:12px; }

.data-statistics { display:flex;flex-direction:column;min-height:0;background:#f2f7fb; }
.stats-tabs { flex:1;min-height:0;height:auto;margin:0;border:0;border-top:2px solid #58b5d2;border-radius:8px;background:#fff;box-shadow:0 8px 30px rgba(21,63,99,.05); }
.stats-tabs :deep(.el-tabs__content) { height:calc(100% - 56px);overflow:auto; }
.chart-wrapper { border:0;border-top:1px solid #c5e2ed;border-radius:4px 4px 8px 8px;box-shadow:0 5px 20px rgba(21,63,99,.04); }
</style>
