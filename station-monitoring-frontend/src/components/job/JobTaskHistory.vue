<template>
  <div class="task-history">
    <h2>历史任务查询</h2>
    
    <!-- 搜索过滤区域 -->
    <div class="search-area">
      <el-form :model="searchForm" label-width="80px" inline>
        <el-form-item label="关键词">
          <el-input 
            v-model="searchForm.keyword" 
            placeholder="标题/描述" 
            clearable 
            @clear="handleSearch"
          />
        </el-form-item>
        
        <el-form-item label="任务类型">
          <el-select 
            v-model="searchForm.type" 
            placeholder="所有类型" 
            clearable
            @change="handleSearch"
          >
            <el-option label="维护" value="维护" />
            <el-option label="安装" value="安装" />
            <el-option label="检查" value="检查" />
            <el-option label="配置" value="配置" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="任务状态">
          <el-select 
            v-model="searchForm.status" 
            placeholder="所有状态" 
            clearable
            @change="handleSearch"
          >
            <el-option label="待处理" value="pending" />
            <el-option label="进行中" value="in-progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleSearch"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 统计信息 -->
    <div class="statistics">
      <el-descriptions :column="4" border size="small">
        <el-descriptions-item label="查询结果总数">{{ filteredTasks.length }}</el-descriptions-item>
        <el-descriptions-item label="已完成任务">{{ completedCount }}</el-descriptions-item>
        <el-descriptions-item label="总任务时长">{{ totalTaskDuration }}</el-descriptions-item>
        <el-descriptions-item label="导出">
          <el-button size="small" type="primary" @click="exportTasks">导出结果</el-button>
        </el-descriptions-item>
      </el-descriptions>
    </div>
    
    <!-- 任务列表 -->
    <el-table 
      :data="pagedTasks" 
      style="width: 100%" 
      border 
      stripe
      v-loading="loading"
    >
      <el-table-column prop="id" label="ID" width="60" sortable />
      <el-table-column prop="title" label="任务标题" min-width="150" show-overflow-tooltip />
      <el-table-column prop="type" label="类型" width="100" sortable />
      <el-table-column label="状态" width="100" sortable="custom" :sort-method="sortByStatus">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)" effect="plain">
            {{ getStatusLabel(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="160" sortable>
        <template #default="scope">
          {{ formatDate(scope.row.createdAt) }}
        </template>
      </el-table-column>
      <el-table-column label="开始时间" width="160" sortable>
        <template #default="scope">
          {{ scope.row.startTime ? formatDate(scope.row.startTime) : '未开始' }}
        </template>
      </el-table-column>
      <el-table-column label="结束时间" width="160" sortable>
        <template #default="scope">
          {{ scope.row.endTime ? formatDate(scope.row.endTime) : '未结束' }}
        </template>
      </el-table-column>
      <el-table-column label="任务时长" width="100" sortable="custom" :sort-method="sortByDuration">
        <template #default="scope">
          {{ calculateTaskDuration(scope.row) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="scope">
          <el-button 
            type="primary" 
            size="small" 
            @click="viewTaskDetails(scope.row)"
            link
          >
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="filteredTasks.length"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="taskDetailVisible"
      title="任务详情"
      width="60%"
      destroy-on-close
    >
      <template v-if="selectedTask">
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="任务ID">{{ selectedTask.id }}</el-descriptions-item>
          <el-descriptions-item label="任务标题">{{ selectedTask.title }}</el-descriptions-item>
          <el-descriptions-item label="任务类型">{{ selectedTask.type }}</el-descriptions-item>
          <el-descriptions-item label="优先级">{{ getPriorityLabel(selectedTask.priority) }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getStatusLabel(selectedTask.status) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(selectedTask.createdAt) }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ selectedTask.startTime ? formatDate(selectedTask.startTime) : '未开始' }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ selectedTask.endTime ? formatDate(selectedTask.endTime) : '未结束' }}
          </el-descriptions-item>
          <el-descriptions-item label="任务描述" :span="2">{{ selectedTask.description }}</el-descriptions-item>
        </el-descriptions>
        
        <h3>任务历史记录</h3>
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
            :timestamp="formatDate(selectedTask.createdAt)" 
            type="primary"
          >
            <h4>任务创建</h4>
          </el-timeline-item>
        </el-timeline>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue';

// 属性定义
const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  }
});

// 状态
const loading = ref(false);
const taskDetailVisible = ref(false);
const selectedTask = ref(null);
const currentPage = ref(1);
const pageSize = ref(10);

// 搜索表单
const searchForm = reactive({
  keyword: '',
  type: '',
  status: '',
  dateRange: null
});

// 处理搜索
const handleSearch = () => {
  // 重置分页到第一页
  currentPage.value = 1;
};

// 重置搜索条件
const resetSearch = () => {
  searchForm.keyword = '';
  searchForm.type = '';
  searchForm.status = '';
  searchForm.dateRange = null;
  handleSearch();
};

// 过滤后的任务
const filteredTasks = computed(() => {
  let result = [...props.tasks];
  
  // 关键词过滤
  if (searchForm.keyword) {
    const keyword = searchForm.keyword.toLowerCase();
    result = result.filter(task => 
      task.title.toLowerCase().includes(keyword) || 
      task.description.toLowerCase().includes(keyword)
    );
  }
  
  // 类型过滤
  if (searchForm.type) {
    result = result.filter(task => task.type === searchForm.type);
  }
  
  // 状态过滤
  if (searchForm.status) {
    result = result.filter(task => task.status === searchForm.status);
  }
  
  // 日期范围过滤
  if (searchForm.dateRange && searchForm.dateRange.length === 2) {
    const startDate = new Date(searchForm.dateRange[0]);
    startDate.setHours(0, 0, 0, 0);
    
    const endDate = new Date(searchForm.dateRange[1]);
    endDate.setHours(23, 59, 59, 999);
    
    result = result.filter(task => {
      const createdDate = new Date(task.createdAt);
      return createdDate >= startDate && createdDate <= endDate;
    });
  }
  
  return result;
});

// 分页后的任务
const pagedTasks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredTasks.value.slice(start, end);
});

// 已完成任务计数
const completedCount = computed(() => {
  return filteredTasks.value.filter(task => task.status === 'completed').length;
});

// 总任务时长
const totalTaskDuration = computed(() => {
  let totalMinutes = 0;
  
  filteredTasks.value.forEach(task => {
    if (task.startTime && task.endTime) {
      const start = new Date(task.startTime);
      const end = new Date(task.endTime);
      const durationMs = end - start;
      totalMinutes += durationMs / (1000 * 60);
    }
  });
  
  // 转换为小时:分钟格式
  const hours = Math.floor(totalMinutes / 60);
  const minutes = Math.floor(totalMinutes % 60);
  
  return `${hours}小时${minutes}分钟`;
});

// 任务历史记录（排序后）
const sortedHistory = computed(() => {
  if (!selectedTask.value || !selectedTask.value.history) return [];
  return [...selectedTask.value.history].sort((a, b) => 
    new Date(b.timestamp) - new Date(a.timestamp)
  );
});

// 分页变化
const handleSizeChange = (size) => {
  pageSize.value = size;
};

const handleCurrentChange = (page) => {
  currentPage.value = page;
};

// 查看任务详情
const viewTaskDetails = (task) => {
  selectedTask.value = task;
  taskDetailVisible.value = true;
};

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
    minute: '2-digit'
  });
};

// 计算任务时长
const calculateTaskDuration = (task) => {
  if (!task.startTime || !task.endTime) return '未完成';
  
  const start = new Date(task.startTime);
  const end = new Date(task.endTime);
  const durationMs = end - start;
  
  // 转换为小时:分钟格式
  const hours = Math.floor(durationMs / (1000 * 60 * 60));
  const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
  
  return `${hours}h ${minutes}m`;
};

// 按状态排序
const sortByStatus = (a, b) => {
  const statusOrder = {
    'pending': 1,
    'in-progress': 2,
    'completed': 3,
    'rejected': 4
  };
  
  return statusOrder[a.status] - statusOrder[b.status];
};

// 按时长排序
const sortByDuration = (a, b) => {
  if (!a.startTime || !a.endTime) return 1;
  if (!b.startTime || !b.endTime) return -1;
  
  const aDuration = new Date(a.endTime) - new Date(a.startTime);
  const bDuration = new Date(b.endTime) - new Date(b.startTime);
  
  return aDuration - bDuration;
};

// 导出任务
const exportTasks = () => {
  // 实际项目中可以实现为CSV导出或其他格式
  alert('导出功能在实际项目中实现');
};
</script>

<style scoped>
.task-history {
  padding: 10px;
}

h2 {
  margin-bottom: 20px;
  font-size: 22px;
  color: #303133;
}

h3 {
  margin: 20px 0 10px;
  font-size: 18px;
  color: #606266;
}

.search-area {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.statistics {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style> 