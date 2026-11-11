<template>
  <div class="task-progress">
    <h2>任务进度统计</h2>
    
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ statistics.pending }}</div>
          <div class="stat-label">待处理任务</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card in-progress">
          <div class="stat-value">{{ statistics.inProgress }}</div>
          <div class="stat-label">进行中任务</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card completed">
          <div class="stat-value">{{ statistics.completed }}</div>
          <div class="stat-label">已完成任务</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card rejected">
          <div class="stat-value">{{ statistics.rejected }}</div>
          <div class="stat-label">已驳回任务</div>
        </el-card>
      </el-col>
    </el-row>
    
    <div class="chart-container">
      <h3>任务状态分布</h3>
      <v-chart class="chart" :option="pieChartOption" autoresize />
    </div>
    
    <div class="chart-container">
      <h3>任务完成率</h3>
      <div class="progress-bar">
        <el-progress 
          :percentage="completionRate" 
          :stroke-width="20"
          :format="percentFormat"
          :color="getProgressColor(completionRate)"
        />
      </div>
      <div class="progress-description">
        总完成率: {{ completionRate.toFixed(2) }}% ({{ statistics.completed }} / {{ totalTasks }})
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import VChart from 'vue-echarts';

// 注册必要的 ECharts 组件
use([
  CanvasRenderer,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent
]);

// 属性定义
const props = defineProps({
  statistics: {
    type: Object,
    default: () => ({
      completed: 0,
      pending: 0,
      inProgress: 0,
      rejected: 0
    })
  }
});

// 计算总任务数
const totalTasks = computed(() => {
  const { completed, pending, inProgress, rejected } = props.statistics;
  return completed + pending + inProgress + rejected;
});

// 计算完成率
const completionRate = computed(() => {
  if (totalTasks.value === 0) return 0;
  return (props.statistics.completed / totalTasks.value) * 100;
});

// 饼图配置
const pieChartOption = computed(() => {
  const { completed, pending, inProgress, rejected } = props.statistics;
  
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: ['待处理', '进行中', '已完成', '已驳回']
    },
    series: [
      {
        name: '任务状态',
        type: 'pie',
        radius: '70%',
        center: ['50%', '60%'],
        data: [
          { value: pending, name: '待处理', itemStyle: { color: '#909399' } },
          { value: inProgress, name: '进行中', itemStyle: { color: '#E6A23C' } },
          { value: completed, name: '已完成', itemStyle: { color: '#67C23A' } },
          { value: rejected, name: '已驳回', itemStyle: { color: '#F56C6C' } }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };
});

// 百分比格式化
const percentFormat = (percentage) => {
  return `${percentage}%`;
};

// 获取进度条颜色
const getProgressColor = (rate) => {
  if (rate < 30) return '#F56C6C';
  if (rate < 70) return '#E6A23C';
  return '#67C23A';
};
</script>

<style scoped>
.task-progress {
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

.stat-card {
  text-align: center;
  padding: 20px 0;
  margin-bottom: 20px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
}

.stat-card.in-progress .stat-value {
  color: #E6A23C;
}

.stat-card.completed .stat-value {
  color: #67C23A;
}

.stat-card.rejected .stat-value {
  color: #F56C6C;
}

.stat-label {
  margin-top: 10px;
  color: #606266;
  font-size: 14px;
}

.chart-container {
  margin: 30px 0;
}

.chart {
  height: 300px;
}

.progress-bar {
  margin: 20px 0;
}

.progress-description {
  text-align: center;
  color: #606266;
  font-size: 14px;
}
</style> 