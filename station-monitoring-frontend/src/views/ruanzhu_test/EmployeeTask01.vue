<template>
  <div class="task-manager-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">任务管理中心</h1>
      <span class="page-subtitle">管理您的工作任务与历史记录</span>
    </div>

    <!-- 筛选工具栏 -->
    <div class="toolbar-section">
      <div class="search-controls">
        <div class="search-box">
          <el-input
              v-model="searchCriteria.keyword"
              placeholder="搜索任务名称或描述"
              class="search-input"
              clearable
              @clear="refreshTaskData"
          >
            <template #prefix>
              <el-icon>
                <Search/>
              </el-icon>
            </template>
          </el-input>
        </div>

        <div class="filter-controls">
          <el-select
              v-model="searchCriteria.statusFilter"
              placeholder="任务状态"
              clearable
              class="filter-selector"
              @change="refreshTaskData"
          >
            <el-option
                v-for="status in TASK_STATUS_OPTIONS"
                :key="status.value"
                :label="status.label"
                :value="status.value"
            />
          </el-select>

          <el-select
              v-model="searchCriteria.typeFilter"
              placeholder="任务类型"
              clearable
              class="filter-selector"
              @change="refreshTaskData"
          >
            <el-option
                v-for="type in TASK_TYPE_OPTIONS"
                :key="type.value"
                :label="type.label"
                :value="type.value"
            />
          </el-select>

          <el-date-picker
              v-model="searchCriteria.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              class="date-range-picker"
              @change="refreshTaskData"
          />

          <div class="action-buttons">
            <el-button
                type="primary"
                icon="Search"
                @click="refreshTaskData"
                :loading="loadingStates.taskList"
            >
              搜索
            </el-button>
            <el-button icon="Refresh" @click="resetSearchFilters">
              重置
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content-area">
      <!-- 标签页导航 -->
      <div class="tab-navigation">
        <el-tabs v-model="activeView" class="view-tabs">
          <el-tab-pane label="当前任务" name="activeTasks"/>
          <el-tab-pane label="历史记录" name="taskHistory"/>
        </el-tabs>
      </div>

      <!-- 当前任务视图 -->
      <div v-show="activeView === 'activeTasks'" class="view-content">
        <div class="task-list-container">
          <el-table
              :data="activeTaskList"
              v-loading="loadingStates.taskList"
              class="task-data-table"
              :height="tableHeight"
              stripe
          >
            <el-table-column
                label="序号"
                width="70"
                align="center"
                fixed="left"
            >
              <template #default="{ $index }">
                <span class="sequence-number">
                  {{ calculateSequenceNumber($index) }}
                </span>
              </template>
            </el-table-column>

            <el-table-column
                prop="title"
                label="任务名称"
                min-width="160"
                align="center"
                show-overflow-tooltip
            />

            <el-table-column
                prop="description"
                label="任务描述"
                min-width="220"
                align="center"
                show-overflow-tooltip
            />

            <el-table-column
                label="优先级"
                width="90"
                align="center"
            >
              <template #default="{ row }">
                <el-tag
                    :type="getPriorityTagType(row.priority)"
                    effect="dark"
                    class="priority-tag"
                >
                  {{ formatPriorityText(row.priority) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column
                label="状态"
                width="110"
                align="center"
            >
              <template #default="{ row }">
                <el-tag
                    :type="getStatusTagType(row.status)"
                    effect="light"
                    class="status-tag"
                >
                  {{ formatStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column
                label="时间安排"
                width="180"
                align="center"
            >
              <template #default="{ row }">
                <div class="time-info">
                  <div class="time-item">
                    <span class="time-label">开始:</span>
                    <span class="time-value">{{ formatDateTime(row.startTime) }}</span>
                  </div>
                  <div class="time-item">
                    <span class="time-label">截止:</span>
                    <span class="time-value">{{ formatDateTime(row.endTime) }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column
                label="进度"
                width="130"
                align="center"
            >
              <template #default="{ row }">
                <el-progress
                    :percentage="calculateProgressPercentage(row.status)"
                    :status="getProgressStatus(row.status)"
                    :stroke-width="12"
                    class="progress-display"
                />
              </template>
            </el-table-column>

            <el-table-column
                label="操作"
                width="280"
                align="center"
                fixed="right"
            >
              <template #default="{ row }">
                <div class="action-buttons-group">
                  <el-button
                      size="small"
                      type="info"
                      plain
                      @click="displayTaskDetails(row)"
                  >
                    查看详情
                  </el-button>

                  <el-button
                      v-if="row.status === '0'"
                      size="small"
                      type="success"
                      plain
                      @click="initiateTaskAcceptance(row)"
                  >
                    接受任务
                  </el-button>

                  <el-button
                      v-if="row.status === '1'"
                      size="small"
                      type="warning"
                      plain
                      @click="initiateTaskExecution(row)"
                  >
                    开始执行
                  </el-button>

                  <el-button
                      v-if="row.status === '2'"
                      size="small"
                      type="primary"
                      plain
                      @click="initiateTaskCompletion(row)"
                  >
                    提交完成
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-controls">
            <el-pagination
                v-model:current-page="pagination.current"
                v-model:page-size="pagination.size"
                :total="pagination.total"
                :page-sizes="[10, 20, 30, 50]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="refreshTaskData"
                @current-change="refreshTaskData"
            />
          </div>
        </div>
      </div>

      <!-- 历史记录视图 -->
      <div v-show="activeView === 'taskHistory'" class="view-content">
        <div class="history-list-container">
          <el-table
              :data="historicalTaskList"
              v-loading="loadingStates.historyList"
              class="history-data-table"
              :height="tableHeight"
              stripe
          >
            <el-table-column
                label="记录ID"
                width="90"
                align="center"
                fixed="left"
            >
              <template #default="{ row }">
                <span class="record-id">{{ row.historyId }}</span>
              </template>
            </el-table-column>

            <el-table-column
                label="任务信息"
                min-width="200"
                align="center"
            >
              <template #default="{ row }">
                <div class="task-info">
                  <div class="task-name">{{ row.title }}</div>
                  <div class="task-id">ID: {{ row.taskId }}</div>
                </div>
              </template>
            </el-table-column>

            <el-table-column
                label="类型与优先级"
                width="140"
                align="center"
            >
              <template #default="{ row }">
                <div class="type-priority">
                  <div class="task-type">
                    {{ formatTaskTypeText(row.type) }}
                  </div>
                  <el-tag
                      :type="getPriorityTagType(row.priority)"
                      size="small"
                      class="history-priority-tag"
                  >
                    {{ formatPriorityText(row.priority) }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>

            <el-table-column
                label="状态"
                width="100"
                align="center"
            >
              <template #default="{ row }">
                <el-tag
                    :type="getStatusTagType(row.status)"
                    size="small"
                    class="history-status-tag"
                >
                  {{ formatStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column
                prop="statusTime"
                label="操作时间"
                width="170"
                align="center"
            >
              <template #default="{ row }">
                {{ formatDateTime(row.statusTime) }}
              </template>
            </el-table-column>

            <el-table-column
                prop="feedback"
                label="反馈内容"
                min-width="200"
                align="center"
                show-overflow-tooltip
            />

            <el-table-column
                label="操作"
                width="100"
                align="center"
                fixed="right"
            >
              <template #default="{ row }">
                <el-button
                    size="small"
                    type="info"
                    plain
                    @click="displayHistoricalDetails(row)"
                >
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-controls">
            <el-pagination
                v-model:current-page="historyPagination.current"
                v-model:page-size="historyPagination.size"
                :total="historyPagination.total"
                :page-sizes="[10, 20, 30, 50]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="refreshHistoricalData"
                @current-change="refreshHistoricalData"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 任务详情对话框 -->
    <el-dialog
        v-model="dialogs.detailsVisible"
        title="任务详细信息"
        width="70%"
        :close-on-click-modal="false"
    >
      <div v-if="selectedTaskData" class="task-detail-content">
        <el-descriptions
            :column="2"
            border
            size="medium"
            class="task-descriptions"
        >
          <el-descriptions-item label="任务名称">
            {{ selectedTaskData.title }}
          </el-descriptions-item>

          <el-descriptions-item label="任务类型">
            {{ formatTaskTypeText(selectedTaskData.type) }}
          </el-descriptions-item>

          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityTagType(selectedTaskData.priority)">
              {{ formatPriorityText(selectedTaskData.priority) }}
            </el-tag>
          </el-descriptions-item>

          <el-descriptions-item label="当前状态">
            <el-tag :type="getStatusTagType(selectedTaskData.status)">
              {{ formatStatusText(selectedTaskData.status) }}
            </el-tag>
          </el-descriptions-item>

          <el-descriptions-item label="负责人">
            {{ selectedTaskData.createdByUsername || '未指定' }}
          </el-descriptions-item>

          <el-descriptions-item label="审核人">
            {{ selectedTaskData.dealByUsername || '待分配' }}
          </el-descriptions-item>

          <el-descriptions-item label="创建时间" :span="2">
            {{ formatDateTime(selectedTaskData.createTime) }}
          </el-descriptions-item>

          <el-descriptions-item label="开始时间" :span="2">
            {{ formatDateTime(selectedTaskData.startTime) || '尚未开始' }}
          </el-descriptions-item>

          <el-descriptions-item label="完成时间" :span="2">
            {{ formatDateTime(selectedTaskData.finishTime) || '尚未完成' }}
          </el-descriptions-item>

          <el-descriptions-item label="截止时间" :span="2">
            {{ formatDateTime(selectedTaskData.endTime) }}
          </el-descriptions-item>

          <el-descriptions-item label="任务描述" :span="2">
            <div class="task-description-content">
              {{ selectedTaskData.description || '暂无描述' }}
            </div>
          </el-descriptions-item>

          <el-descriptions-item label="操作反馈" :span="2">
            {{ selectedTaskData.operationFeedback || '暂无反馈' }}
          </el-descriptions-item>

          <el-descriptions-item label="审核结果" :span="2">
            <div class="review-result">
              <el-tag
                  :type="getReviewResultType(selectedTaskData.status)"
                  size="large"
              >
                {{ formatReviewResult(selectedTaskData.status) }}
              </el-tag>
              <div
                  v-if="selectedTaskData.reviewComment"
                  class="review-comment-content"
              >
                {{ selectedTaskData.reviewComment }}
              </div>
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 进度时间轴 -->
        <div class="progress-timeline-section">
          <h3 class="section-title">任务进度时间线</h3>
          <el-steps
              :active="calculateStepProgress(selectedTaskData.status)"
              finish-status="success"
              align-center
          >
            <el-step
                title="待接受"
                :description="formatDateTime(selectedTaskData.createTime)"
            />
            <el-step
                title="已接受"
                :description="formatDateTime(selectedTaskData.acceptTime)"
            />
            <el-step
                title="执行中"
                :description="formatDateTime(selectedTaskData.startTime)"
            />
            <el-step
                title="待审核"
                :description="formatDateTime(selectedTaskData.finishTime)"
            />
            <el-step
                title="已完成"
                :description="formatDateTime(selectedTaskData.dealTime)"
            />
          </el-steps>
        </div>

        <!-- 附件列表 -->
        <div
            v-if="selectedTaskData.attachmentList?.length"
            class="attachments-section"
        >
          <h3 class="section-title">相关附件</h3>
          <div class="attachment-items-container">
            <div
                v-for="attachment in selectedTaskData.attachmentList"
                :key="attachment.id"
                class="attachment-item"
                @click="downloadAttachmentFile(attachment)"
            >
              <el-icon class="attachment-icon">
                <Document/>
              </el-icon>
              <span class="attachment-name">{{ attachment.name }}</span>
              <el-icon class="download-icon">
                <Download/>
              </el-icon>
            </div>
          </div>
        </div>

        <!-- 操作历史 -->
        <div
            v-if="selectedTaskData.stepList?.length"
            class="operation-history-section"
        >
          <h3 class="section-title">操作历史记录</h3>
          <el-timeline class="operation-timeline">
            <el-timeline-item
                v-for="step in selectedTaskData.stepList"
                :key="step.id"
                :timestamp="formatDateTime(step.statusTime)"
                :type="getTimelineStepType(step.status)"
                placement="top"
            >
              {{ formatStepDescription(step, selectedTaskData) }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-dialog>

    <!-- 接受任务确认对话框 -->
    <el-dialog
        v-model="dialogs.acceptDialogVisible"
        title="确认接受任务"
        width="45%"
    >
      <div v-if="selectedTaskData" class="confirmation-dialog-content">
        <el-alert
            title="任务接受确认"
            type="info"
            :closable="false"
            show-icon
            class="confirmation-alert"
        >
          您确定要接受此任务吗？接受后，您将负责该任务的执行与完成。
        </el-alert>

        <el-descriptions :column="1" border class="confirmation-descriptions">
          <el-descriptions-item label="任务名称">
            {{ selectedTaskData.title }}
          </el-descriptions-item>

          <el-descriptions-item label="任务描述">
            {{ selectedTaskData.description }}
          </el-descriptions-item>

          <el-descriptions-item label="截止时间">
            {{ formatDateTime(selectedTaskData.endTime) }}
          </el-descriptions-item>

          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityTagType(selectedTaskData.priority)">
              {{ formatPriorityText(selectedTaskData.priority) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="dialog-footer">
          <el-button @click="dialogs.acceptDialogVisible = false">
            取消操作
          </el-button>
          <el-button
              type="primary"
              @click="confirmTaskAcceptance"
              :loading="loadingStates.taskAccept"
          >
            确认接受
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 开始任务确认对话框 -->
    <el-dialog
        v-model="dialogs.startDialogVisible"
        title="确认开始任务"
        width="45%"
    >
      <div v-if="selectedTaskData" class="confirmation-dialog-content">
        <el-alert
            title="任务开始确认"
            type="warning"
            :closable="false"
            show-icon
            class="confirmation-alert"
        >
          确认开始执行此任务吗？系统将记录任务开始时间。
        </el-alert>

        <el-descriptions :column="1" border class="confirmation-descriptions">
          <el-descriptions-item label="任务名称">
            {{ selectedTaskData.title }}
          </el-descriptions-item>

          <el-descriptions-item label="任务描述">
            {{ selectedTaskData.description }}
          </el-descriptions-item>

          <el-descriptions-item label="截止时间">
            {{ formatDateTime(selectedTaskData.endTime) }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="dialog-footer">
          <el-button @click="dialogs.startDialogVisible = false">
            暂不开始
          </el-button>
          <el-button
              type="warning"
              @click="confirmTaskExecution"
              :loading="loadingStates.taskStart"
          >
            确认开始
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 完成任务提交对话框 -->
    <el-dialog
        v-model="dialogs.completeDialogVisible"
        title="提交任务完成"
        width="55%"
    >
      <div v-if="selectedTaskData" class="completion-dialog-content">
        <el-descriptions :column="1" border class="task-summary-descriptions">
          <el-descriptions-item label="任务名称">
            {{ selectedTaskData.title }}
          </el-descriptions-item>

          <el-descriptions-item label="任务描述">
            {{ selectedTaskData.description }}
          </el-descriptions-item>

          <el-descriptions-item label="开始时间">
            {{ formatDateTime(selectedTaskData.startTime) }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="completion-form-section">
          <el-form
              :model="completionFormData"
              :rules="completionFormRules"
              ref="completionFormRef"
              label-width="100px"
              class="completion-form"
          >
            <el-form-item label="完成反馈" prop="feedbackContent">
              <el-input
                  v-model="completionFormData.feedbackContent"
                  type="textarea"
                  :rows="4"
                  placeholder="请详细描述任务完成情况、遇到的问题及解决方案"
                  maxlength="500"
                  show-word-limit
              />
            </el-form-item>

            <el-form-item label="相关附件">
              <el-upload
                  ref="fileUploadRef"
                  :http-request="handleFileUpload"
                  multiple
                  :limit="5"
                  :on-exceed="handleFileLimitExceeded"
                  :on-success="handleUploadSuccess"
                  :on-error="handleUploadError"
                  :on-remove="handleFileRemoval"
                  :before-upload="validateFileBeforeUpload"
                  :file-list="uploadedFilesList"
              >
                <template #trigger>
                  <el-button type="primary" icon="Upload">
                    选择文件
                  </el-button>
                </template>

                <template #tip>
                  <div class="upload-tips">
                    支持上传文档、图片等格式，单个文件不超过10MB，最多可上传5个文件
                  </div>
                </template>
              </el-upload>
            </el-form-item>
          </el-form>
        </div>

        <div class="dialog-footer">
          <el-button @click="dialogs.completeDialogVisible = false">
            取消提交
          </el-button>
          <el-button
              type="success"
              @click="submitTaskCompletion"
              :loading="loadingStates.taskComplete"
          >
            提交完成
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, reactive, computed, onMounted, nextTick} from 'vue'
import {Search, Download, Document, Upload} from '@element-plus/icons-vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {
  getEmployeeTask,
  getTaskById,
  getTaskStep,
  getTaskAttachmentList,
  downloadAttachment,
  getAllTaskDetailHistoryByUserId,
  updateTaskStatus,
  uploadAttachment,
  submitOperationFeedBack
} from '@/http/api/task.js'

// ==================== 常量定义 ====================
const TASK_STATUS = {
  PENDING_ACCEPT: '0',
  ACCEPTED: '1',
  IN_PROGRESS: '2',
  PENDING_REVIEW: '3',
  COMPLETED: '4',
  REJECTED: '5'
}

const TASK_STATUS_OPTIONS = [
  {value: '', label: '全部状态'},
  {value: TASK_STATUS.PENDING_ACCEPT, label: '待接受'},
  {value: TASK_STATUS.ACCEPTED, label: '已接受'},
  {value: TASK_STATUS.IN_PROGRESS, label: '进行中'},
  {value: TASK_STATUS.PENDING_REVIEW, label: '待审核'},
  {value: TASK_STATUS.COMPLETED, label: '已完成'},
  {value: TASK_STATUS.REJECTED, label: '已驳回'}
]

const TASK_TYPE_OPTIONS = [
  {value: '', label: '全部类型'},
  {value: '0', label: '日常巡检'},
  {value: '1', label: '维修任务'},
  {value: '2', label: '异常处理'},
  {value: '3', label: '设备安装'}
]

// ==================== 响应式数据 ====================
// 加载状态管理
const loadingStates = reactive({
  taskList: false,
  historyList: false,
  taskAccept: false,
  taskStart: false,
  taskComplete: false
})

// 搜索条件
const searchCriteria = reactive({
  keyword: '',
  statusFilter: '',
  typeFilter: '',
  dateRange: []
})

// 分页配置
const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

const historyPagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

// 数据列表
const activeTaskList = ref([])
const historicalTaskList = ref([])

// 视图状态
const activeView = ref('activeTasks')

// 对话框状态
const dialogs = reactive({
  detailsVisible: false,
  acceptDialogVisible: false,
  startDialogVisible: false,
  completeDialogVisible: false
})

// 选中的任务数据
const selectedTaskData = ref(null)

// 完成表单数据
const completionFormData = reactive({
  feedbackContent: ''
})

// 文件上传相关
const uploadedFilesList = ref([])
const completionFormRef = ref(null)
const fileUploadRef = ref(null)

// ==================== 表单验证规则 ====================
const completionFormRules = {
  feedbackContent: [
    {required: true, message: '请填写任务完成反馈', trigger: 'blur'},
    {min: 5, max: 500, message: '反馈内容长度应在5-500字符之间', trigger: 'blur'}
  ]
}

// ==================== 计算属性 ====================
const tableHeight = computed(() => {
  return window.innerHeight - 400
})

// ==================== 格式化函数 ====================
const formatDateTime = (timestamp) => {
  if (!timestamp) return ''

  try {
    const dateObj = new Date(timestamp)
    if (isNaN(dateObj.getTime())) return timestamp

    return dateObj.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    }).replace(/\//g, '-')
  } catch {
    return timestamp
  }
}

const formatStatusText = (statusCode) => {
  const statusMap = {
    [TASK_STATUS.PENDING_ACCEPT]: '待接受',
    [TASK_STATUS.ACCEPTED]: '已接受',
    [TASK_STATUS.IN_PROGRESS]: '进行中',
    [TASK_STATUS.PENDING_REVIEW]: '待审核',
    [TASK_STATUS.COMPLETED]: '已完成',
    [TASK_STATUS.REJECTED]: '已驳回'
  }
  return statusMap[statusCode] || '未知状态'
}

const formatTaskTypeText = (typeCode) => {
  const typeMap = {
    '0': '日常巡检',
    '1': '维修任务',
    '2': '异常处理',
    '3': '设备安装'
  }
  return typeMap[typeCode] || '其他任务'
}

const formatPriorityText = (priorityCode) => {
  const priorityMap = {
    '0': '低',
    '1': '中',
    '2': '高',
    0: '低',
    1: '中',
    2: '高'
  }
  return priorityMap[priorityCode] || '未知'
}

// ==================== 样式获取函数 ====================
const getStatusTagType = (statusCode) => {
  const typeMap = {
    [TASK_STATUS.PENDING_ACCEPT]: 'info',
    [TASK_STATUS.ACCEPTED]: 'primary',
    [TASK_STATUS.IN_PROGRESS]: 'warning',
    [TASK_STATUS.PENDING_REVIEW]: 'warning',
    [TASK_STATUS.COMPLETED]: 'success',
    [TASK_STATUS.REJECTED]: 'danger'
  }
  return typeMap[statusCode] || 'info'
}

const getPriorityTagType = (priorityCode) => {
  const typeMap = {
    '0': '',
    '1': 'warning',
    '2': 'danger',
    0: '',
    1: 'warning',
    2: 'danger'
  }
  return typeMap[priorityCode] || ''
}

// ==================== 进度相关函数 ====================
const calculateProgressPercentage = (statusCode) => {
  const progressMap = {
    [TASK_STATUS.PENDING_ACCEPT]: 0,
    [TASK_STATUS.ACCEPTED]: 25,
    [TASK_STATUS.IN_PROGRESS]: 50,
    [TASK_STATUS.PENDING_REVIEW]: 100,
    [TASK_STATUS.COMPLETED]: 100,
    [TASK_STATUS.REJECTED]: 50
  }
  return progressMap[statusCode] || 0
}

const getProgressStatus = (statusCode) => {
  if (statusCode === TASK_STATUS.COMPLETED) return 'success'
  if (statusCode === TASK_STATUS.REJECTED) return 'exception'
  return ''
}

const calculateStepProgress = (statusCode) => {
  const stepMap = {
    [TASK_STATUS.PENDING_ACCEPT]: 0,
    [TASK_STATUS.ACCEPTED]: 1,
    [TASK_STATUS.IN_PROGRESS]: 2,
    [TASK_STATUS.PENDING_REVIEW]: 3,
    [TASK_STATUS.COMPLETED]: 4,
    [TASK_STATUS.REJECTED]: 2
  }
  return stepMap[statusCode] || 0
}

// ==================== 工具函数 ====================
const calculateSequenceNumber = (index) => {
  return (pagination.current - 1) * pagination.size + index + 1
}

const getReviewResultType = (statusCode) => {
  if (statusCode === TASK_STATUS.COMPLETED) return 'success'
  if (statusCode === TASK_STATUS.REJECTED) return 'danger'
  return 'info'
}

const formatReviewResult = (statusCode) => {
  if (statusCode === TASK_STATUS.COMPLETED) return '审核通过'
  if (statusCode === TASK_STATUS.REJECTED) return '审核不通过'
  return '等待审核'
}

const getTimelineStepType = (statusCode) => {
  if (statusCode === TASK_STATUS.COMPLETED) return 'success'
  if (statusCode === TASK_STATUS.REJECTED) return 'danger'
  if (statusCode === TASK_STATUS.PENDING_REVIEW) return 'warning'
  return 'primary'
}

const formatStepDescription = (stepData, taskData) => {
  const actionMap = {
    [TASK_STATUS.PENDING_ACCEPT]: '任务已创建，等待接受',
    [TASK_STATUS.ACCEPTED]: `${taskData.assignedToUsername || '您'}已接受任务`,
    [TASK_STATUS.IN_PROGRESS]: `${taskData.assignedToUsername || '您'}开始执行任务`,
    [TASK_STATUS.PENDING_REVIEW]: '任务已提交，等待审核',
    [TASK_STATUS.COMPLETED]: '任务已完成，审核通过',
    [TASK_STATUS.REJECTED]: `任务被驳回，原因：${stepData.feedback || '未提供原因'}`
  }
  return actionMap[stepData.status] || `状态更新：${stepData.status}`
}

// ==================== 数据获取函数 ====================
const fetchActiveTaskData = async () => {
  loadingStates.taskList = true

  try {
    const queryParams = {
      page: pagination.current,
      size: pagination.size,
      search: searchCriteria.keyword,
      status: searchCriteria.statusFilter,
      type: searchCriteria.typeFilter
    }

    // 添加日期范围参数
    if (searchCriteria.dateRange?.length === 2) {
      const [startDate, endDate] = searchCriteria.dateRange
      queryParams.createDate = formatDateParam(startDate)
      queryParams.endDate = formatDateParam(endDate)
    }

    const response = await getEmployeeTask(queryParams)

    if (response.data?.success) {
      activeTaskList.value = response.data.data.taskList || []
      pagination.total = response.data.data.total || 0
    } else {
      ElMessage.error(response.data?.message || '获取任务数据失败')
    }
  } catch (error) {
    console.error('获取任务数据异常:', error)
    ElMessage.error('网络错误，获取任务数据失败')
  } finally {
    loadingStates.taskList = false
  }
}

const fetchHistoricalTaskData = async () => {
  loadingStates.historyList = true

  try {
    const queryParams = {
      page: historyPagination.current,
      size: historyPagination.size,
      search: searchCriteria.keyword,
      status: searchCriteria.statusFilter,
      type: searchCriteria.typeFilter
    }

    // 添加日期范围参数
    if (searchCriteria.dateRange?.length === 2) {
      const [startDate, endDate] = searchCriteria.dateRange
      queryParams.createDate = formatDateParam(startDate)
      queryParams.endDate = formatDateParam(endDate)
    }

    const response = await getAllTaskDetailHistoryByUserId(queryParams)

    if (response.data?.success) {
      historicalTaskList.value = response.data.data.taskDetailHistoryList || []
      historyPagination.total = response.data.data.taskDetailHistoryCount || 0
    } else {
      ElMessage.error(response.data?.message || '获取历史记录失败')
    }
  } catch (error) {
    console.error('获取历史记录异常:', error)
    ElMessage.error('网络错误，获取历史记录失败')
  } finally {
    loadingStates.historyList = false
  }
}

const formatDateParam = (dateValue) => {
  if (!dateValue) return null

  if (typeof dateValue === 'string') {
    const dateObj = new Date(dateValue)
    return isNaN(dateObj.getTime()) ? dateValue : dateObj.toISOString().slice(0, 10)
  }

  if (dateValue instanceof Date) {
    return dateValue.toISOString().slice(0, 10)
  }

  return dateValue
}

// ==================== 视图刷新函数 ====================
const refreshTaskData = () => {
  if (activeView.value === 'activeTasks') {
    fetchActiveTaskData()
  } else {
    fetchHistoricalTaskData()
  }
}

const refreshHistoricalData = () => {
  fetchHistoricalTaskData()
}

// ==================== 搜索功能 ====================
const resetSearchFilters = () => {
  searchCriteria.keyword = ''
  searchCriteria.statusFilter = ''
  searchCriteria.typeFilter = ''
  searchCriteria.dateRange = []
  pagination.current = 1
  historyPagination.current = 1
  refreshTaskData()
}

// ==================== 任务详情相关 ====================
const displayTaskDetails = async (taskItem) => {
  try {
    loadingStates.taskList = true
    selectedTaskData.value = taskItem

    const [detailResponse, stepResponse, attachmentResponse] = await Promise.all([
      getTaskById(taskItem.id),
      getTaskStep(taskItem.id),
      getTaskAttachmentList(taskItem.id)
    ])

    if (detailResponse.data?.success && stepResponse.data?.success && attachmentResponse.data?.success) {
      selectedTaskData.value = {
        ...detailResponse.data.data,
        stepList: stepResponse.data.data,
        attachmentList: attachmentResponse.data.data
      }
      dialogs.detailsVisible = true
    } else {
      ElMessage.error('获取任务详情信息失败')
    }
  } catch (error) {
    console.error('获取任务详情异常:', error)
    ElMessage.error('网络错误，获取详情失败')
  } finally {
    loadingStates.taskList = false
  }
}

const displayHistoricalDetails = async (historyItem) => {
  try {
    const response = await getTaskById(historyItem.taskId)

    if (response.data?.success) {
      selectedTaskData.value = response.data.data
      dialogs.detailsVisible = true
    } else {
      ElMessage.error('获取历史详情失败')
    }
  } catch (error) {
    console.error('获取历史详情异常:', error)
    ElMessage.error('网络错误，获取详情失败')
  }
}

// ==================== 附件处理 ====================
const downloadAttachmentFile = async (attachmentItem) => {
  try {
    const response = await downloadAttachment(attachmentItem.id)

    // 创建下载链接
    const downloadUrl = window.URL.createObjectURL(new Blob([response.data]))
    const downloadLink = document.createElement('a')
    downloadLink.href = downloadUrl
    downloadLink.download = attachmentItem.name
    document.body.appendChild(downloadLink)
    downloadLink.click()
    document.body.removeChild(downloadLink)
    window.URL.revokeObjectURL(downloadUrl)

    ElMessage.success(`附件下载成功: ${attachmentItem.name}`)
  } catch (error) {
    console.error('下载附件异常:', error)
    ElMessage.error(`附件下载失败: ${attachmentItem.name}`)
  }
}

// ==================== 任务操作相关 ====================
const initiateTaskAcceptance = (taskItem) => {
  selectedTaskData.value = taskItem
  dialogs.acceptDialogVisible = true
}

const confirmTaskAcceptance = async () => {
  if (!selectedTaskData.value) return

  loadingStates.taskAccept = true

  try {
    const response = await updateTaskStatus(selectedTaskData.value.id, TASK_STATUS.ACCEPTED)

    if (response.data?.success) {
      ElMessage.success('任务接受成功')
      dialogs.acceptDialogVisible = false
      await fetchActiveTaskData()
    } else {
      ElMessage.error(response.data?.message || '任务接受操作失败')
    }
  } catch (error) {
    console.error('接受任务异常:', error)
    ElMessage.error('网络错误，接受任务失败')
  } finally {
    loadingStates.taskAccept = false
  }
}

const initiateTaskExecution = (taskItem) => {
  selectedTaskData.value = taskItem
  dialogs.startDialogVisible = true
}

const confirmTaskExecution = async () => {
  if (!selectedTaskData.value) return

  loadingStates.taskStart = true

  try {
    const response = await updateTaskStatus(selectedTaskData.value.id, TASK_STATUS.IN_PROGRESS)

    if (response.data?.success) {
      ElMessage.success('任务开始执行成功')
      dialogs.startDialogVisible = false
      await fetchActiveTaskData()
    } else {
      ElMessage.error(response.data?.message || '任务开始操作失败')
    }
  } catch (error) {
    console.error('开始任务异常:', error)
    ElMessage.error('网络错误，开始任务失败')
  } finally {
    loadingStates.taskStart = false
  }
}

const initiateTaskCompletion = (taskItem) => {
  selectedTaskData.value = taskItem
  completionFormData.feedbackContent = ''
  uploadedFilesList.value = []
  dialogs.completeDialogVisible = true

  nextTick(() => {
    if (completionFormRef.value) {
      completionFormRef.value.clearValidate()
    }
  })
}

// ==================== 文件上传处理 ====================
const validateFileBeforeUpload = (fileItem) => {
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (fileItem.size > maxSize) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }
  return true
}

const handleFileLimitExceeded = () => {
  ElMessage.warning('最多只能上传5个文件')
}

const handleUploadSuccess = (responseData) => {
  ElMessage.success('文件上传成功')
}

const handleUploadError = () => {
  ElMessage.error('文件上传失败')
}

const handleFileRemoval = (fileItem) => {
  const fileUrl = fileItem.response?.data?.url
  if (fileUrl) {
    // 从表单数据中移除对应的附件
    completionFormData.attachments = completionFormData.attachments?.filter(
        attachment => attachment.url !== fileUrl
    ) || []
  }
}

const handleFileUpload = async (uploadOptions) => {
  const {file: fileItem, onSuccess, onError} = uploadOptions

  try {
    const response = await uploadAttachment(fileItem, selectedTaskData.value.id)

    if (response.data?.success) {
      onSuccess(response)
      // 添加到表单附件列表
      if (!completionFormData.attachments) {
        completionFormData.attachments = []
      }
      completionFormData.attachments.push(response.data)
      ElMessage.success(`文件 ${fileItem.name} 上传成功`)
    } else {
      const errorMessage = response.data?.message || '文件上传失败'
      onError(new Error(errorMessage))
      ElMessage.error(errorMessage)
    }
  } catch (error) {
    console.error('文件上传异常:', error)
    onError(error)
    ElMessage.error(`文件上传失败: ${error.message}`)
  }
}

// ==================== 任务完成提交 ====================
const submitTaskCompletion = async () => {
  if (!selectedTaskData.value) return

  // 表单验证
  if (!completionFormRef.value) return

  try {
    await completionFormRef.value.validate()
  } catch {
    ElMessage.warning('请完善任务完成反馈信息')
    return
  }

  loadingStates.taskComplete = true

  try {
    // 更新任务状态
    const statusResponse = await updateTaskStatus(
        selectedTaskData.value.id,
        TASK_STATUS.PENDING_REVIEW
    )

    // 提交反馈信息
    const feedbackResponse = await submitOperationFeedBack(
        selectedTaskData.value.id,
        completionFormData.feedbackContent
    )

    // 处理文件上传
    let uploadSuccess = true
    if (uploadedFilesList.value.length > 0) {
      for (const fileItem of uploadedFilesList.value) {
        try {
          await uploadAttachment(fileItem.raw, selectedTaskData.value.id)
        } catch {
          uploadSuccess = false
        }
      }

      if (!uploadSuccess) {
        ElMessage.warning('部分文件上传失败，但任务状态已更新')
      }
    }

    if (statusResponse.data?.success && feedbackResponse.data?.success) {
      ElMessage.success('任务提交成功，等待审核')
      dialogs.completeDialogVisible = false
      await fetchActiveTaskData()
    } else {
      ElMessage.error('任务提交操作失败')
    }
  } catch (error) {
    console.error('提交任务异常:', error)
    ElMessage.error('网络错误，提交任务失败')
  } finally {
    loadingStates.taskComplete = false
  }
}

// ==================== 视图切换处理 ====================
const handleViewChange = (viewName) => {
  if (viewName === 'activeTasks') {
    fetchActiveTaskData()
  } else if (viewName === 'taskHistory') {
    fetchHistoricalTaskData()
  }
}

// ==================== 生命周期钩子 ====================
onMounted(() => {
  fetchActiveTaskData()
})
</script>

<style scoped>
.task-manager-container {
  padding: 24px;
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.page-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
}

.toolbar-section {
  margin-bottom: 20px;
  background: #ffffff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.search-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-box {
  flex: 1;
  max-width: 300px;
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-selector {
  width: 140px;
}

.date-range-picker {
  width: 280px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.main-content-area {
  flex: 1;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tab-navigation {
  padding: 0 24px;
  border-bottom: 1px solid #e4e7ed;
}

.view-tabs {
  :deep(.el-tabs__header) {
    margin: 0;
  }
}

.view-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 16px;
}

.task-list-container,
.history-list-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.task-data-table,
.history-data-table {
  flex: 1;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  overflow: hidden;
}

.sequence-number {
  font-weight: 500;
  color: #409eff;
}

.priority-tag,
.status-tag {
  font-weight: 500;
}

.time-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.time-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.time-label {
  color: #909399;
  font-weight: 500;
}

.time-value {
  color: #606266;
}

.progress-display {
  margin: 0 auto;
  width: 100%;
}

.action-buttons-group {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-name {
  font-weight: 500;
  color: #303133;
}

.task-id {
  font-size: 12px;
  color: #909399;
}

.type-priority {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
}

.history-priority-tag,
.history-status-tag {
  width: fit-content;
}

.pagination-controls {
  padding: 16px 0;
  display: flex;
  justify-content: center;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* 任务详情对话框样式 */
.task-detail-content {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 8px;
}

.task-descriptions {
  margin-bottom: 24px;
}

.task-description-content {
  line-height: 1.6;
  color: #606266;
}

.review-result {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.review-comment-content {
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 24px 0 16px 0;
  padding-left: 12px;
  border-left: 3px solid #409eff;
}

.progress-timeline-section {
  margin: 24px 0;
}

.attachments-section {
  margin: 24px 0;
}

.attachment-items-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  gap: 8px;
}

.attachment-item:hover {
  background: #e4e7ed;
}

.attachment-icon {
  color: #409eff;
  font-size: 18px;
}

.attachment-name {
  flex: 1;
  color: #303133;
  font-size: 14px;
}

.download-icon {
  color: #909399;
  font-size: 16px;
}

.operation-history-section {
  margin: 24px 0;
}

.operation-timeline {
  padding-left: 20px;
}

/* 确认对话框样式 */
.confirmation-dialog-content,
.completion-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.confirmation-alert {
  margin-bottom: 16px;
}

.confirmation-descriptions,
.task-summary-descriptions {
  margin-bottom: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.completion-form-section {
  margin-top: 20px;
}

.completion-form {
  .el-form-item {
    margin-bottom: 20px;
  }
}

.upload-tips {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a0a4ac;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .search-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    max-width: 100%;
  }

  .filter-controls {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .task-manager-container {
    padding: 16px;
  }

  .toolbar-section {
    padding: 12px;
  }

  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-selector,
  .date-range-picker {
    width: 100%;
  }

  .action-buttons-group {
    flex-direction: column;
    align-items: stretch;
  }

  .action-buttons-group .el-button {
    margin-bottom: 4px;
  }
}
</style>