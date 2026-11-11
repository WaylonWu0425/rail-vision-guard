<template>
  <div class="employee-task-container">
    <div class="page-title">我的任务</div>

    <!-- 任务操作区 -->
    <div class="action-bar">
      <span>搜索：</span>
      <el-input
          v-model="searchInput"
          placeholder="搜索任务"
          class="search-input"
          clearable
      >
        <template #prefix>
          <el-icon>
            <Search/>
          </el-icon>
        </template>
      </el-input>
      <span>筛选：</span>

      <el-select v-model="filterStatus" placeholder="任务状态" clearable class="filter-select">
        <el-option label="待接受" value="0"/>
        <el-option label="已接受" value="1"/>
        <el-option label="进行中" value="2"/>
        <el-option label="待审核" value="3"/>
        <el-option label="已完成" value="4"/>
        <el-option label="已驳回" value="5"/>
      </el-select>

      <el-select v-model="filterType" placeholder="任务类型" clearable class="filter-select">
        <el-option label="日常巡检" value="0"/>
        <el-option label="维修任务" value="1"/>
        <el-option label="异常处理" value="2"/>
        <el-option label="设备安装" value="3"/>
      </el-select>

      <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="创建日期"
          end-placeholder="截止日期"
          class="date-picker"
      />

      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="resetSearch">重置</el-button>
    </div>

    <!-- 任务列表/表格 -->
    <div class="list">
      <!-- 标签页放在顶部 -->
      <div class="tabs-header">
        <el-tabs v-model="activeTab" @tab-click="handleTabClick">
          <el-tab-pane label="我的任务" name="myTasks"></el-tab-pane>
          <el-tab-pane label="历史记录" name="history"></el-tab-pane>
        </el-tabs>
      </div>

      <!-- 表格内容区域 -->
      <div class="tabs-content">
        <!-- 我的任务表格 -->
        <div v-show="activeTab === 'myTasks'" class="tab-content">
          <el-table :data="tasks" style="width: 100%" v-loading="loading" class="table-form">
            <el-table-column fixed prop="id" label="序号" min-width="60" align="center">
              <template #default="{ $index }">
                {{ $index + 1 }}
              </template>
            </el-table-column>
            <el-table-column prop="title" label="任务名称" min-width="150" align="center"/>
            <el-table-column prop="description" label="任务描述" min-width="200" show-overflow-tooltip align="center"/>
            <el-table-column prop="priority" label="优先级" min-width="80" align="center">
              <template #default="scope">
                <el-tag
                    :type="scope.row.priority == 2 ? 'danger' : scope.row.priority == 1 ? 'warning' : 'primary'"
                    style="font-weight: bold"
                >
                  {{ scope.row.priority == 2 ? '高' : scope.row.priority == 1 ? '中' : '低' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" min-width="100" align="center">
              <template #default="scope">
                <el-tag
                    :type="getStatusType(scope.row.status)"
                    style="font-weight: bold"
                >
                  {{ getStatusLabel(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="startTime" label="开始时间" min-width="160" :formatter="formatTime" align="center"/>
            <el-table-column prop="endTime" label="截止时间" min-width="160" :formatter="formatTime" align="center"/>
            <el-table-column label="进度" min-width="120" align="center">
              <template #default="scope">
                <el-progress
                    :percentage="getProgressValue(scope.row.status)"
                    :status="scope.row.status == '4' ? 'success' : scope.row.status == '5' ? 'exception' : ''"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="260" align="center">
              <template #default="scope">
                <el-button
                    size="small"
                    @click="viewTaskDetails(scope.row)"
                    type="primary"
                    plain
                >
                  详情
                </el-button>
                <el-button
                    size="small"
                    @click="acceptTask(scope.row)"
                    v-if="scope.row.status === '0'"
                    type="success"
                    plain
                >
                  接受
                </el-button>
                <el-button
                    size="small"
                    @click="startTask(scope.row)"
                    v-if="scope.row.status === '1'"
                    type="warning"
                    plain
                >
                  开始
                </el-button>
                <el-button
                    size="small"
                    @click="completeTask(scope.row)"
                    v-if="scope.row.status === '2'"
                    type="success"
                    plain
                >
                  完成
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
              layout="prev, pager, next, total"
              :total="totalTasks"
              :page-size="pageSize"
              :current-page="currentPage"
              @current-change="handlePageChange"
              class="pagination"
          />
        </div>

        <!-- 历史记录表格 -->
        <div v-show="activeTab === 'history'" class="tab-content">
          <el-table :data="historyRecords" v-loading="historyLoading" style="width: 100%;height: 92%;">
            <el-table-column prop="historyId" label="记录ID" min-width="80" align="center"/>
            <el-table-column prop="taskId" label="任务ID" min-width="80" align="center"/>
            <el-table-column prop="title" label="任务名称" min-width="150" align="center"/>
            <el-table-column prop="type" label="任务类型" min-width="100" align="center">
              <template #default="scope">
                {{ formatTaskType(scope.row.type) }}
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" min-width="80" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.priority == 2 ? 'danger' : scope.row.priority == 1 ? 'warning' : 'primary'">
                  {{ formatPriority(scope.row.priority) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" min-width="100" align="center">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ getStatusLabel(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="statusTime" label="操作时间" min-width="160" align="center" :formatter="formatTime"/>
            <el-table-column prop="feedback" label="反馈" min-width="180" align="center"/>
            <el-table-column label="操作" min-width="100" align="center">
              <template #default="scope">
                <el-button
                    size="small"
                    @click="viewTaskDetails(scope.row, true)"
                    type="primary"
                    plain
                >
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
              layout="prev, pager, next, total"
              :total="totalHistory"
              :page-size="historyPageSize"
              :current-page="historyCurrentPage"
              @current-change="handleHistoryPageChange"
              class="pagination"
          />
        </div>
      </div>
    </div>

    <!-- 任务详情对话框 -->
    <el-dialog v-model="detailsVisible" title="任务详情" width="60%">
      <div v-if="currentTask">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称">{{ currentTask.title }}</el-descriptions-item>
          <el-descriptions-item label="任务类型">{{ formatTaskType(currentTask.type) }}</el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag
                :type="currentTask.priority === '2' ? 'danger' : currentTask.priority === '1' ? 'warning' : 'info'"
            >
              {{ formatPriority(currentTask.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentTask.status)">
              {{ formatTaskStatus(currentTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建人">{{ currentTask.createdByUsername }}</el-descriptions-item>
          <el-descriptions-item label="审核人员">{{ currentTask.dealByUsername }}</el-descriptions-item>
          <el-descriptions-item label="开始时间" :span="2">{{
              safeFormatDate(currentTask.startTime) || '尚未开始'
            }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间" :span="2">{{
              safeFormatDate(currentTask.finishTime) || '尚未完成'
            }}
          </el-descriptions-item>
          <el-descriptions-item label="截止时间" :span="2">{{
              safeFormatDate(currentTask.endTime)
            }}
          </el-descriptions-item>
          <el-descriptions-item label="任务描述" :span="2">{{ currentTask.description }}</el-descriptions-item>
          <el-descriptions-item label="操作反馈" :span="2">{{
              currentTask.operationFeedback || '暂无反馈'
            }}
          </el-descriptions-item>
          <el-descriptions-item label="审核反馈" :span="2">
            <el-tag
                :type="currentTask.status == '4'
                ? 'success'
                : currentTask.status == '5'
                  ? 'danger'
                  : 'info'"
                disable-transitions
            >
              {{
                currentTask.status == '4'
                    ? '通过'
                    : currentTask.status == '5'
                        ? '不通过'
                        : currentTask.status != 5 && currentTask.status != 4
                            ? '暂无反馈'
                            : currentTask.status
              }}
            </el-tag>
            <div v-if="currentTask.reviewComment" class="review-comment">
              {{ currentTask.reviewComment }}
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <div class="task-progress-section">
          <h3>任务进度</h3>
          <el-steps :active="getProgressStep(currentTask)" finish-status="success">
            <el-step title="待接受" :description="safeFormatDate(currentTask.createTime)"/>
            <el-step title="已接受" :description="safeFormatDate(currentTask.acceptTime)"/>
            <el-step title="进行中" :description="safeFormatDate(currentTask.startTime)"/>
            <el-step title="待审核" :description="safeFormatDate(currentTask.finishTime)"/>
            <el-step title="已完成" :description="safeFormatDate(currentTask.dealTime)"/>
          </el-steps>
        </div>

        <div class="task-attachments-section" v-if="currentTask.attachmentList && currentTask.attachmentList.length">
          <h3>任务附件</h3>
          <div class="attachment-list">
            <el-tag v-for="(attachment, index) in currentTask.attachmentList" :key="index" class="attachment-tag">
              {{ attachment.name }}
              <el-icon @click="downloadAttachmentByid(attachment)">
                <Download/>
              </el-icon>
            </el-tag>
          </div>
        </div>

        <div class="task-history-section">
          <h3>操作历史</h3>
          <el-timeline>
            <el-timeline-item
                v-for="activity in currentTask.stepList"
                :key="activity.id"
                :timestamp="safeFormatDate(activity.statusTime)"
                :type="getStepType(activity.status)"
            >
              {{ formatStepContent(activity, currentTask) }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-dialog>

    <!-- 接受任务对话框 -->
    <el-dialog v-model="acceptDialogVisible" title="接受任务" width="40%">
      <div v-if="currentTask">
        <el-alert
            title="任务确认"
            type="info"
            description="您确定要接受此任务吗？接受后，您将负责完成此任务。"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
        />
        <el-descriptions :column="1" border>
          <el-descriptions-item label="任务名称">{{ currentTask.title }}</el-descriptions-item>
          <el-descriptions-item label="任务描述">{{ currentTask.description }}</el-descriptions-item>
          <el-descriptions-item label="截止时间">{{ safeFormatDate(currentTask.endTime) }}</el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="currentTask.priority === '2' ? 'danger' : currentTask.priority === '1' ? 'warning' : 'info'">
              {{ formatPriority(currentTask.priority) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="acceptDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAcceptTask">确认接受</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 开始任务对话框 -->
    <el-dialog v-model="startDialogVisible" title="开始任务" width="40%">
      <div v-if="currentTask">
        <el-alert
            title="开始任务"
            type="warning"
            description="您确定要开始执行此任务吗？任务开始后将记录时间。"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
        />
        <el-descriptions :column="1" border>
          <el-descriptions-item label="任务名称">{{ currentTask.title }}</el-descriptions-item>
          <el-descriptions-item label="任务描述">{{ currentTask.description }}</el-descriptions-item>
          <el-descriptions-item label="截止时间">{{ safeFormatDate(currentTask.endTime) }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="startDialogVisible = false">取消</el-button>
          <el-button type="warning" @click="confirmStartTask">确认开始</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 完成任务对话框 -->
    <el-dialog v-model="completeDialogVisible" title="完成任务" width="50%">
      <div v-if="currentTask">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="任务名称">{{ currentTask.title }}</el-descriptions-item>
          <el-descriptions-item label="任务描述">{{ currentTask.description }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ safeFormatDate(currentTask.startTime) }}</el-descriptions-item>
        </el-descriptions>

        <div class="complete-form" style="margin-top: 20px;">
          <el-form :model="completeForm" label-width="100px" :rules="completeRules" ref="completeFormRef">
            <el-form-item label="完成反馈" prop="feedback">
              <el-input
                  v-model="completeForm.feedback"
                  type="textarea"
                  rows="4"
                  placeholder="请输入任务完成情况、遇到的问题或其他反馈"
              />
            </el-form-item>
            <el-form-item label="上传附件">
              <el-upload
                  :http-request="handleFileUpload"
                  multiple
                  :limit="5"
                  :on-exceed="handleExceed"
                  :on-success="handleUploadSuccess"
                  :on-error="handleUploadError"
                  :on-remove="handleRemove"
                  :before-upload="beforeUpload"
                  :file-list="fileList"
                  ref="uploadRef"
              >
                <template #trigger>
                  <el-button type="primary">选择文件</el-button>
                </template>
                <template #tip>
                  <div class="el-upload__tip">
                    可上传任务相关文档、图片等（最多5个文件，每个不超过10MB）
                  </div>
                </template>
              </el-upload>
            </el-form-item>
          </el-form>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="completeDialogVisible = false">取消</el-button>
          <el-button type="success" @click="confirmCompleteTask">提交完成</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, reactive, computed, onMounted} from 'vue';
import {Search, Download} from '@element-plus/icons-vue';
import {ElMessage, ElMessageBox} from 'element-plus';
import {useStore} from 'vuex';
import {
  getTaskList,
  getTaskById,
  updateTask,
  getTaskStep,
  getTaskAttachmentList,
  downloadAttachment,
  reviewFeedback,
  getAllTaskDetailHistoryByUserId,
  getEmployeeTask,
  updateTaskStatus,
  uploadAttachment,
  submitOperationFeedBack
} from '@/http/api/task.js';

// 状态变量
/** 任务列表加载状态标志 */
const loading = ref(false);
/** 历史记录加载状态标志 */
const historyLoading = ref(false);
/** 当前任务列表数据 */
const tasks = ref([]);
/** 历史记录列表数据 */
const historyRecords = ref([]);
/** 控制任务详情对话框的显示状态 */
const detailsVisible = ref(false);
/** 控制接受任务对话框的显示状态 */
const acceptDialogVisible = ref(false);
/** 控制开始任务对话框的显示状态 */
const startDialogVisible = ref(false);
/** 控制完成任务对话框的显示状态 */
const completeDialogVisible = ref(false);
/** 当前选中的任务对象 */
const currentTask = ref(null);
/** 当前激活的标签页 */
const activeTab = ref('myTasks');
/** 搜索框输入值 */
const searchInput = ref('');
/** 状态过滤器的选中值 */
const filterStatus = ref('');
/** 类型过滤器的选中值 */
const filterType = ref('');
/** 日期范围选择器的值 */
const dateRange = ref([]);
/** 文件上传列表 */
const fileList = ref([]);

// 分页
/** 每页显示的任务数量 */
const pageSize = ref(10);
/** 当前任务列表页码 */
const currentPage = ref(1);
/** 任务总数 */
const totalTasks = ref(0);
/** 每页显示的历史记录数量 */
const historyPageSize = ref(10);
/** 当前历史记录页码 */
const historyCurrentPage = ref(1);
/** 历史记录总数 */
const totalHistory = ref(0);

// 存储实例
const store = useStore();

// 任务完成表单
/**
 * 任务完成表单数据对象
 * @property {string} feedback - 完成反馈
 * @property {Array} attachments - 附件列表
 */
const completeForm = reactive({
  feedback: '',
  attachments: []
});

// 表单校验规则
const completeRules = {
  feedback: [
    {required: true, message: '请输入任务完成情况反馈', trigger: 'blur'},
    {min: 5, max: 500, message: '长度在 5 到 500 个字符', trigger: 'blur'}
  ]
};

// 获取状态对应的类型样式
const getStatusType = (status) => {
  switch (status) {
    case '0':     // 待接受
      return 'info';
    case '1':     // 已接受
      return 'primary';
    case '2':     // 进行中
      return 'primary';
    case '3':     // 待审核
      return 'warning';
    case '4':     // 已完成
      return 'success';
    case '5':     // 已驳回
      return 'danger';
    default:
      return 'info';
  }
};

// 获取任务状态标签
const getStatusLabel = (status) => {
  switch (status) {
    case '0':
      return '待接受';
    case '1':
      return '已接受';
    case '2':
      return '进行中';
    case '3':
      return '待审核';
    case '4':
      return '已完成';
    case '5':
      return '已驳回';
    default:
      return '未知状态';
  }
};

// 格式化任务状态
const formatTaskStatus = (status) => {
  return getStatusLabel(status);
};

// 格式化任务类型
const formatTaskType = (type) => {
  switch (type) {
    case '0':
      return '日常巡检';
    case '1':
      return '维修任务';
    case '2':
      return '异常处理';
    case '3':
      return '设备安装';
    default:
      return '其他任务';
  }
};

// 格式化优先级
const formatPriority = (priority) => {
  switch (priority) {
    case '0':
    case 0:
      return '低';
    case '1':
    case 1:
      return '中';
    case '2':
    case 2:
      return '高';
    default:
      return '未知';
  }
};

// 格式化时间
const formatTime = (row, column, cellValue) => {
  return safeFormatDate(cellValue);
};

// 安全格式化日期
const safeFormatDate = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).replace(/\//g, '-');
  } catch (error) {
    return dateString;
  }
};

// 获取任务进度百分比
const getProgressValue = (status) => {
  switch (status) {
    case '0':
      return 0;
    case '1':
      return 25;
    case '2':
      return 50;
    case '3':
      return 100;
    case '4':
      return 100;
    case '5':
      return 50; // 驳回也展示到 进行中 阶段
    default:
      return 0;
  }
};

// 获取任务进度步骤
const getProgressStep = (task) => {
  if (!task) return 0;

  const status = task.status;
  switch (status) {
    case '0':
      return 0;
    case '1':
      return 1;
    case '2':
      return 2;
    case '3':
      return 3;
    case '4':
      return 4;
    case '5':
      return 2; // 驳回停留在 进行中 阶段
    default:
      return 0;
  }
};

// 获取时间轴步骤类型
const getStepType = (status) => {
  switch (status) {
    case '0':
      return '';
    case '1':
      return 'primary';
    case '2':
      return 'primary';
    case '3':
      return 'warning';
    case '4':
      return 'success';
    case '5':
      return 'danger';
    default:
      return '';
  }
};

// 格式化步骤内容
const formatStepContent = (step, task) => {
  switch (step.status) {
    case '0':
      return `任务已创建，待接受`;
    case '1':
      return `${task.assignedToUsername || '您'} 已接受任务`;
    case '2':
      return `${task.assignedToUsername || '您'} 开始执行任务`;
    case '3':
      return `任务已提交，等待审核`;
    case '4':
      return `任务已完成，审核通过`;
    case '5':
      return `任务被驳回，原因：${step.feedback || '无'}`;
    default:
      return `状态更新: ${step.status}`;
  }
};


// 上传文件前检查
const beforeUpload = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10;
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB!');
    return false;
  }
  return true;
};

// 处理文件超出限制
const handleExceed = () => {
  ElMessage.warning('最多只能上传5个文件');
};

// 上传成功处理
const handleUploadSuccess = (response, file, fileList) => {
  ElMessage.success('附件上传成功');
  console.log('上传成功:', response);
  //
};

// 上传失败处理
const handleUploadError = () => {
  ElMessage.error('附件上传失败');
};

// 移除文件处理
const handleRemove = (file, fileList) => {
  const fileUrl = file.response?.data?.url;
  if (fileUrl) {
    completeForm.attachments = completeForm.attachments.filter(
        attachment => attachment.url !== fileUrl
    );
  }
};

// 处理文件上传
const handleFileUpload = async (options) => {
  try {
    const {file, onSuccess, onError} = options;
    console.log('开始上传文件:', file.name, '任务ID:', currentTask.value.id);

    const response = await uploadAttachment(file, currentTask.value.id);
    console.log('上传文件响应:', response);

    if (response.data && response.data.success) {
      onSuccess(response);
      completeForm.attachments.push(response.data);   // 将上传成功的文件添加到任务附件列表中
      ElMessage.success(`文件 ${file.name} 上传成功`);
    } else {
      const errorMsg = response.data?.message || '上传失败';
      console.error('上传失败:', errorMsg);
      onError(new Error(errorMsg));
      ElMessage.error(errorMsg);
    }
  } catch (error) {
    console.error('上传文件异常:', error);
    onError(error);
    ElMessage.error(`文件上传失败: ${error.message}`);
  }
};

// 查看任务详情
const viewTaskDetails = async (row, isHistory = false) => {
  try {
    loading.value = true;
    currentTask.value = row;


    const response = await getTaskById(row.id);
    const response2 = await getTaskStep(row.id);   //获取任务的进度
    const response3 = await getTaskAttachmentList(row.id); //获取任务的附件

    if (response.data.success && response2.data.success && response3.data.success) {
      currentTask.value = {
        ...response.data.data,
        stepList: response2.data.data,
        attachmentList: response3.data.data
      };
      detailsVisible.value = true;
    } else {
      ElMessage.error(response.data.message || '获取任务详情失败');
    }

  } catch (error) {
    console.error('获取任务详情失败:', error);
    ElMessage.error('获取任务详情失败');
  } finally {
    loading.value = false;
  }
};

//下载附件
const downloadAttachmentByid = async (attachment) => {
  try {
    const response = await downloadAttachment(attachment.id);

    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', attachment.name);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    ElMessage.success(`下载附件: ${attachment.name} 成功`);
  } catch (error) {
    console.error('下载附件出错:', error);
    ElMessage.error(`下载附件失败: ${attachment.name}`);
  }
};

// 接受任务   
const acceptTask = (row) => {
  currentTask.value = row;
  acceptDialogVisible.value = true;
};

// 确认接受任务   1.写入status值为1，表示已接受任务  2.将任务表中的status值改为1
const confirmAcceptTask = async () => {
  try {
    if (!currentTask.value) return;

    const response = await updateTaskStatus(currentTask.value.id, '1');  // 更改为已接受状态

    if (response.data.success) {
      ElMessage.success('任务接受成功');
      acceptDialogVisible.value = false;
      // 刷新任务列表
      await fetchTaskList();
    } else {
      ElMessage.error(response?.message || '任务接受失败');
    }
  } catch (error) {
    console.error('接受任务失败:', error);
    ElMessage.error('接受任务失败');
  }
};

// 开始任务
const startTask = (row) => {
  currentTask.value = row;
  startDialogVisible.value = true;
};

// 确认开始任务
const confirmStartTask = async () => {
  try {
    if (!currentTask.value) return;

    const response = await updateTaskStatus(currentTask.value.id, '2');

    if (response.data.success) {
      ElMessage.success('任务已开始');
      startDialogVisible.value = false;
      // 刷新任务列表
      await fetchTaskList();
    } else {
      ElMessage.error(response?.message || '开始任务失败');
    }
  } catch (error) {
    console.error('开始任务失败:', error);
    ElMessage.error('开始任务失败');
  }
};

// 完成任务
const completeTask = (row) => {
  currentTask.value = row;
  completeForm.feedback = '';
  completeForm.attachments = [];
  fileList.value = [];
  completeDialogVisible.value = true;
};

// 确认完成任务
const confirmCompleteTask = async () => {
  try {
    if (!currentTask.value) return;

    // 表单验证
    if (!completeForm.feedback) {
      ElMessage.warning('请填写任务完成反馈');
      return;
    }

    // 修改状态
    const response = await updateTaskStatus(currentTask.value.id, '3');

    // 提交反馈
    const response2 = await submitOperationFeedBack(currentTask.value.id, completeForm.feedback);

    // 上传附件
    let allUploadsSuccessful = true;
    if (fileList.value.length > 0) {
      try {
        console.log('准备上传附件, 数量:', fileList.value.length);

        // 逐个上传文件，避免一次性上传过多
        for (const fileItem of fileList.value) {
          console.log('上传文件:', fileItem.name);
          const uploadResponse = await uploadAttachment(fileItem.raw, currentTask.value.id);

          if (!uploadResponse.data || !uploadResponse.data.success) {
            console.error('文件上传失败:', fileItem.name, uploadResponse.data?.message);
            allUploadsSuccessful = false;
          }
        }

        if (!allUploadsSuccessful) {
          ElMessage.warning('部分附件上传失败，但任务状态已更新');
        }
      } catch (uploadError) {
        console.error('上传附件失败:', uploadError);
        ElMessage.warning('附件上传失败，但任务状态已更新');
      }
    }

    if (response.data.success && response2.data.success) {
      ElMessage.success('任务提交成功，等待审核');
      completeDialogVisible.value = false;
      // 刷新任务列表
      await fetchTaskList();
    } else {
      ElMessage.error(response.data.message || '提交任务失败');
    }
  } catch (error) {
    console.error('提交任务失败:', error);
    ElMessage.error('提交任务失败');
  }
};

// 搜索任务
const handleSearch = () => {
  currentPage.value = 1;
  fetchTaskList();
};

// 重置搜索条件
const resetSearch = () => {
  searchInput.value = '';
  filterStatus.value = '';
  filterType.value = '';
  dateRange.value = [];
  currentPage.value = 1;
  fetchTaskList();
};

// 处理标签页切换
const handleTabClick = (tab) => {
  if (tab.props.name === 'myTasks') {
    fetchTaskList();
  } else if (tab.props.name === 'history') {
    fetchHistoryList();
  }
};

// 分页切换
const handlePageChange = (page) => {
  currentPage.value = page;
  fetchTaskList();
};

// 历史记录分页切换
const handleHistoryPageChange = (page) => {
  historyCurrentPage.value = page;
  fetchHistoryList();
};

// 获取任务列表
const fetchTaskList = async () => {
  try {
    loading.value = true;

    const params = {
      page: currentPage.value,
      size: pageSize.value,
      search: searchInput.value,
      status: filterStatus.value,
      type: filterType.value
    };

    // 添加时间范围筛选并格式化日期
    if (dateRange.value && dateRange.value.length === 2) {
      // 确保日期格式为yyyy-MM-dd
      params.createDate = formatDateToYYYYMMDD(dateRange.value[0]);
      params.endDate = formatDateToYYYYMMDD(dateRange.value[1]);
    }

    const response = await getEmployeeTask(params);

    if (response.data && response.data.success) {
      tasks.value = response.data.data.taskList || [];
      totalTasks.value = response.data.data.total || 0;
    } else {
      ElMessage.error(response.data?.message || '获取任务列表失败');
    }
  } catch (error) {
    console.error('获取任务列表失败:', error);
    ElMessage.error('获取任务列表失败');
  } finally {
    loading.value = false;
  }
};

// 添加日期格式化函数
const formatDateToYYYYMMDD = (date) => {
  if (!date) return null;

  if (typeof date === 'string') {
    // 如果已经是字符串，尝试解析并格式化
    const d = new Date(date);
    return isNaN(d.getTime()) ? date : d.toISOString().slice(0, 10);
  }

  if (date instanceof Date) {
    return date.toISOString().slice(0, 10); // 格式为 YYYY-MM-DD
  }

  return date;
};

// 获取历史记录列表
const fetchHistoryList = async () => {
  try {
    historyLoading.value = true;

    const params = {
      page: historyCurrentPage.value,
      size: historyPageSize.value,
      search: searchInput.value,
      status: filterStatus.value,
      type: filterType.value
    };

    // 添加时间范围筛选
    if (dateRange.value && dateRange.value.length === 2) {
      params.createDate = formatDateToYYYYMMDD(dateRange.value[0]);
      params.endDate = formatDateToYYYYMMDD(dateRange.value[1]);
    }

    const response = await getAllTaskDetailHistoryByUserId(params);

    if (response.data.success) {
      historyRecords.value = response.data.data.taskDetailHistoryList || [];
      totalHistory.value = response.data.data.taskDetailHistoryCount || 0;
    } else {
      ElMessage.error(response.data.message || '获取历史记录失败');
    }
  } catch (error) {
    console.error('获取历史记录失败:', error);
    ElMessage.error('获取历史记录失败');
  } finally {
    historyLoading.value = false;
  }
};

// 生命周期钩子 - 组件挂载时获取数据
onMounted(() => {
  fetchTaskList();
});
</script>

<style scoped>
.employee-task-container {
  padding: 20px;
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.page-title {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 2%;
  height: 5%;
  color: #303133;
  border-left: 4px solid #409eff;
  padding-left: 15px;
}

.action-bar {
  display: flex;
  align-items: center;
  height: 5%;
  margin-bottom: 2%;
  flex-wrap: wrap;
  gap: 10px;
}

.search-input {
  width: 220px;
  margin-right: 15px;
}

.filter-select {
  width: 130px;
  margin-right: 15px;
}

.date-picker {
  width: 260px;
  margin-right: 15px;
}

.list {
  flex: 1;
  height: 80%;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.tabs-header {
  height: 5%;
  margin-bottom: 2%;
}

/* 优化Element Plus标签显示 */
:deep(.el-tabs__nav-wrap) {
  padding: 0 10px;
}

:deep(.el-tabs__content) {
  display: none; /* 隐藏原始content，因为使用自定义布局 */
}

.tabs-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tab-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: auto;
}

.table-form {
  width: 100%;
  height: 100%;
  margin-bottom: 10px;
}

.pagination {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
  padding: 8px;
}

/* 任务详情样式 */
.task-progress-section,
.task-feedback-section,
.task-history-section,
.task-attachments-section {
  margin-top: 30px;
}

.task-progress-section h3,
.task-feedback-section h3,
.task-history-section h3,
.task-attachments-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
  color: #303133;
  border-left: 3px solid #409eff;
  padding-left: 10px;
}

.feedback-card {
  margin-top: 10px;
  background-color: #f9f9f9;
}

.attachment-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.attachment-tag {
  display: flex;
  align-items: center;
  padding: 8px 12px;
}

.attachment-tag .el-icon {
  margin-left: 8px;
  cursor: pointer;
}

.review-comment {
  margin-top: 10px;
  color: #606266;
  font-size: 14px;
  background-color: #f5f7fa;
  padding: 8px 12px;
  border-radius: 4px;
}

/* 响应式样式调整 */
@media screen and (max-width: 1200px) {
  .action-bar {
    gap: 8px;
  }

  .search-input,
  .filter-select,
  .date-picker {
    margin-right: 8px;
  }

  .date-picker {
    width: 220px;
  }
}

@media screen and (max-width: 768px) {
  .action-bar {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-input,
  .filter-select,
  .date-picker {
    width: 100%;
    margin-right: 0;
    margin-bottom: 10px;
  }
}

/* 确保Element UI表格正确渲染 */
:deep(.el-table__inner-wrapper) {
  height: 100%;
}

:deep(.el-table__body-wrapper) {
  overflow-y: auto;
}
</style>