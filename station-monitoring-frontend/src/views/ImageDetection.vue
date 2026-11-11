<template>
  <div class="image-detection">
    <!-- 左侧：检测视频区域 -->
    <div class="video-container">
      <h3>图像检测</h3>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="displayedCameras.length === 0" class="no-cameras">
        没有选择摄像头，请在右侧列表中选择
      </div>
      <div v-else class="video-grid">
        <div v-for="camera in displayedCameras" :key="camera.id" class="video-item" :class="{ 'active': currentCamera && currentCamera.id === camera.id }" :data-camera-id="camera.id">
          <div class="camera-header">
            <span>{{ camera.name || `摄像头 ${camera.id}` }}</span>
            <div class="camera-controls">
              <el-button type="success" size="small" @click="toggleFullscreen(camera)" plain>
                <el-icon><FullScreen /></el-icon>
              </el-button>
            </div>
          </div>
          <img :src="`http://localhost:5000/video_feed/${camera.id}`" :alt="`摄像头 ${camera.id} 视频流`" />
        </div>
      </div>
    </div>

    <!-- 右侧面板 -->
    <div class="right-panel">
      <!-- 在线摄像头列表 -->
      <div class="camera-list-container">
        <div class="panel-header">
          <h3>在线摄像头</h3>
          <div class="search-box">
            <el-input v-model="searchKeyword" placeholder="搜索摄像头" clearable @clear="fetchCameras">
              <template #suffix>
                <el-icon @click="searchCameras"><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
        
        <div class="camera-list-scroll">
          <div class="camera-list">
            <div 
              v-for="camera in onlineCameras" 
              :key="camera.id" 
              class="camera-item"
              :class="{'camera-selected': isDisplayed(camera.id)}"
              @click="toggleCameraDisplay(camera)"
            >
              <div class="camera-info">
                <span class="camera-name">{{ camera.name || `摄像头 ${camera.id}` }}</span>
                <el-tag size="small" type="success">在线</el-tag>
              </div>
              <div class="camera-actions">
                <el-button 
                  type="primary" 
                  size="small" 
                  :icon="isDisplayed(camera.id) ? 'VideoPlay' : 'VideoPlay'" 
                  @click.stop="toggleCameraDisplay(camera)"
                  circle
                ></el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 危险状况列表 -->
      <div class="alert-list-container">
        <div class="panel-header">
          <h3>危险状况列表</h3>
          <div class="panel-controls">
            <el-checkbox v-model="autoScroll">自动滚动</el-checkbox>
            <el-button size="small" @click="clearAlerts" type="danger" plain>清空</el-button>
          </div>
        </div>
        
        <div class="alert-list-scroll" ref="alertScrollContainer">
          <div class="alert-list">
            <div v-if="alerts.length === 0" class="no-alerts">
              暂无危险状况
            </div>
            <div v-for="(alert, index) in alerts" :key="index" class="alert-item" :class="{ 'high': alert.type == 0 || alert.level == 0, 'medium': alert.type == 1 || alert.level == 1, 'low': alert.type == 2 || alert.level == 2 }">
              <div class="alert-time">{{ formatTime(alert.createTime) }}</div>
              <div class="alert-content">
                <div class="alert-title">
                  <el-tag :type="getAlertTypeByLevel(alert.type || alert.level)" size="small">{{ getAlertLevelText(alert.type || alert.level) }}</el-tag>
                  <span>{{ alert.title || alert.content }}</span>
                </div>
                <div class="alert-description">{{ alert.description }}</div>
                <div class="alert-source">
                  摄像头: {{ getCameraNameById(alert.cameraId) }}
                </div>
              </div>
              <div class="alert-actions">
                <el-button type="primary" size="small" @click="viewAlertCamera(alert.cameraId)">查看</el-button>
                <el-button type="info" size="small" @click="markAsRead(index)">已读</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { Search, FullScreen } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { getAllCameras, searchCamera } from "@/http/api/camera.js";
import { getUndisposedAlarmInfo, updateAlarmInfoById } from '@/http/api/alarm.js'
// 摄像头数据
const cameras = ref([]);
const displayedCameras = reactive([]);
const currentCamera = ref(null);
const loading = ref(true);
const searchKeyword = ref('');

// 危险状况列表
const alerts = ref([]);
const autoScroll = ref(true);
const alertScrollContainer = ref(null);
const alarmTimer = ref(null); // 添加定时器引用

//获取未处理的危险警告
const getUndisposedAlarmData = async() => {
  try {
    const response = await getUndisposedAlarmInfo();
    if (response.data.success) {
      alerts.value = response.data.data; // 修复变量名从alarms改为alerts
    }else {
      ElMessage({
        message: '获取未处理危险警告失败',
        type: 'error',
        plain: true,
      });
    }
  }catch(error) {
    console.error('获取所有危险警告失败', error);
  }
}

// 获取在线摄像头列表
const onlineCameras = computed(() => {
  return cameras.value.filter(camera => camera.status == 0);
});

// 获取所有摄像头数据
const fetchCameras = async () => {
  try {
    loading.value = true;
    const response = await getAllCameras();
    cameras.value = response.data || [];
  } catch (error) {
    console.error('获取摄像头列表失败:', error);
    ElMessage.error('获取摄像头列表失败');
  } finally {
    loading.value = false;
  }
};

// 搜索摄像头
const searchCameras = async () => {
  if (!searchKeyword.value) {
    fetchCameras();
    return;
  }
  
  try {
    loading.value = true;
    const response = await searchCamera(searchKeyword.value);
    cameras.value = response.data || [];
  } catch (error) {
    console.error('搜索摄像头失败:', error);
    ElMessage.error('搜索摄像头失败');
  } finally {
    loading.value = false;
  }
};

// 判断摄像头是否在显示列表中
const isDisplayed = (cameraId) => {
  return displayedCameras.some(cam => cam.id === cameraId);
};

// 切换摄像头显示状态
const toggleCameraDisplay = (camera) => {
  const cameraIndex = displayedCameras.findIndex(cam => cam.id === camera.id);
  
  if (cameraIndex !== -1) {
    // 如果是当前控制的摄像头，清除当前选择
    if (currentCamera.value && currentCamera.value.id === camera.id) {
      currentCamera.value = null;
    }
    
    // 从显示列表中移除
    displayedCameras.splice(cameraIndex, 1);
  } else {
    // 添加到显示列表
    displayedCameras.push(camera);
    
    // 设置为当前选中的摄像头
    currentCamera.value = camera;
  }
};

// 切换全屏模式
const toggleFullscreen = (camera) => {
  const videoItem = document.querySelector(`.video-item[data-camera-id="${camera.id}"]`);
  
  if (!videoItem) {
    ElMessage.warning('找不到视频元素');
    return;
  }

  if (!document.fullscreenElement) {
    // 进入全屏
    videoItem.requestFullscreen().catch(err => {
      ElMessage.error(`全屏错误: ${err.message}`);
    });
  } else {
    // 退出全屏
    document.exitFullscreen().catch(err => {
      ElMessage.error(`退出全屏错误: ${err.message}`);
    });
  }
};

// 根据摄像头ID获取摄像头名称
const getCameraNameById = (cameraId) => {
  const camera = cameras.value.find(cam => cam.id === cameraId);
  return camera ? (camera.name || `摄像头 ${cameraId}`) : `摄像头 ${cameraId}`;
};

// 格式化时间
const formatTime = (time) => {
  const date = new Date(time);
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const seconds = date.getSeconds().toString().padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};

// 根据警报级别获取类型
const getAlertTypeByLevel = (level) => {
  switch (Number(level)) {
    case 0: return 'danger';
    case 1: return 'warning';
    case 2: return 'info';
    default: return 'info';
  }
};

// 根据警报级别获取文本
const getAlertLevelText = (level) => {
  switch (Number(level)) {
    case 0: return '高危';
    case 1: return '中危';
    case 2: return '低危';
    default: return '未知';
  }
};

// 查看报警的摄像头
const viewAlertCamera = (cameraId) => {
  const camera = cameras.value.find(cam => cam.id === cameraId);
  if (!camera) {
    ElMessage.warning('找不到相关摄像头');
    return;
  }
  
  // 如果摄像头不在显示列表中，添加进去
  if (!isDisplayed(cameraId)) {
    toggleCameraDisplay(camera);
  }
  
  // 设置为当前选中的摄像头
  currentCamera.value = camera;
};

// 标记警报为已读
const markAsRead = async (index) => {
  const alert = alerts.value[index];
  if (!alert || alert.dealFlag !== 0) {
    return;
  }
  
  try {
    const response = await updateAlarmInfoById(alert.id);
    if (response.data.success) {
      ElMessage({
        message: '已标记为已读',
        type: 'success',
        plain: true,
      });
      // 重新获取未处理的警告
      getUndisposedAlarmData();
    } else {
      ElMessage({
        message: '标记为已读失败',
        type: 'error',
        plain: true,
      });
    }
  } catch (error) {
    console.error('标记为已读失败:', error);
    ElMessage.error('标记为已读失败');
  }
};

// 清空警报列表
const clearAlerts = () => {
  alerts.value = [];
};

// 监听警报列表变化，实现自动滚动
watch(alerts, () => {
  if (autoScroll.value && alertScrollContainer.value) {
    nextTick(() => {
      alertScrollContainer.value.scrollTop = 0;
    });
  }
});

// 设置定时获取警告信息
const setupAlarmTimer = () => {
  // 先清除之前的定时器
  if (alarmTimer.value) {
    clearInterval(alarmTimer.value);
  }
  
  // 立即获取一次数据
  getUndisposedAlarmData();
  
  // 设置每5秒获取一次数据
  alarmTimer.value = setInterval(() => {
    getUndisposedAlarmData();
  }, 5000);
};

// 组件挂载与卸载
onMounted(() => {
  fetchCameras();
  setupAlarmTimer(); // 启动定时获取警告信息
});

onUnmounted(() => {
  // 清理资源
  if (alarmTimer.value) {
    clearInterval(alarmTimer.value);
    alarmTimer.value = null;
  }
});
</script>

<style scoped>
.image-detection {
  display: flex;
  width: 100%;
  height: 100%;
  background-color: #f0f2f5;
  overflow: hidden;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

h3 {
  text-align: center;
}

.loading, .no-cameras, .no-alerts {
  text-align: center;
  padding: 20px;
  font-size: 16px;
  color: #909399;
}

.video-container {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  height: 100%;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(45%, 1fr));
  grid-auto-rows: 300px;
  gap: 15px;
}

.video-item {
  position: relative;
  background-color: #000;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
  height: 100%;
}

.video-item.active {
  border: 2px solid #409eff;
}

.camera-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 10px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  z-index: 10;
}

.camera-controls {
  display: flex;
  gap: 5px;
}

.video-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.right-panel {
  width: 380px;
  background-color: white;
  border-left: 1px solid #dcdfe6;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
}

.camera-list-container {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid #dcdfe6;
  height: 300px;
}

.panel-header {
  padding: 10px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.camera-list-scroll, .alert-list-scroll {
  flex: 1;
  overflow-y: auto;
}

.camera-list, .alert-list {
  padding: 10px;
}

.camera-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.camera-item:hover {
  background-color: #f5f7fa;
}

.camera-selected {
  background-color: #ecf5ff;
}

.camera-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.camera-name {
  font-weight: bold;
}

.alert-list-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.alert-item {
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 12px;
  background-color: #f9f9f9;
  border-left: 4px solid #909399;
}

.alert-item.high {
  border-left-color: #f56c6c;
  background-color: #fef0f0;
}

.alert-item.medium {
  border-left-color: #e6a23c;
  background-color: #fdf6ec;
}

.alert-item.low {
  border-left-color: #409eff;
  background-color: #ecf5ff;
}

.alert-time {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.alert-content {
  margin-bottom: 10px;
}

.alert-title {
  font-weight: bold;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.alert-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.alert-source {
  font-size: 12px;
  color: #909399;
}

.alert-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 全屏状态下的样式调整 */
:fullscreen .video-item {
  border: none;
  border-radius: 0;
}

:fullscreen .video-item img {
  width: 100vw;
  height: 100vh;
}
</style>
  