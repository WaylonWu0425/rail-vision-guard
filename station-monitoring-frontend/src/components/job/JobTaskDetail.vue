<template>
  <el-dialog
    v-model="dialogVisible"
    title="任务详情"
    width="60%"
    destroy-on-close
  >
    <template v-if="task">
      <el-descriptions title="基本信息" :column="2" border>
        <el-descriptions-item label="任务ID">{{ task.id }}</el-descriptions-item>
        <el-descriptions-item label="任务标题">{{ task.title }}</el-descriptions-item>
        <el-descriptions-item label="任务类型">{{ task.type }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityType(task.priority)" effect="dark">
            {{ getPriorityLabel(task.priority) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(task.status)" effect="plain">
            {{ getStatusLabel(task.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(task.createdAt) }}</el-descriptions-item>
        <el-descriptions-item label="开始时间" :span="task.startTime ? 1 : 2">
          {{ task.startTime ? formatDate(task.startTime) : '尚未开始' }}
        </el-descriptions-item>
        <el-descriptions-item v-if="task.endTime" label="结束时间">
          {{ formatDate(task.endTime) }}
        </el-descriptions-item>
        <el-descriptions-item label="截止日期">{{ formatDate(task.dueDate) }}</el-descriptions-item>
        <el-descriptions-item label="任务描述" :span="2">{{ task.description }}</el-descriptions-item>
      </el-descriptions>

      <!-- 任务操作区域 -->
      <div class="task-actions">
        <h3>任务操作</h3>
        
        <!-- 员工操作按钮 -->
        <div v-if="!isAdmin && task.status !== 'completed' && task.status !== 'rejected'" class="action-buttons">
          <el-button 
            v-if="task.status === 'pending'" 
            type="success" 
            @click="handleStatusChange('in-progress')"
          >
            开始任务
          </el-button>
          <el-button 
            v-if="task.status === 'in-progress'" 
            type="warning" 
            @click="handleStatusChange('pending')"
          >
            暂停任务
          </el-button>
          <el-button 
            v-if="task.status === 'in-progress'" 
            type="primary" 
            @click="handleStatusChange('completed')"
          >
            完成任务
          </el-button>
        </div>
        
        <!-- 管理员审核按钮 -->
        <div v-if="isAdmin && task.status === 'completed'" class="action-buttons">
          <el-button type="success" @click="handleReview(true)">审核通过</el-button>
          <el-button type="danger" @click="handleReview(false)">审核不通过</el-button>
        </div>
        
        <!-- 添加反馈表单 -->
        <el-form v-if="task.status !== 'rejected' && task.status !== 'completed' || (isAdmin && task.status === 'completed')">
          <el-form-item label="添加反馈">
            <el-input
              v-model="feedbackText"
              type="textarea"
              rows="3"
              placeholder="输入反馈信息..."
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitFeedback">提交反馈</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 任务历史记录 -->
      <div class="task-history">
        <h3>历史记录</h3>
        <el-timeline>
          <el-timeline-item
            v-for="(record, index) in sortedHistory"
            :key="index"
            :timestamp="formatDate(record.timestamp)"
            :type="getHistoryItemType(record.status)"
          >
            <h4>状态变更为: {{ getStatusLabel(record.status) }}</h4>
            <p v-if="record.feedback">{{ record.feedback }}</p>
          </el-timeline-item>
          
          <!-- 创建记录 -->
          <el-timeline-item 
            :timestamp="formatDate(task.createdAt)" 
            type="primary"
          >
            <h4>任务创建</h4>
          </el-timeline-item>
        </el-timeline>
      </div>
    </template>

    <template #footer>
      <span>
        <el-button @click="handleClose">关闭</el-button>
      </span>
    </template>
  </el-dialog>
  
  <!-- 状态对话框 -->
  <el-dialog
    v-model="statusDialogVisible"
    title="更新任务状态"
    width="30%"
    destroy-on-close
  >
    <el-form>
      <el-form-item label="反馈信息">
        <el-input
          v-model="dialogFeedback"
          type="textarea"
          rows="4"
          placeholder="输入任务反馈..."
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
          v-model="dialogFeedback"
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
</template>

<script setup>
import { ref, computed, watch } from 'vue';

// 属性定义
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  task: {
    type: Object,
    default: null
  },
  isAdmin: {
    type: Boolean,
    default: false
  }
});

// 事件定义
const emit = defineEmits(['close', 'update-status', 'review-task', 'add-feedback']);

// 本地状态
const dialogVisible = ref(props.visible);
const feedbackText = ref('');
const statusDialogVisible = ref(false);
const reviewDialogVisible = ref(false);
const newStatus = ref('');
const isApproved = ref(true);
const dialogFeedback = ref('');

// 监听对话框可见性
watch(() => props.visible, (val) => {
  dialogVisible.value = val;
}, { immediate: true });

// 监听内部对话框可见性
watch(dialogVisible, (val) => {
  if (!val) {
    emit('close');
  }
});

// 计算属性：排序后的历史记录（最新的在前面）
const sortedHistory = computed(() => {
  if (!props.task || !props.task.history) return [];
  return [...props.task.history].sort((a, b) => 
    new Date(b.timestamp) - new Date(a.timestamp)
  );
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

// 历史记录项类型映射
const getHistoryItemType = (status) => {
  const map = {
    'pending': 'warning',
    'in-progress': 'primary',
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
  if (!dateString) return '未设置';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false;
};

// 处理状态变更
const handleStatusChange = (status) => {
  newStatus.value = status;
  statusDialogVisible.value = true;
};

// 确认状态更新
const confirmStatusUpdate = () => {
  if (props.task) {
    emit('update-status', {
      taskId: props.task.id,
      status: newStatus.value,
      feedback: dialogFeedback.value
    });
    statusDialogVisible.value = false;
    dialogFeedback.value = '';
  }
};

// 处理审核
const handleReview = (approved) => {
  isApproved.value = approved;
  reviewDialogVisible.value = true;
};

// 确认审核
const confirmReview = () => {
  if (props.task) {
    emit('review-task', {
      taskId: props.task.id,
      approved: isApproved.value,
      feedback: dialogFeedback.value
    });
    reviewDialogVisible.value = false;
    dialogFeedback.value = '';
  }
};

// 提交反馈
const submitFeedback = () => {
  if (props.task && feedbackText.value.trim()) {
    emit('add-feedback', {
      taskId: props.task.id,
      feedback: feedbackText.value
    });
    feedbackText.value = '';
  }
};
</script>

<style scoped>
.task-actions, .task-history {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.action-buttons {
  margin-bottom: 20px;
}

h3 {
  font-size: 16px;
  margin-bottom: 15px;
  color: #409eff;
}
</style> 