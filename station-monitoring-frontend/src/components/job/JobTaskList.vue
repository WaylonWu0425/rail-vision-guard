<template>
  <div class="task-list">
    <div class="task-search">
      <el-input
        v-model="searchQuery"
        placeholder="搜索任务..."
        clearable
        prefix-icon="Search"
      />
      <el-select v-model="statusFilter" placeholder="状态筛选" clearable>
        <el-option label="待处理" value="pending" />
        <el-option label="进行中" value="in-progress" />
        <el-option label="已完成" value="completed" />
        <el-option label="已驳回" value="rejected" />
      </el-select>
      <el-select v-model="typeFilter" placeholder="类型筛选" clearable>
        <el-option label="维护" value="维护" />
        <el-option label="安装" value="安装" />
        <el-option label="检查" value="检查" />
        <el-option label="配置" value="配置" />
      </el-select>
    </div>

    <el-table 
      :data="filteredTasks" 
      style="width: 100%"
      v-loading="loading"
      border
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="任务标题" min-width="160" />
      <el-table-column prop="description" label="任务描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="type" label="类型" width="100" />
      <el-table-column label="优先级" width="100">
        <template #default="scope">
          <el-tag 
            :type="getPriorityType(scope.row.priority)" 
            effect="dark"
          >
            {{ getPriorityLabel(scope.row.priority) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag 
            :type="getStatusType(scope.row.status)" 
            effect="plain"
          >
            {{ getStatusLabel(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="截止日期" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.dueDate) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button 
            type="primary" 
            size="small" 
            @click="$emit('view-task', scope.row)"
            icon="View"
            link
          >
            查看
          </el-button>
          
          <!-- 员工操作按钮 -->
          <template v-if="!isAdmin && scope.row.status !== 'completed' && scope.row.status !== 'rejected'">
            <el-button 
              v-if="scope.row.status === 'pending'" 
              type="success" 
              size="small" 
              @click="handleStatusChange(scope.row, 'in-progress')"
              link
            >
              开始
            </el-button>
            <el-button 
              v-if="scope.row.status === 'in-progress'" 
              type="warning" 
              size="small" 
              @click="handleStatusChange(scope.row, 'pending')"
              link
            >
              暂停
            </el-button>
            <el-button 
              v-if="scope.row.status === 'in-progress'" 
              type="info" 
              size="small" 
              @click="handleComplete(scope.row)"
              link
            >
              完成
            </el-button>
          </template>
          
          <!-- 管理员操作按钮 -->
          <template v-if="isAdmin">
            <el-button 
              type="warning" 
              size="small" 
              @click="$emit('edit-task', scope.row)"
              icon="Edit"
              link
            >
              编辑
            </el-button>
            <el-dropdown trigger="click">
              <el-button 
                type="danger" 
                size="small" 
                link
              >
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$emit('delete-task', scope.row.id)">删除</el-dropdown-item>
                  <el-dropdown-item 
                    v-if="scope.row.status === 'in-progress'"
                    @click="handleReview(scope.row, true)"
                  >
                    审核通过
                  </el-dropdown-item>
                  <el-dropdown-item 
                    v-if="scope.row.status === 'in-progress'"
                    @click="handleReview(scope.row, false)"
                  >
                    审核不通过
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <!-- 状态更新对话框 -->
    <el-dialog
      v-model="statusDialogVisible"
      title="更新任务状态"
      width="30%"
      destroy-on-close
    >
      <el-form>
        <el-form-item label="反馈信息">
          <el-input
            v-model="feedbackText"
            type="textarea"
            rows="4"
            placeholder="输入任务反馈内容..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span>
          <el-button @click="statusDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmStatusUpdate">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 审核对话框 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="isApproved ? '审核通过' : '审核不通过'"
      width="30%"
      destroy-on-close
    >
      <el-form>
        <el-form-item label="审核意见">
          <el-input
            v-model="reviewFeedback"
            type="textarea"
            rows="4"
            placeholder="输入审核意见..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span>
          <el-button @click="reviewDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmReview">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Search, View, Edit, ArrowDown } from '@element-plus/icons-vue';

// 属性定义
const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  },
  isAdmin: {
    type: Boolean,
    default: false
  }
});

// 事件定义
const emit = defineEmits([
  'view-task', 
  'edit-task', 
  'delete-task', 
  'update-status',
  'review-task'
]);

// 状态
const loading = ref(false);
const searchQuery = ref('');
const statusFilter = ref('');
const typeFilter = ref('');

// 状态更新弹窗
const statusDialogVisible = ref(false);
const feedbackText = ref('');
const currentTask = ref(null);
const newStatus = ref('');

// 审核弹窗
const reviewDialogVisible = ref(false);
const reviewFeedback = ref('');
const taskToReview = ref(null);
const isApproved = ref(true);

// 过滤后的任务列表
const filteredTasks = computed(() => {
  let result = props.tasks;
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(task => 
      task.title.toLowerCase().includes(query) || 
      task.description.toLowerCase().includes(query)
    );
  }
  
  // 状态过滤
  if (statusFilter.value) {
    result = result.filter(task => task.status === statusFilter.value);
  }
  
  // 类型过滤
  if (typeFilter.value) {
    result = result.filter(task => task.type === typeFilter.value);
  }
  
  return result;
});

// 状态颜色映射
const getStatusType = (status) => {
  const map = {
    'pending': 'info',
    'in-progress': 'warning',
    'completed': 'success',
    'rejected': 'danger'
  };
  return map[status] || 'info';
};

// 状态标签映射
const getStatusLabel = (status) => {
  const map = {
    'pending': '待处理',
    'in-progress': '进行中',
    'completed': '已完成',
    'rejected': '已驳回'
  };
  return map[status] || '未知';
};

// 优先级颜色映射
const getPriorityType = (priority) => {
  const map = {
    'low': 'info',
    'medium': 'warning',
    'high': 'danger'
  };
  return map[priority] || 'info';
};

// 优先级标签映射
const getPriorityLabel = (priority) => {
  const map = {
    'low': '低',
    'medium': '中',
    'high': '高'
  };
  return map[priority] || '未知';
};

// 日期格式化
const formatDate = (dateString) => {
  if (!dateString) return '无截止日期';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 处理状态更改
const handleStatusChange = (task, status) => {
  currentTask.value = task;
  newStatus.value = status;
  statusDialogVisible.value = true;
};

// 处理任务完成
const handleComplete = (task) => {
  currentTask.value = task;
  newStatus.value = 'completed';
  statusDialogVisible.value = true;
};

// 确认状态更新
const confirmStatusUpdate = () => {
  if (currentTask.value) {
    emit('update-status', {
      taskId: currentTask.value.id,
      status: newStatus.value,
      feedback: feedbackText.value
    });
    statusDialogVisible.value = false;
    feedbackText.value = '';
  }
};

// 处理审核
const handleReview = (task, approved) => {
  taskToReview.value = task;
  isApproved.value = approved;
  reviewDialogVisible.value = true;
};

// 确认审核
const confirmReview = () => {
  if (taskToReview.value) {
    emit('review-task', {
      taskId: taskToReview.value.id,
      approved: isApproved.value,
      feedback: reviewFeedback.value
    });
    reviewDialogVisible.value = false;
    reviewFeedback.value = '';
  }
};
</script>

<style scoped>
.task-list {
  width: 100%;
}

.task-search {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.el-input {
  max-width: 250px;
}

.el-select {
  width: 150px;
}
</style> 