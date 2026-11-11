<template>
  <div class="job-management-container">
    <div class="page-title">作业内容管理</div>
    
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
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <span>筛选：</span>
      
      <el-select v-model="filterStatus" placeholder="任务状态" clearable class="filter-select">
        <el-option label="待分配" value="0" />
        <el-option label="已接受" value="1" />
        <el-option label="进行中" value="2" />
        <el-option label="待审核" value="3" />
        <el-option label="已完成" value="4" />
        <el-option label="已驳回" value="5" />
      </el-select>
      
      <el-select v-model="filterType" placeholder="任务类型" clearable class="filter-select">
        <el-option label="日常巡检" value="0" />
        <el-option label="维修任务" value="1" />
        <el-option label="异常处理" value="2" />
        <el-option label="设备安装" value="3" />
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
      <el-button type="primary" @click="dialogVisible = true">创建新任务</el-button>
    </div>
    
    <!-- 任务列表/表格 -->
    <div class="list">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="table">
        <el-tab-pane label="任务管理" name="tasks" class="tab-form">
          <el-table :data="tasks" style="width: 100%" v-loading="loading" class="table-form">
            <el-table-column fixed prop="id" label="序号" min-width="60" align="center">
                <template #default="{ $index }">
                {{ $index + 1 }}
                </template>
            </el-table-column>
            <el-table-column prop="title" label="任务名称" min-width="150" align="center"/>
            <el-table-column prop="description" label="任务描述" min-width="200" show-overflow-tooltip align="center"/>
            <el-table-column prop="assignedToUsername" label="执行人" min-width="120" align="center"/>
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
            <el-table-column prop="endTime" label="结束时间" min-width="160" :formatter="formatTime" align="center"/>
            <el-table-column label="进度" min-width="120" align="center">
              <template #default="scope">
                <!-- 如果审核完成且通过才显示成功对勾 -->
                <el-progress 
                  :percentage="getProgressValue(scope.row.status)" 
                  :status="scope.row.status == '4' ? 'success' : ''"    
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="220" align="center">
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
                  @click="editTask(scope.row)"
                  v-if="scope.row.status !== '4'" 
                  type="warning" 
                  plain
                >
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="success" 
                  plain
                  v-if="scope.row.status == '3'"
                  @click="reviewTask(scope.row)"
                >
                  审核
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
        </el-tab-pane>
        
        <el-tab-pane label="历史记录" name="history" style="height: 100%;">
          <el-table :data="historyRecords" v-loading="historyLoading" style="width: 100%;height: 92%;">
            <el-table-column prop="historyId" label="记录ID" min-width="80" align="center" />
            <el-table-column prop="taskId" label="任务ID" min-width="80" align="center" />
            <el-table-column prop="title" label="任务名称" min-width="150" align="center" />
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
            <el-table-column prop="statusTime" label="操作时间" min-width="160" align="center" :formatter="formatTime" />
            <el-table-column prop="feedback" label="反馈" min-width="180" align="center" />
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
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 创建新任务对话框 -->
    <el-dialog v-model="dialogVisible" title="创建新任务" width="50%">
      <el-form :model="newTask" label-width="100px" :rules="taskRules" ref="taskForm">
        <el-form-item label="任务名称" prop="title">
          <el-input v-model="newTask.title" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input 
            v-model="newTask.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入任务描述"
          />
        </el-form-item>
        <el-form-item label="任务类型" prop="type">
          <el-select v-model="newTask.type" placeholder="请选择任务类型">
            <el-option label="日常巡检" value="0" />
            <el-option label="维修任务" value="1" />
            <el-option label="异常处理" value="2" />
            <el-option label="设备安装" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行人" prop="assignedToId">
          <el-select v-model="newTask.assignedToId" placeholder="请选择执行人">
            <el-option 
              v-for="user in availableUsers" 
              :key="user.id" 
              :label="user.username" 
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="newTask.priority" placeholder="请选择优先级">
            <el-option label="高" value="2" />
            <el-option label="中" value="1" />
            <el-option label="低" value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期" prop="endTime">
          <el-date-picker
            v-model="newTask.endTime"
            type="datetime"
            placeholder="选择截止日期时间"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitTask">创建</el-button>
        </span>
      </template>
    </el-dialog>
    
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
          <el-descriptions-item label="执行人">{{ currentTask.assignedToUsername }}</el-descriptions-item>
          <el-descriptions-item label="审核人员">{{ currentTask.dealByUsername }}</el-descriptions-item>
          <el-descriptions-item label="开始时间" :span="2">{{ safeFormatDate(currentTask.startTime) || '尚未开始' }}</el-descriptions-item>
          <el-descriptions-item label="完成时间" :span="2">{{ safeFormatDate(currentTask.finishTime) || '尚未完成' }}</el-descriptions-item>
          <el-descriptions-item label="任务描述" :span="2">{{ currentTask.description }}</el-descriptions-item>
          <el-descriptions-item label="操作反馈" :span="2">{{ currentTask.operationFeedback || '暂无反馈' }}</el-descriptions-item>
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
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="task-progress-section">
          <h3>任务进度</h3>
          <el-steps :active="getProgressStep(currentTask)" finish-status="success">
            <el-step title="已创建" :description="safeFormatDate(currentTask.createTime)" />
            <el-step title="进行中" :description="safeFormatDate(currentTask.startTime)" />
            <el-step title="待审核" :description="safeFormatDate(currentTask.finishTime)" />
            <el-step title="已完成" :description="safeFormatDate(currentTask.dealTime)" />
          </el-steps>
        </div>
        
        <div class="task-feedback-section" v-if="currentTask.operationFeedback">
          <h3>执行反馈</h3>
          <el-card class="feedback-card">
            <p>{{ currentTask.operationFeedback }}</p>
            <div v-if="currentTask.attachmentList && currentTask.attachmentList.length">
              <h4>附件：</h4>
              <div class="attachment-list">
                <el-tag v-for="(attachment, index) in currentTask.attachmentList" :key="index" class="attachment-tag">
                  {{ attachment.name }}
                  <el-icon @click="downloadAttachmentByid(attachment)"><Download /></el-icon>
                </el-tag>
              </div>
            </div>
          </el-card>
        </div>
        
        <div class="task-history-section">
          <h3>操作历史</h3>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in currentTask.stepList"
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
    
    <!-- 任务审核对话框 -->
    <el-dialog v-model="reviewVisible" title="任务审核" width="50%">
      <div v-if="currentTask">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="任务名称">{{ currentTask.title }}</el-descriptions-item>
          <el-descriptions-item label="任务描述">{{ currentTask.description }}</el-descriptions-item>
          <el-descriptions-item label="执行人">{{ currentTask.assignedToUsername }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ safeFormatDate(currentTask.finishTime) }}</el-descriptions-item>
          <el-descriptions-item label="执行反馈">{{ currentTask.operationFeedback || '无反馈' }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="review-form">
          <h3>审核意见</h3>
          <el-form :model="reviewForm" label-width="100px">
            <el-form-item label="审核结果">
              <el-radio-group v-model="reviewForm.result">
                <el-radio :label="4">通过</el-radio>
                <el-radio :label="5">驳回</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="审核意见" v-if="reviewForm.result == '5'">
              <el-input 
                v-model="reviewForm.comment" 
                type="textarea" 
                rows="3"
                placeholder="请输入驳回原因及修改建议"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="reviewVisible = false">取消</el-button>
          <el-button type="primary" @click="submitReview">提交审核</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { Search, Download } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getAllUser } from '@/http/api/user.js';
import { getTaskList, createTask, getTaskById, updateTask, getTaskStep, getTaskAttachmentList, downloadAttachment, reviewFeedback, getAllTaskDetailHistory } from '@/http/api/task.js';
import { getCurrentInstance } from 'vue';


// 状态变量
/** 任务列表加载状态标志，控制列表加载指示器显示 */
const loading = ref(false);
/** 历史记录加载状态标志，控制历史列表加载指示器显示 */
const historyLoading = ref(false);
/** 当前任务列表数据，包含所有任务信息 */
const tasks = ref([]);
/** 历史记录列表数据，包含已完成或已驳回的任务 */
const historyRecords = ref([]);
/** 控制新建/编辑任务对话框的显示状态 */
const dialogVisible = ref(false);
/** 控制任务详情对话框的显示状态 */
const detailsVisible = ref(false);
/** 控制任务审核对话框的显示状态 */
const reviewVisible = ref(false);
/** 当前选中的任务对象，用于详情查看、编辑和审核 */
const currentTask = ref(null);
/** 当前激活的标签页，可选值为'tasks'或'history' */
const activeTab = ref('tasks');
/** 搜索框输入值，用于任务名称、描述和执行人搜索 */
const searchInput = ref('');
/** 状态过滤器的选中值，用于按任务状态筛选 */
const filterStatus = ref('');
/** 类型过滤器的选中值，用于按任务类型筛选 */
const filterType = ref('');
/** 日期范围选择器的值，包含开始日期和结束日期 */
const dateRange = ref([]);

// 分页
/** 每页显示的任务数量 */
const pageSize = ref(10);
/** 当前任务列表页码 */
const currentPage = ref(1);
/** 任务总数，用于分页计算 */
const totalTasks = ref(0);
/** 每页显示的历史记录数量 */
const historyPageSize = ref(10);
/** 当前历史记录页码 */
const historyCurrentPage = ref(1);
/** 历史记录总数，用于分页计算 */
const totalHistory = ref(0);

// 新任务表单
/** 
 * 新建/编辑任务的表单数据对象
 * @property {string} title - 任务名称
 * @property {string} description - 任务描述
 * @property {string} type - 任务类型，如日常巡检、维修任务等
 * @property {string} assignedToId - 任务执行人
 * @property {string} priority - 任务优先级，可选值为'高'、'中'、'低'
 * @property {Date} endTime - 任务截止日期
 */
const newTask = reactive({
  title: '',
  description: '',
  type: '',
  assignedToId: '',
  priority: '',
  endTime: ''
});

// 审核表单
/**
 * 任务审核表单数据对象
 * @property {string} result - 审核结果，0为通过，1为驳回
 * @property {string} comment - 审核意见，驳回时必填
 */
const reviewForm = reactive({
  result: '4',
  comment: ''
});

// 表单验证规则
const taskRules = {
  title: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入任务描述', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择任务类型', trigger: 'change' }
  ],
  assignee: [
    { required: true, message: '请选择执行人', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
};

// 可用用户列表
/** 可选的任务执行人列表，从服务器获取 */
const availableUsers = ref([]);

// 获取状态对应的类型样式
const getStatusType = (status) => {
  switch (status) {
    case '0':     //待分配
      return 'info';
    case '1':     //已接受
      return 'primary';
    case '2':     //进行中
      return 'primary';
    case '3':     //待审核
      return 'warning';
    case '4':     //审核完成
      return 'success';
    case '5':     //驳回
      return 'danger';
    default:
      return 'info';
  }
};
//任务状态信息
const getStatusLabel = (status) => {
  switch (status) {
    case '0':
      return '待分配';
    case '1':
      return '已接受';
    case '2':
      return '进行中';
    case '3':
      return '待审核';
    case '4':
      return '已完成';
    case '5':
      return '驳回';
    default:
      return '未知';
  }
};

//进度条数字展示
const getProgressValue = (status) => {
  switch (status) {
    case '0': // 待分配
    return 0;
    case '1': // 已接受
      return 25;
    case '2': // 进行中
    case '5': // 已驳回
      return 75;
    case '3': // 待审核
    case '4': // 已完成（审核完成）
      return 100;
    default:
      return 0;
  }
};

// 获取进度状态步骤
const getProgressStep = (task) => {
  switch (task.status) {
    case '0':
      return 1;
    case '1':
    case '2':
      return 2;
    case '3':
      return 3;
    case '4':
      return 4;
    case '5':
      return 2; // 驳回时回到进行中状态
    default:
      return 1;
  }
};

// 操作历史状态映射
const statusMap = {
  '0': { label: '已创建任务', type: 'info' },
  '1': { label: '已接受任务', type: 'primary' },
  '3': { label: '已完成任务', type: 'primary' },
  '4': { label: '任务审核通过', type: 'success' },
  '5': { label: '审核未通过', type: 'danger' }
};

// 格式化操作历史内容
const formatStepContent = (step, currentTask) => {
  let content = '';
  // 根据status选择不同的用户名
  let userName = '';
  if (step.status == '0') {
    userName = currentTask.createByUsername || '';
  } else if (step.status == '1') {
    userName = currentTask.assignedToUsername || '';
  } else if (step.status == '4' || step.status == '5') {
    userName = currentTask.dealByUsername || '';
  } else {
    // 其它情况可自定义
    userName = step.dealByUsername || step.username || currentTask.dealByUsername || currentTask.assignedToUsername || '';
  }
  // 状态文字
  const statusInfo = statusMap[step.status] || { label: '未知状态', type: 'info' };
  content += statusInfo.label;
  // if (userName) content += `${userName}`;
  if (userName) content = `${userName}` + content;
  // 审核未通过时，显示审核意见
  if (step.status == '5' && currentTask.reviewFeedback) {
    content += `，审核意见：${currentTask.reviewFeedback}`;
  }
  return content;
};

// timeline颜色
const getStepType = (status) => {
  return statusMap[status]?.type || 'info';
};

// 格式化任务类型显示
const formatTaskType = (type) => {
  const typeMap = {
    '0': '日常巡检',
    '1': '维修任务',
    '2': '异常处理',
    '3': '设备安装'
  };
  return typeMap[type] || type;
};

// 格式化任务状态显示
const formatTaskStatus = (status) => {
  const statusMap = {
    '0': '待分配',
    '1': '已接受',
    '2': '进行中',
    '3': '待审核',
    '4': '已完成',
    '5': '已驳回'
  };
  return statusMap[status] || status;
};

// 格式化优先级显示
const formatPriority = (priority) => {
  const priorityMap = {
    '0': '低',
    '1': '中',
    '2': '高'
  };
  return priorityMap[priority] || priority;
};


// 修改分页后的任务列表
const paginatedTasks = computed(() => {
  return tasks.value;
});

// 修改分页后的历史记录
const paginatedHistory = computed(() => {
  return historyRecords.value;
});

// 添加搜索处理函数
const handleSearch = () => {
  currentPage.value = 1; // 重置页码
  fetchTasks();
  if (activeTab.value === 'history') {
    historyCurrentPage.value = 1;
    fetchHistoryRecords();
  }
};

// 修改重置搜索函数
const resetSearch = () => {
  searchInput.value = '';
  filterStatus.value = '';
  filterType.value = '';
  dateRange.value = [];
  currentPage.value = 1;
  historyCurrentPage.value = 1;
  fetchTasks();
  if (activeTab.value === 'history') {
    fetchHistoryRecords();
  }
};

// 修改标签页切换处理函数
const handleTabClick = (tab) => {
  if (tab.props.name === 'tasks') {
    fetchTasks();
  } else {
    fetchHistoryRecords();
  }
};

// 修改分页变化处理函数
const handlePageChange = (page) => {
  currentPage.value = page;
  fetchTasks();
};

// 修改历史记录分页变化处理函数
const handleHistoryPageChange = (page) => {
  historyCurrentPage.value = page;
  fetchHistoryRecords();
};

// 查看任务详情
const viewTaskDetails = async (task, isFromHistory = false) => {
  try {
    loading.value = true;
    // 根据来源选择正确的ID
    const taskId = isFromHistory ? task.taskId : task.id;
    
    const response = await getTaskById(taskId);
    const response2 = await getTaskStep(taskId);   //获取任务的进度
    const response3 = await getTaskAttachmentList(taskId); //获取任务的附件
    
    if (response.data.success&&response2.data.success&&response3.data.success) {
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
    console.error('获取任务详情出错:', error);
    ElMessage.error('获取任务详情失败');
  } finally {
    loading.value = false;
  }
};


// 编辑任务
const editTask = async (task) => {
  try {
    loading.value = true;
    const response = await getTaskById(task.id);
    if (response.data.success) {
      currentTask.value = response.data.data;
      //将currentTask.value的值赋值给newTask，
      Object.assign(newTask, {
        title: currentTask.value.title,
        description: currentTask.value.description,
        type: currentTask.value.type,
        assignedToId: currentTask.value.assignedToId,
        priority: currentTask.value.priority,
        endTime: currentTask.value.endTime
      });
      dialogVisible.value = true;
    } else {
      ElMessage.error(response.data.message || '获取任务详情失败');
    }
  } catch (error) {
    console.error('获取任务详情出错:', error);
    ElMessage.error('获取任务详情失败');
  } finally {
    loading.value = false;
  }
};

// 审核任务
const reviewTask = (task) => {
  currentTask.value = task;
  reviewForm.result = '4';
  reviewForm.comment = '';
  reviewVisible.value = true;
};

// 提交审核结果
const submitReview = async () => {
  if (reviewForm.result == '5' && !reviewForm.comment) {
    ElMessage.warning('请填写驳回原因');
    return;
  }
  
  try {
    loading.value = true;
    
    const response = await reviewFeedback(currentTask.value.id, reviewForm.result, reviewForm.comment);
    
    if (response.data.success) {
      if (reviewForm.result == '4') {
        ElMessage.success('任务已审核通过');
      } else {
        ElMessage.warning('任务已驳回');
      }
      reviewVisible.value = false;
      fetchTasks(); // 刷新任务列表
    } else {
      ElMessage.error(response.data.message || '审核任务失败');
    }
  } catch (error) {
    console.error('审核任务出错:', error);
    ElMessage.error('审核任务失败');
  } finally {
    loading.value = false;
  }
};

// 提交任务（编辑任务 + 新增任务）
const submitTask = async () => {
  try {
    loading.value = true;
    
    let response;
    //如果task.id为空，则创建新任务，否则编辑任务
    if (currentTask.value) {
      // 编辑任务
      const params = {
        id: currentTask.value.id,
        title: newTask.title,
        description: newTask.description,
        type: newTask.type,
        assigned_to_id: newTask.assignee,
        priority: newTask.priority,
        end_time: newTask.deadline
      };
      
      response = await updateTask(params);
    } else {
      // 创建新任务
      const params = {
        title: newTask.title,
        description: newTask.description,
        type: newTask.type,
        assignedToId: newTask.assignedToId,
        priority: newTask.priority,
        endTime: newTask.endTime
      };
      
      response = await createTask(params);
    }
    
    if (response.data.success) {
      ElMessage.success(currentTask.value ? '任务更新成功' : '任务创建成功');
      
      // 重置表单
      currentTask.value = null;
      Object.assign(newTask, {
        title: '',
        description: '',
        type: '',
        assignedToId: '',
        priority: '', // 默认优先级为中
        endTime: ''
      });
      
      dialogVisible.value = false;
      fetchTasks(); // 刷新任务列表
    } else {
      ElMessage.error(response.data.message || (currentTask.value ? '更新任务失败' : '创建任务失败'));
    }
  } catch (error) {
    console.error(currentTask.value ? '更新任务出错:' : '创建任务出错:', error);
    ElMessage.error(currentTask.value ? '更新任务失败' : '创建任务失败');
  } finally {
    loading.value = false;
  }
};

// 下载附件
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

// 获取任务列表
const fetchTasks = async () => {
  try {
    loading.value = true;
    
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      search: searchInput.value,
      status: filterStatus.value,
      type: filterType.value,
      startDate: dateRange.value && dateRange.value[0] ? dateRange.value[0] : null,
      endDate: dateRange.value && dateRange.value[1] ? dateRange.value[1] : null
    };
    const response = await getTaskList(params);
    
    if (response.data.success) {
      tasks.value = response.data.data.taskList;
      totalTasks.value = response.data.data.total;
    } else {
      ElMessage.error(response.data.message);
    }
  } catch (error) {
    console.error('获取任务列表出错:', error);
    ElMessage.error('获取任务列表失败');
  } finally {
    loading.value = false;
  }
};

// 获取历史记录列表
const fetchHistoryRecords = async () => {
  try {
    historyLoading.value = true;
    const params = {
      page: historyCurrentPage.value,
      size: historyPageSize.value,
      search: searchInput.value,
      type: filterType.value,
      status: filterStatus.value,
      startDate: dateRange.value && dateRange.value[0] ? dateRange.value[0] : null,
      endDate: dateRange.value && dateRange.value[1] ? dateRange.value[1] : null
    };
    const response = await getAllTaskDetailHistory(params);
    if (response.data && response.data.data) {
      historyRecords.value = response.data.data.taskDetailHistoryList;
      totalHistory.value = response.data.data.taskDetailHistoryCount;
    } else {
      ElMessage.error(response.data.message || '获取历史记录失败');
    }
  } catch (error) {
    console.error('获取历史记录出错:', error);
    ElMessage.error('获取历史记录失败');
  } finally {
    historyLoading.value = false;
  }
};

// 获取可用用户列表
const fetchAvailableUsers = async () => {
  try {
    const response = await getAllUser();
    if (response.data.success) {
      availableUsers.value = response.data.data;
    } else {
      ElMessage.error(response.data.message || '获取用户列表失败');
    }
  } catch (error) {
    console.error('获取用户列表出错:', error);
    ElMessage.error('获取用户列表失败');
  }
};

// 获取全局 `formatDate` 方法
const { appContext } = getCurrentInstance();
const formatDate = appContext.config.globalProperties.$formatDate;

// 定义格式化方法
const formatTime = (row, column, cellValue) => {
  if (!cellValue) return '';
  const result = formatDate(cellValue, 'YYYY-MM-DD HH:mm:ss');
  if (!result || result.includes('NaN')) return '';
  return result;
};

const safeFormatDate = (date) => {
  if (!date) return '';
  const result = formatDate(date, 'YYYY-MM-DD HH:mm:ss');
  // 如果格式化后依然是无效值（如NaN），也返回空
  if (!result || result.includes('NaN')) return '';
  return result;
};

// 页面加载时获取数据
onMounted(() => {
  fetchTasks();
  fetchAvailableUsers();
});
</script>

<style scoped>
.job-management-container {
  width: 100%;
  height: 100%;
  min-height: 0;
  padding: 24px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: #f3f7fc;
  overflow: auto;
}

.page-title {
  margin: 0;
  height: auto;
  font-size: 23px;
  font-weight: 700;
  color: #15395d;
}

.action-bar {
  min-height: 60px;
  height: auto;
  margin: 0;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  width: 100%;
  padding: 12px 16px;
  box-sizing: border-box;
  border: 1px solid #dbe6f2;
  border-radius: 10px;
  background: #fff;
}
.list {
  width: 100%;
  flex: 1;
  min-height: 420px;
  height: auto;
  border: 1px solid #dbe6f2;
  border-radius: 10px;
  background: #fff;
  padding: 8px 16px 16px;
  box-sizing: border-box;
}
.table {
  height: 100%;
}
.tab-form {
  height: 100%; 
}
.table-form {
  height: 92%;
}

.table-form2 {
  height: 92%;
}
.search-input {
  width: 180px;
  flex-shrink: 0;
}

.filter-select {
  width: 120px;
  flex-shrink: 0;
}

.date-picker {
  width: 300px;
  flex-shrink: 0;
}
.pagination {
  margin-top: 13px;
  display: flex;
  justify-content: flex-end;
  height: 4%;
}

.task-progress-section, 
.task-feedback-section, 
.task-history-section {
  margin-top: 25px;
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
}

.task-progress-section h3, 
.task-feedback-section h3, 
.task-history-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
  color: #606266;
}

.feedback-card {
  background-color: #f8f9fa;
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
  gap: 5px;
  cursor: pointer;
}

.history-filters {
  margin-bottom: 20px;
  display: flex;
  gap: 15px;
}

.review-form {
  margin-top: 20px;
}

.review-form h3 {
  margin-bottom: 15px;
  font-size: 16px;
  color: #606266;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .action-bar {
    flex-direction: row;
    align-items: center;
    overflow-x: auto;
    padding-bottom: 5px;
  }
  
  .search-input,
  .filter-select,
  .date-picker {
    width: auto;
    margin-bottom: 0;
  }
}
</style>
