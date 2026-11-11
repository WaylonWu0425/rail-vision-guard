<template>
  <div class="monitoring-screen">
    <!-- 监控画面区域 -->
    <div class="video-container">
      <div v-for="(camera) in displayedCameras" :key="camera.id" class="video-item"
           :class="{ 'active': currentCamera && currentCamera.id === camera.id }" :data-camera-id="camera.id">
        <div class="camera-header">
          <span>{{ camera.name }}</span>
          <div class="camera-controls">
            <el-button type="primary" size="small" @click="selectCamera(camera)" plain>控制</el-button>
            <el-button type="success" size="small" @click="toggleFullscreen(camera)" plain>
              <el-icon>
                <FullScreen/>
              </el-icon>
            </el-button>
          </div>
        </div>
        <canvas ref="canvasElements" :id="`canvas-${camera.id}`" class="video-canvas"></canvas>
        <video ref="videoElements" :id="`video-${camera.id}`" class="video-element"></video>
      </div>
    </div>

    <!-- 右侧操作面板 -->
    <div class="right-panel">
      <!-- 摄像头列表 - 缩小并添加滚动 -->
      <div class="camera-list-container">
        <div class="panel-header">
          <h3>摄像头列表</h3>
          <div class="search-box">
            <el-input v-model="searchKeyword" placeholder="搜索摄像头" clearable @clear="getCameraData">
              <template #suffix>
                <el-icon @click="searchCameras">
                  <Search/>
                </el-icon>
              </template>
            </el-input>
          </div>
        </div>

        <!-- 修改这里：设置固定高度，启用滚动 -->
        <div class="camera-list-scroll">
          <div class="camera-list">
            <div
                v-for="camera in cameraList"
                :key="camera.id"
                class="camera-item"
                :class="{'camera-selected': isDisplayed(camera.id)}"
                @click="toggleCameraDisplay(camera)"
            >
              <div class="camera-info">
                <span class="camera-name">{{ camera.name }}</span>
                <el-tag size="small" :type="camera.status == 0 ? 'success' : 'danger'">
                  {{ camera.status == 0 ? '在线' : '离线' }}
                </el-tag>
              </div>
              <div class="camera-actions">
                <el-button
                    type="primary"
                    size="small"
                    :icon="isDisplayed(camera.id) ? 'VideoPlay' : 'VideoPlay'"
                    :disabled="!camera.status"
                    @click.stop="toggleCameraDisplay(camera)"
                    circle
                ></el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 云台控制面板 -->
      <div class="ptz-control-panel" v-if="currentCamera">
        <div class="panel-header">
          <h3>云台控制 - {{ currentCamera.name }}</h3>
        </div>

        <div class="ptz-container">
          <div class="step-selector">
            <span>步长(1-8):</span>
            <el-select v-model="step" style="width: 80px;">
              <el-option v-for="n in 8" :key="n" :label="n" :value="n"></el-option>
            </el-select>
          </div>

          <div class="ptz-controls">
            <el-button class="ptz-btn" @mousedown="onHandlePTZ('LeftUp', false)" @mouseup="onHandlePTZ('LeftUp', true)">
              <el-icon>
                <ArrowUpLeft/>
              </el-icon>
            </el-button>
            <el-button class="ptz-btn" @mousedown="onHandlePTZ('Up', false)" @mouseup="onHandlePTZ('Up', true)">
              <el-icon>
                <ArrowUp/>
              </el-icon>
            </el-button>
            <el-button class="ptz-btn" @mousedown="onHandlePTZ('RightUp', false)"
                       @mouseup="onHandlePTZ('RightUp', true)">
              <el-icon>
                <ArrowUpRight/>
              </el-icon>
            </el-button>
            <el-button class="ptz-btn" @mousedown="onHandlePTZ('Left', false)" @mouseup="onHandlePTZ('Left', true)">
              <el-icon>
                <ArrowLeft/>
              </el-icon>
            </el-button>
            <el-button class="ptz-btn center-btn">中心</el-button>
            <el-button class="ptz-btn" @mousedown="onHandlePTZ('Right', false)" @mouseup="onHandlePTZ('Right', true)">
              <el-icon>
                <ArrowRight/>
              </el-icon>
            </el-button>
            <el-button class="ptz-btn" @mousedown="onHandlePTZ('LeftDown', false)"
                       @mouseup="onHandlePTZ('LeftDown', true)">
              <el-icon>
                <ArrowDownLeft/>
              </el-icon>
            </el-button>
            <el-button class="ptz-btn" @mousedown="onHandlePTZ('Down', false)" @mouseup="onHandlePTZ('Down', true)">
              <el-icon>
                <ArrowDown/>
              </el-icon>
            </el-button>
            <el-button class="ptz-btn" @mousedown="onHandlePTZ('RightDown', false)"
                       @mouseup="onHandlePTZ('RightDown', true)">
              <el-icon>
                <ArrowDownRight/>
              </el-icon>
            </el-button>
          </div>

          <div class="camera-functions">
            <div class="function-row">
              <el-button @mousedown="onHandlePTZ('ZoomWide', false)" @mouseup="onHandlePTZ('ZoomWide', true)">变倍-
              </el-button>
              <el-button @mousedown="onHandlePTZ('ZoomTele', false)" @mouseup="onHandlePTZ('ZoomTele', true)">变倍+
              </el-button>
            </div>
            <div class="function-row">
              <el-button @mousedown="onHandlePTZ('FocusFar', false)" @mouseup="onHandlePTZ('FocusFar', true)">聚焦-
              </el-button>
              <el-button @mousedown="onHandlePTZ('FocusNear', false)" @mouseup="onHandlePTZ('FocusNear', true)">聚焦+
              </el-button>
            </div>
            <div class="function-row">
              <el-button @mousedown="onHandlePTZ('IrisSmall', false)" @mouseup="onHandlePTZ('IrisSmall', true)">光圈-
              </el-button>
              <el-button @mousedown="onHandlePTZ('IrisLarge', false)" @mouseup="onHandlePTZ('IrisLarge', true)">光圈+
              </el-button>
            </div>
          </div>

          <div class="control-actions">
            <el-button type="primary" @click="playerCapture">截图</el-button>
            <el-button type="success" @click="toggleRecord">{{ isRecording ? '停止录制' : '开始录制' }}</el-button>
            <el-button type="warning" @click="playerStop">关闭视频</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive, onMounted, onUnmounted, nextTick} from 'vue';
import {
  Search,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUpLeft,
  ArrowUpRight,
  ArrowDownLeft,
  ArrowDownRight,
  VideoPlay,
  FullScreen
} from '@element-plus/icons-vue';
import {ElMessage} from 'element-plus';
import {getAllCameras, searchCamera} from "@/http/api/camera.js";

// 摄像头列表
const cameraList = reactive([]);
const searchKeyword = ref('');
const step = ref(1);
const currentCamera = ref(null);
const displayedCameras = reactive([]);
const canvasElements = ref([]);
const videoElements = ref([]);
const playerInstances = reactive({});
const isRecording = ref(false);
const fullscreenCamera = ref(null);

// 获取所有摄像头数据
const getCameraData = async () => {
  try {
    const response = await getAllCameras();
    cameraList.splice(0, cameraList.length, ...response.data);
  } catch (error) {
    console.error('获取摄像头列表失败:', error);
    ElMessage.error('获取摄像头列表失败');
  }
};

// 搜索摄像头
const searchCameras = async () => {
  if (!searchKeyword.value) {
    getCameraData();
    return;
  }

  try {
    const response = await searchCamera(searchKeyword.value);
    cameraList.splice(0, cameraList.length, ...response.data);
  } catch (error) {
    console.error('搜索摄像头失败:', error);
    ElMessage.error('搜索摄像头失败');
  }
};

// 选择摄像头进行控制
const selectCamera = (camera) => {
  currentCamera.value = camera;
};

// 判断摄像头是否在显示列表中
const isDisplayed = (cameraId) => {
  return displayedCameras.some(cam => cam.id === cameraId);
};

// 切换摄像头显示状态
const toggleCameraDisplay = async (camera) => {
  // 检查摄像头是否离线
  if (!camera.status) {
    ElMessage.warning('该摄像头当前离线');
    return;
  }

  const cameraIndex = displayedCameras.findIndex(cam => cam.id === camera.id);

  if (cameraIndex !== -1) {
    // 如果是当前控制的摄像头，清除当前选择
    if (currentCamera.value && currentCamera.value.id === camera.id) {
      currentCamera.value = null;
    }

    // 停止视频播放
    if (playerInstances[camera.id]) {
      playerInstances[camera.id].close();
      delete playerInstances[camera.id];
    }

    // 从显示列表中移除
    displayedCameras.splice(cameraIndex, 1);
  } else {
    // 添加到显示列表
    displayedCameras.push(camera);

    // 设置为当前选中的摄像头
    currentCamera.value = camera;

    // 等待DOM更新后初始化播放器
    await nextTick();
    initPlayer(camera);
  }
};

// 初始化视频播放器
const initPlayer = (camera) => {
  const canvasId = `canvas-${camera.id}`;
  const videoId = `video-${camera.id}`;

  const canvasElement = document.getElementById(canvasId);
  const videoElement = document.getElementById(videoId);

  if (!canvasElement || !videoElement) {
    console.error('无法找到视频元素');
    return;
  }

  const options = {
    wsURL: 'ws://' + camera.ip + '/rtspoverwebsocket',
    rtspURL: 'rtsp://' + camera.ip + '/cam/realmonitor?channel=1&subtype=0&proto=Private3',
    username: camera.username,
    password: camera.password
  };

  const player = new window.PlayerControl(options);

  player.on('WorkerReady', function () {
    player.connect();
  });

  player.on('DecodeStart', function (rs) {
    console.log('开始解码:', camera.name);
  });

  player.on('PlayStart', function (rs) {
    console.log('开始播放:', camera.name);
  });


  player.init(canvasElement, videoElement);
  playerInstances[camera.id] = player;
};

// 云台控制
const onHandlePTZ = (type, isStop) => {
  if (!currentCamera.value) return;

  let arg2 = 0;
  let arg2Arr = ['LeftUp', 'RightUp', 'LeftDown', 'RightDown'];

  if (arg2Arr.indexOf(type) > -1) {
    arg2 = step.value;
  }

  if (!isStop) {
    RPC.PTZManager('start', currentCamera.value.channel || 0, {
      'code': type,
      'arg1': step.value,
      'arg2': arg2,
      'arg3': 0
    });
  } else {
    RPC.PTZManager('stop', currentCamera.value.channel || 0, {
      'code': type,
      'arg1': step.value,
      'arg2': arg2,
      'arg3': 0
    });
  }
};

// 摄像头功能 - 截图
const playerCapture = () => {
  if (!currentCamera.value || !playerInstances[currentCamera.value.id]) {
    ElMessage.warning('请先选择一个在线摄像头');
    return;
  }

  try {
    playerInstances[currentCamera.value.id].capture('screenshot_' + new Date().getTime());
    ElMessage.success('截图成功');
  } catch (error) {
    console.error('截图失败:', error);
    ElMessage.error('截图失败');
  }
};

// 摄像头功能 - 切换录制状态
const toggleRecord = () => {
  if (!currentCamera.value || !playerInstances[currentCamera.value.id]) {
    ElMessage.warning('请先选择一个在线摄像头');
    return;
  }

  try {
    if (isRecording.value) {
      playerInstances[currentCamera.value.id].startRecord(false);
      isRecording.value = false;
      ElMessage.success('停止录制');
    } else {
      playerInstances[currentCamera.value.id].startRecord(true);
      isRecording.value = true;
      ElMessage.success('开始录制');
    }
  } catch (error) {
    console.error('录制操作失败:', error);
    ElMessage.error('录制操作失败');
  }
};

// 摄像头功能 - 停止播放
const playerStop = () => {
  if (!currentCamera.value || !playerInstances[currentCamera.value.id]) {
    ElMessage.warning('请先选择一个在线摄像头');
    return;
  }

  try {
    playerInstances[currentCamera.value.id].close();
    delete playerInstances[currentCamera.value.id];

    const cameraIndex = displayedCameras.findIndex(cam => cam.id === currentCamera.value.id);
    if (cameraIndex !== -1) {
      displayedCameras.splice(cameraIndex, 1);
    }

    currentCamera.value = null;
    ElMessage.success('已关闭视频');
  } catch (error) {
    console.error('关闭视频失败:', error);
    ElMessage.error('关闭视频失败');
  }
};

// WebSocket 连接，用于实时获取摄像头状态
let ws = null;

const connectWebSocket = () => {
  if (ws) {
    ws.close();
  }

  ws = new WebSocket("ws://localhost:8081/ws/cameraStatus");

  ws.onopen = () => {
    console.log("WebSocket 连接成功");
  };

  ws.onmessage = (event) => {
    try {
      const cameraStatusUpdate = JSON.parse(event.data);
      updateCameraStatus(cameraStatusUpdate);
    } catch (error) {
      console.error("WebSocket 数据解析失败:", error);
    }
  };

  ws.onclose = () => {
    console.log("WebSocket 连接已关闭");
  };

  ws.onerror = (error) => {
    console.error("WebSocket 错误:", error);
  };
};

// 更新摄像头状态
const updateCameraStatus = (cameraList) => {
  cameraList.forEach(updatedCamera => {
    const index = cameraList.findIndex(c => c.id === updatedCamera.id);
    if (index !== -1) {
      cameraList[index].status = updatedCamera.status;
    }
  });
};

// 切换全屏模式
const toggleFullscreen = (camera) => {
  if (!camera || !playerInstances[camera.id]) {
    ElMessage.warning('无法切换该摄像头的全屏状态');
    return;
  }

  const videoItem = document.querySelector(`.video-item[data-camera-id="${camera.id}"]`);

  if (!videoItem) {
    ElMessage.warning('找不到视频元素');
    return;
  }

  if (!document.fullscreenElement) {
    // 进入全屏
    videoItem.requestFullscreen().then(() => {
      fullscreenCamera.value = camera;
    }).catch(err => {
      ElMessage.error(`全屏错误: ${err.message}`);
    });
  } else {
    // 退出全屏
    document.exitFullscreen().then(() => {
      fullscreenCamera.value = null;
    }).catch(err => {
      ElMessage.error(`退出全屏错误: ${err.message}`);
    });
  }
};

// 监听全屏变化事件
const handleFullscreenChange = () => {
  if (!document.fullscreenElement && fullscreenCamera.value) {
    fullscreenCamera.value = null;
  }
};

// 组件挂载与卸载
onMounted(() => {
  getCameraData();
  connectWebSocket();

  // 添加全屏变化监听
  document.addEventListener('fullscreenchange', handleFullscreenChange);
});

onUnmounted(() => {
  // 关闭所有播放实例
  Object.values(playerInstances).forEach(player => {
    try {
      player.close();
    } catch (e) {
      console.error('关闭播放器失败:', e);
    }
  });

  // 关闭WebSocket连接
  if (ws) {
    ws.close();
  }

  // 移除全屏监听
  document.removeEventListener('fullscreenchange', handleFullscreenChange);
});
</script>

<style scoped>
.monitoring-screen {
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

.video-container {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(45%, 1fr));
  grid-auto-rows: 300px;
  gap: 10px;
  padding: 10px;
  overflow-y: auto;
  height: 100%;
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

.video-canvas, .video-element {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.right-panel {
  width: 300px;
  background-color: white;
  border-left: 1px solid #dcdfe6;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
}

.camera-list-container {
  flex: 0 0 auto; /* 不伸缩 */
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid #dcdfe6;
  /* 设置固定高度 */
  height: 300px; /* 固定总高度 */
}

.panel-header {
  padding: 10px;
  border-bottom: 1px solid #ebeef5;
}

.search-box {
  margin-top: 10px;
}

.camera-list-scroll {
  flex: 1;
  overflow-y: auto; /* 启用垂直滚动 */
}

.camera-list {
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

.ptz-control-panel {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  overflow: auto;
  min-height: 0;
}

.ptz-container {
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ptz-controls {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 5px;
}

.ptz-btn {
  height: 40px;
  padding: 0;
  font-size: 18px;
}

.center-btn {
  background-color: #f0f0f0;
}

.camera-functions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.function-row {
  display: flex;
  gap: 10px;
}

.control-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

/* 全屏状态下的样式调整 */
:fullscreen .video-item {
  border: none;
  border-radius: 0;
}

:fullscreen .video-canvas,
:fullscreen .video-element {
  width: 100vw;
  height: 100vh;
}
</style>
