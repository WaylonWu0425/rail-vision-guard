<template>
  <div class="monitoring-screen">
    <header class="monitor-page-head"><div><span>LIVE MONITORING / 站场画面</span><h1>实时预览</h1></div><p>选择摄像头查看画面，并使用截图、录像与数字缩放。</p></header>
    <!-- 监控画面区域 -->
    <div class="video-container">
      <div v-if="loadingCameras" class="video-empty" role="status">正在加载摄像头列表…</div>
      <div v-else-if="cameraLoadError" class="video-empty video-error">
        <span>{{ cameraLoadError }}</span>
        <el-button size="small" type="primary" plain @click="getCameraData">重新加载</el-button>
      </div>
      <div v-else-if="cameraList.length === 0" class="video-empty">
        暂无摄像头，请先在“摄像头管理”中添加设备。
      </div>
      <div v-else-if="displayedCameras.length === 0" class="video-empty">
        <span>从右侧选择一台在线摄像头，即可打开实时预览。</span>
      </div>
      <div v-else class="video-grid">
      <div v-for="(camera) in displayedCameras" :key="camera.id" class="video-item"
           :class="{ 'active': currentCamera && currentCamera.id === camera.id, 'is-zoomed': zoomState.zoomLevel > 1 }"
           :data-camera-id="camera.id"
           @wheel.prevent="onWheelZoom"
           @mousedown="onPanStart"
           @mousemove="onPanMove"
           @mouseup="onPanEnd"
           @mouseleave="onPanEnd">
        <div class="camera-header">
          <span>{{ camera.name }}</span>
          <div class="camera-controls">
            <span v-if="zoomState.zoomLevel > 1" class="zoom-badge">×{{ zoomState.zoomLevel.toFixed(1) }}</span>
            <el-button v-if="zoomState.zoomLevel > 1" type="info" size="small" @click="resetZoom" plain>复位</el-button>
            <el-button type="primary" size="small" @click="selectCamera(camera)" plain>控制</el-button>
            <el-button type="success" size="small" @click="toggleFullscreen(camera)" plain>
              <el-icon>
                <FullScreen/>
              </el-icon>
            </el-button>
          </div>
        </div>
        <!-- 缩放平移容器：通过 CSS transform 实现数字变倍 -->
        <div class="zoom-viewport"
             :style="{ transform: `translate(${zoomState.panX}px, ${zoomState.panY}px) scale(${zoomState.zoomLevel})` }">
          <canvas ref="canvasElements" :id="`canvas-${camera.id}`" class="video-canvas"></canvas>
          <video ref="videoElements" :id="`video-${camera.id}`" class="video-element"></video>
        </div>
      </div>
      </div>
    </div>

    <!-- 右侧操作面板 -->
    <div class="right-panel">
      <!-- 摄像头列表 - 缩小并添加滚动 -->
      <div class="camera-list-container">
        <div class="panel-header">
          <h3>摄像头列表</h3>
          <el-tag size="small" :type="cameraStatusConnected ? 'success' : 'warning'">
            {{ cameraStatusConnected ? '状态已连接' : '状态重连中' }}
          </el-tag>
          <div class="search-box">
            <el-input v-model="searchKeyword" placeholder="搜索摄像头" clearable @keyup.enter="searchCameras" @clear="getCameraData">
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
                <RailSignal class="rail-table-signal" :state="cameraRailState(camera.status)" />
              </div>
              <div class="camera-actions">
                <el-button
                    type="primary"
                    size="small"
                    :icon="isDisplayed(camera.id) ? 'VideoPlay' : 'VideoPlay'"
                    :disabled="!isCameraOnline(camera)"
                    @click.stop="toggleCameraDisplay(camera)"
                    circle
                ></el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 设备能力自适应控制面板 -->
      <div class="ptz-control-panel" v-if="currentCamera">
        <div class="panel-header">
          <h3>{{ supportsMechanicalPTZ ? '云台控制' : '画面控制' }} - {{ currentCamera.name }}</h3>
        </div>

        <div class="ptz-container">
          <div v-if="!supportsMechanicalPTZ" class="device-capability-note">
            固定枪机：不支持机械云台、光学变倍、聚焦和光圈；可使用数字缩放、截图与录像。
          </div>

          <div v-if="supportsMechanicalPTZ" class="step-selector">
            <span class="step-label">云台步长</span>
            <el-select v-model="step" style="width: 90px;" size="small">
              <el-option v-for="n in 8" :key="n" :label="n" :value="n"></el-option>
            </el-select>
          </div>

          <!-- 方向键盘：mousedown 开始运动，mouseup / mouseleave 停止，防止鼠标拖出按钮后云台失控 -->
          <div v-if="supportsMechanicalPTZ" class="ptz-dpad">
            <button class="dpad-btn" title="左上" @mousedown="onPTZDown('LeftUp')" @mouseup="onPTZUp('LeftUp')" @mouseleave="onPTZLeave('LeftUp')">
              <el-icon class="rot-45"><ArrowUp/></el-icon>
            </button>
            <button class="dpad-btn" title="上" @mousedown="onPTZDown('Up')" @mouseup="onPTZUp('Up')" @mouseleave="onPTZLeave('Up')">
              <el-icon><ArrowUp/></el-icon>
            </button>
            <button class="dpad-btn" title="右上" @mousedown="onPTZDown('RightUp')" @mouseup="onPTZUp('RightUp')" @mouseleave="onPTZLeave('RightUp')">
              <el-icon class="rot-135"><ArrowUp/></el-icon>
            </button>
            <button class="dpad-btn" title="左" @mousedown="onPTZDown('Left')" @mouseup="onPTZUp('Left')" @mouseleave="onPTZLeave('Left')">
              <el-icon><ArrowLeft/></el-icon>
            </button>
            <button class="dpad-center" title="回到初始位置（需球机支持）" @click="onGotoPreset">
              <el-icon><Aim/></el-icon>
            </button>
            <button class="dpad-btn" title="右" @mousedown="onPTZDown('Right')" @mouseup="onPTZUp('Right')" @mouseleave="onPTZLeave('Right')">
              <el-icon><ArrowRight/></el-icon>
            </button>
            <button class="dpad-btn" title="左下" @mousedown="onPTZDown('LeftDown')" @mouseup="onPTZUp('LeftDown')" @mouseleave="onPTZLeave('LeftDown')">
              <el-icon class="rot--45"><ArrowLeft/></el-icon>
            </button>
            <button class="dpad-btn" title="下" @mousedown="onPTZDown('Down')" @mouseup="onPTZUp('Down')" @mouseleave="onPTZLeave('Down')">
              <el-icon><ArrowDown/></el-icon>
            </button>
            <button class="dpad-btn" title="右下" @mousedown="onPTZDown('RightDown')" @mouseup="onPTZUp('RightDown')" @mouseleave="onPTZLeave('RightDown')">
              <el-icon class="rot--135"><ArrowLeft/></el-icon>
            </button>
          </div>

          <!-- 数字缩放：所有摄像头均可用，固定枪机不会发送无效云台指令 -->
          <div class="ptz-functions">
            <div class="func-row">
              <span class="func-label">画面缩放</span>
              <div class="func-btns">
                <button class="func-btn" @click="adjustDigitalZoom(-1)">
                  <el-icon><ZoomOut/></el-icon>缩小
                </button>
                <button class="func-btn" @click="adjustDigitalZoom(1)">
                  <el-icon><ZoomIn/></el-icon>放大
                </button>
              </div>
            </div>
          </div>

          <!-- 仅支持云台的设备显示机械控制 -->
          <div v-if="supportsMechanicalPTZ" class="ptz-functions">
            <div class="func-row">
              <span class="func-label">变倍</span>
              <div class="func-btns">
                <button class="func-btn" @mousedown="onPTZDown('ZoomWide')" @mouseup="onPTZUp('ZoomWide')" @mouseleave="onPTZLeave('ZoomWide')">
                  <el-icon><ZoomOut/></el-icon>拉远
                </button>
                <button class="func-btn" @mousedown="onPTZDown('ZoomTele')" @mouseup="onPTZUp('ZoomTele')" @mouseleave="onPTZLeave('ZoomTele')">
                  <el-icon><ZoomIn/></el-icon>拉近
                </button>
              </div>
            </div>
            <div class="func-row">
              <span class="func-label">聚焦</span>
              <div class="func-btns">
                <button class="func-btn" @mousedown="onPTZDown('FocusFar')" @mouseup="onPTZUp('FocusFar')" @mouseleave="onPTZLeave('FocusFar')">
                  <span class="func-sign">−</span>远焦
                </button>
                <button class="func-btn" @mousedown="onPTZDown('FocusNear')" @mouseup="onPTZUp('FocusNear')" @mouseleave="onPTZLeave('FocusNear')">
                  <span class="func-sign">＋</span>近焦
                </button>
              </div>
            </div>
            <div class="func-row">
              <span class="func-label">光圈</span>
              <div class="func-btns">
                <button class="func-btn" @mousedown="onPTZDown('IrisSmall')" @mouseup="onPTZUp('IrisSmall')" @mouseleave="onPTZLeave('IrisSmall')">
                  <span class="func-sign">−</span>缩小
                </button>
                <button class="func-btn" @mousedown="onPTZDown('IrisLarge')" @mouseup="onPTZUp('IrisLarge')" @mouseleave="onPTZLeave('IrisLarge')">
                  <span class="func-sign">＋</span>放大
                </button>
              </div>
            </div>
          </div>

          <!-- 截图 / 录制 / 关闭：等宽语义色按钮 -->
          <div class="ptz-actions">
            <button class="action-btn act-capture" @click="playerCapture">
              <el-icon><Camera/></el-icon>截图
            </button>
            <button class="action-btn act-record" :class="{ 'is-recording': isRecording }" @click="toggleRecord">
              <span v-if="isRecording" class="rec-dot"></span>
              <el-icon v-else><VideoPlay/></el-icon>
              {{ isRecording ? '停止录制' : '开始录制' }}
            </button>
            <button class="action-btn act-close" @click="playerStop">
              <el-icon><CircleClose/></el-icon>关闭视频
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import RailSignal from '@/components/RailSignal.vue'
import { cameraRailState } from '@/utils/railPresentation'
import {ref, reactive, computed, onMounted, onUnmounted, nextTick} from 'vue';
import {
  Search,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Aim,
  Camera,
  ZoomIn,
  ZoomOut,
  VideoPlay,
  CircleClose,
  FullScreen
} from '@element-plus/icons-vue';
import {ElMessage} from 'element-plus';
import {getAllCameras, searchCamera, ptzControl, gotoPreset} from "@/http/api/camera.js";
import {uploadRecording} from "@/http/api/recording.js";
import {ensurePlayerControlLoaded} from '@/utils/playerControlLoader';
import {subscribeCameraStatus} from '@/services/cameraStatus';

// 摄像头列表
const cameraList = reactive([]);
const loadingCameras = ref(false);
const cameraLoadError = ref('');
const cameraStatusConnected = ref(false);
const searchKeyword = ref('');
const step = ref(1);
const currentCamera = ref(null);
const displayedCameras = reactive([]);
const canvasElements = ref([]);
const videoElements = ref([]);
const playerInstances = reactive({});
let componentUnmounted = false;
const isRecording = ref(false);
const fullscreenCamera = ref(null);
// camera.type：0 为球机，1 为枪机。枪机仅提供浏览器端数字缩放。
const supportsMechanicalPTZ = computed(() => {
  return Boolean(currentCamera.value) && Number(currentCamera.value.type) !== 1;
});
const isCameraOnline = (camera) => String(camera?.status) === '0';

// 获取所有摄像头数据
const getCameraData = async () => {
  loadingCameras.value = true;
  cameraLoadError.value = '';
  try {
    const response = await getAllCameras();
    cameraList.splice(0, cameraList.length, ...response.data);
  } catch (error) {
    console.error('获取摄像头列表失败:', error);
    cameraLoadError.value = '摄像头列表加载失败，请检查后端服务后重试。';
  } finally {
    loadingCameras.value = false;
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
  if (!isCameraOnline(camera)) {
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
    try {
      await initPlayer(camera);
    } catch (error) {
      if (componentUnmounted) return;
      const index = displayedCameras.findIndex(cam => cam.id === camera.id);
      if (index !== -1) displayedCameras.splice(index, 1);
      if (currentCamera.value?.id === camera.id) currentCamera.value = null;
      ElMessage.error(error.message || '播放器启动失败，请检查服务和摄像头连接');
    }
  }
};

// 初始化视频播放器
const initPlayer = async (camera) => {
  await ensurePlayerControlLoaded();
  if (componentUnmounted || !displayedCameras.some(cam => cam.id === camera.id)) return;
  const canvasId = `canvas-${camera.id}`;
  const videoId = `video-${camera.id}`;

  const canvasElement = document.getElementById(canvasId);
  const videoElement = document.getElementById(videoId);

  if (!canvasElement || !videoElement) {
    throw new Error('未找到视频画布，请重新打开该摄像头');
  }

  const options = {
    wsURL: 'ws://' + camera.ip + '/rtspoverwebsocket',
    // subtype=1 拉子码流（720p）：WASM 软解码 4MP 主码流跟不上帧率会导致延迟持续累积，子码流可显著降低延迟
    rtspURL: 'rtsp://' + camera.ip + '/cam/realmonitor?channel=1&subtype=1&proto=Private3',
    username: camera.username,
    password: camera.password,
    lessRateCanvas: true // 低码率渲染模式，降低渲染端开销
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

// 云台控制（走后端标准化接口，mousedown 发开始指令、mouseup/mouseleave 发停止指令）
// pressingCode 记录当前按住的指令：只有 mouseleave 的是正在按住的按钮才补发停止，防止云台失控
const pressingCode = ref(null);

// 数字变倍状态：滚轮缩放 + 拖拽平移，作用于视频 canvas 外层容器的 CSS transform
const zoomState = reactive({
  zoomLevel: 1.0,
  panX: 0,
  panY: 0
});
const ZOOM_MIN = 1.0;
const ZOOM_MAX = 4.0;
const ZOOM_STEP = 0.3;
let panning = false;
let panStart = { x: 0, y: 0 };

// 变倍按钮同时触发 SDK 光学变倍指令 + 前端数字变倍，兼容枪机（无光学变倍）和球机（有光学变倍）
// 球机走光学变倍为主、数字变倍辅助；枪机完全靠数字变倍实现视觉放大
const onPTZDown = (code) => {
  pressingCode.value = code;
  onHandlePTZ(code, false);
  // 变倍+：拉近 → 数字变倍增大；变倍-：拉远 → 数字变倍减小
  if (code === 'ZoomTele') {
    zoomState.zoomLevel = Math.min(ZOOM_MAX, zoomState.zoomLevel + ZOOM_STEP);
  } else if (code === 'ZoomWide') {
    zoomState.zoomLevel = Math.max(ZOOM_MIN, zoomState.zoomLevel - ZOOM_STEP);
    if (zoomState.zoomLevel <= 1) { zoomState.panX = 0; zoomState.panY = 0; }
  }
};

const onPTZUp = (code) => {
  if (pressingCode.value === code) pressingCode.value = null;
  onHandlePTZ(code, true);
};

const onPTZLeave = (code) => {
  if (pressingCode.value === code) {
    pressingCode.value = null;
    onHandlePTZ(code, true);
  }
};

// 跳转预置点：回到摄像头初始位置（使用 camera 表 initViewPoint）
const onGotoPreset = () => {
  if (!currentCamera.value) {
    ElMessage.warning('请先选择一个摄像头');
    return;
  }
  gotoPreset(currentCamera.value.id, null, currentCamera.value.channel || 0)
    .then(res => {
      if (res.data && res.data.success) {
        ElMessage.success(res.data.msg || '已跳转至初始位置');
      } else {
        ElMessage.warning(res.data?.msg || '跳转失败');
      }
    })
    .catch(() => {
      ElMessage.error('跳转预置点请求失败');
    });
};

// 滚轮缩放：以鼠标位置为锚点缩放
const onWheelZoom = (e) => {
  if (!currentCamera.value) return;
  const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
  const newLevel = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, zoomState.zoomLevel + delta));
  if (newLevel === zoomState.zoomLevel) return;
  const rect = e.currentTarget.getBoundingClientRect();
  const mx = e.clientX - rect.left - rect.width / 2;
  const my = e.clientY - rect.top - rect.height / 2;
  const ratio = newLevel / zoomState.zoomLevel;
  zoomState.panX = mx - (mx - zoomState.panX) * ratio;
  zoomState.panY = my - (my - zoomState.panY) * ratio;
  zoomState.zoomLevel = newLevel;
};

// 拖拽平移（仅 zoomLevel > 1 时生效）
const onPanStart = (e) => {
  if (zoomState.zoomLevel <= 1) return;
  if (e.target.closest('button')) return;
  panning = true;
  panStart = { x: e.clientX - zoomState.panX, y: e.clientY - zoomState.panY };
  e.currentTarget.style.cursor = 'grabbing';
};
const onPanMove = (e) => {
  if (!panning) return;
  zoomState.panX = e.clientX - panStart.x;
  zoomState.panY = e.clientY - panStart.y;
};
const onPanEnd = (e) => {
  if (!panning) return;
  panning = false;
  if (e && e.currentTarget) e.currentTarget.style.cursor = '';
};

const resetZoom = () => {
  zoomState.zoomLevel = 1.0;
  zoomState.panX = 0;
  zoomState.panY = 0;
};

const adjustDigitalZoom = (direction) => {
  const nextLevel = Math.min(
    ZOOM_MAX,
    Math.max(ZOOM_MIN, zoomState.zoomLevel + direction * ZOOM_STEP)
  );
  zoomState.zoomLevel = nextLevel;
  if (nextLevel <= ZOOM_MIN) {
    zoomState.panX = 0;
    zoomState.panY = 0;
  }
};

const onHandlePTZ = (type, isStop) => {
  if (!currentCamera.value) return;
  if (!supportsMechanicalPTZ.value) {
    ElMessage.warning('当前固定枪机不支持机械云台控制');
    return;
  }

  ptzControl({
    cameraId: currentCamera.value.id,
    code: type,
    stop: isStop,
    speed: step.value,
    channel: currentCamera.value.channel || 0
  }).then(res => {
    if (res.data && res.data.success === false) {
      ElMessage.warning(res.data.msg || '云台指令下发失败');
    }
  }).catch(() => {
    ElMessage.error('云台控制请求失败，请检查摄像头是否在线');
  });
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
// 大华 WebSDK 的 startRecord 有缺陷：开始时因预览连接已存在而跳过（录制从未启动），
// 停止时却无条件断开预览 WebSocket 导致黑屏。因此改用 MediaRecorder 录制播放 canvas，
// 停止时先上传系统录像库；失败时下载到浏览器默认下载目录。
let mediaRecorder = null;
let recordedChunks = [];
let recordingContext = null;

const toggleRecord = () => {
  if (!currentCamera.value || !playerInstances[currentCamera.value.id]) {
    ElMessage.warning('请先选择一个在线摄像头');
    return;
  }

  if (isRecording.value) {
    stopRecording();
  } else {
    startRecording();
  }
};

const startRecording = () => {
  const canvas = document.getElementById(`canvas-${currentCamera.value.id}`);
  if (!canvas) {
    ElMessage.error('找不到播放画面，无法录制');
    return;
  }
  let stream;
  try {
    stream = canvas.captureStream(25);
  } catch (error) {
    console.error('captureStream 失败:', error);
    ElMessage.error('当前浏览器不支持画面录制');
    return;
  }
  // 优先 mp4（Chrome 126+ 支持），否则回退 webm
  const mimeCandidates = ['video/mp4;codecs=avc1', 'video/mp4', 'video/webm;codecs=vp9', 'video/webm'];
  const mimeType = mimeCandidates.find(m => window.MediaRecorder && MediaRecorder.isTypeSupported(m));
  let recorder;
  try {
    recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
  } catch (error) {
    console.error('创建 MediaRecorder 失败:', error);
    ElMessage.error('当前浏览器不支持视频录制');
    return;
  }
  mediaRecorder = recorder;
  recordedChunks = [];
  recordingContext = {
    cameraId: Number(currentCamera.value.id),
    cameraName: currentCamera.value.name || `摄像头${currentCamera.value.id}`,
    startedAt: new Date().toISOString()
  };
  recorder.ondataavailable = (e) => {
    if (e.data && e.data.size > 0) recordedChunks.push(e.data);
  };
  recorder.onstop = () => {
    const context = recordingContext;
    const type = recorder.mimeType || 'video/webm';
    const ext = type.includes('mp4') ? 'mp4' : 'webm';
    const ts = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    const name = `录制_${context?.cameraName || '摄像头'}_${ts.getFullYear()}${pad(ts.getMonth() + 1)}${pad(ts.getDate())}_${pad(ts.getHours())}${pad(ts.getMinutes())}${pad(ts.getSeconds())}.${ext}`;
    const blob = new Blob(recordedChunks, { type });
    // 手动录像仍带有摄像头和起止时间，回放页可据此定位覆盖告警时刻的文件。
    uploadRecording(blob, name, {
      cameraId: context?.cameraId,
      startedAt: context?.startedAt,
      endedAt: new Date().toISOString(),
      source: 'manual'
    })
      .then(res => {
        if (res.data && res.data.success) {
          ElMessage.success(`录制完成，已保存到"视频回放"页面：${res.data.filename}`);
        } else {
          throw new Error(res.data?.msg || '上传失败');
        }
      })
      .catch((error) => {
        // 上传失败时降级为本地下载，避免录像丢失
        downloadBlob(blob, name);
        const reason = error?.message || '未知错误';
        console.error('录像上传失败:', error);
        ElMessage.warning({
          message: `上传服务器失败（${reason}），已下载到本地：${name}`,
          duration: 9000
        });
      });
    recordedChunks = [];
    if (mediaRecorder === recorder) mediaRecorder = null;
    recordingContext = null;
  };
  recorder.start(1000);
  isRecording.value = true;
  ElMessage.success('开始录制');
};

const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  } else {
    mediaRecorder = null;
  }
  isRecording.value = false;
};

// 上传失败时的降级方案：本地下载保存
const downloadBlob = (blob, name) => {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};

// 摄像头功能 - 停止播放
const playerStop = () => {
  if (!currentCamera.value || !playerInstances[currentCamera.value.id]) {
    ElMessage.warning('请先选择一个在线摄像头');
    return;
  }

  try {
    // 录制中先停止录制，避免 canvas 被移除后录制流中断丢失文件
    if (isRecording.value) {
      stopRecording();
    }
    playerInstances[currentCamera.value.id].close();
    delete playerInstances[currentCamera.value.id];

    const cameraIndex = displayedCameras.findIndex(cam => cam.id === currentCamera.value.id);
    if (cameraIndex !== -1) {
      displayedCameras.splice(cameraIndex, 1);
    }

    resetZoom();
    currentCamera.value = null;
    ElMessage.success('已关闭视频');
  } catch (error) {
    console.error('关闭视频失败:', error);
    ElMessage.error('关闭视频失败');
  }
};

let unsubscribeCameraStatus = null;

const subscribeToCameraStatus = () => {
  unsubscribeCameraStatus = subscribeCameraStatus(({type, updates}) => {
    if (type === 'update') updateCameraStatus(updates);
    if (type === 'connected') {
      cameraStatusConnected.value = true;
      getCameraData();
    }
    if (type === 'connecting' || type === 'disconnected' || type === 'reconnecting' || type === 'error') {
      cameraStatusConnected.value = false;
    }
  });
};

// 更新摄像头状态
const updateCameraStatus = (updates) => {
  const normalizedUpdates = Array.isArray(updates) ? updates : [updates];
  normalizedUpdates.forEach(updatedCamera => {
    if (!updatedCamera || updatedCamera.id == null) return;
    const index = cameraList.findIndex(c => Number(c.id) === Number(updatedCamera.id));
    if (index !== -1) {
      cameraList[index].status = updatedCamera.status;
    }
    const displayed = displayedCameras.find(camera => Number(camera.id) === Number(updatedCamera.id));
    if (displayed) displayed.status = updatedCamera.status;
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
  componentUnmounted = false;
  getCameraData();
  subscribeToCameraStatus();

  // 添加全屏变化监听
  document.addEventListener('fullscreenchange', handleFullscreenChange);
});

onUnmounted(() => {
  componentUnmounted = true;
  // 关闭所有播放实例
  Object.values(playerInstances).forEach(player => {
    try {
      player.close();
    } catch (e) {
      console.error('关闭播放器失败:', e);
    }
  });

  if (unsubscribeCameraStatus) {
    unsubscribeCameraStatus();
    unsubscribeCameraStatus = null;
  }
  cameraStatusConnected.value = false;

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
  padding: 10px;
  overflow-y: auto;
  height: 100%;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  grid-auto-rows: minmax(240px, 300px);
  gap: 10px;
}

.video-empty {
  min-height: 240px;
  height: 100%;
  display: grid;
  place-content: center;
  gap: 12px;
  padding: 24px;
  border: 1px dashed #c8d6e5;
  border-radius: 10px;
  color: #5b6b7d;
  background: #f8fbff;
  text-align: center;
}

.video-error {
  color: #b42318;
  background: #fff7f6;
  border-color: #f0b6af;
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

/* 视频项：放大后允许拖拽平移 */
.video-item.is-zoomed {
  cursor: grab;
}

/* 缩放平移容器：CSS transition 让缩放/平移有平滑动画 */
.zoom-viewport {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.12s ease-out;
  will-change: transform;
}

.zoom-viewport .video-canvas,
.zoom-viewport .video-element {
  position: absolute;
  top: 0;
  left: 0;
  object-fit: cover;
}

/* 缩放指示器 */
.zoom-badge {
  display: inline-block;
  padding: 1px 8px;
  margin-right: 6px;
  border-radius: 10px;
  background: rgba(64, 158, 255, 0.15);
  color: #409eff;
  font-size: 12px;
  font-weight: 600;
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

.device-capability-note {
  padding: 10px;
  border: 1px solid #d9ecff;
  border-radius: 6px;
  background: #ecf5ff;
  color: #409eff;
  font-size: 13px;
  line-height: 1.5;
}

.step-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-label {
  font-size: 13px;
  color: #909399;
}

/* 方向键盘：52px 圆形按钮，等距网格 */
.ptz-dpad {
  display: grid;
  grid-template-columns: repeat(3, 52px);
  grid-template-rows: repeat(3, 52px);
  gap: 8px;
  justify-content: center;
}

.dpad-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #dcdfe6;
  border-radius: 50%;
  background: #f5f7fa;
  color: #606266;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  transition: all 0.15s ease;
  user-select: none;
}

.dpad-btn:hover {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
  transform: translateY(-1px);
}

.dpad-btn:active {
  transform: scale(0.9);
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.2);
}

/* 斜向箭头：直箭头旋转实现，规避斜向图标缺失导致显示空白 */
.rot-45 { transform: rotate(45deg); }
.rot-135 { transform: rotate(135deg); }
.rot--45 { transform: rotate(-45deg); }
.rot--135 { transform: rotate(-135deg); }

/* 中心回中按钮：主色渐变，视觉锚点 */
.dpad-center {
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #2f6fd8);
  color: #fff;
  font-size: 18px;
  cursor: default;
  padding: 0;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.35);
}

/* 变倍 / 聚焦 / 光圈：左侧标签 + 对称按钮 */
.ptz-functions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.func-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.func-label {
  width: 42px;
  flex: none;
  font-size: 13px;
  color: #909399;
  text-align: right;
}

.func-btns {
  flex: 1;
  display: flex;
  gap: 8px;
}

.func-btn {
  flex: 1;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background: #fff;
  color: #606266;
  font-size: 13px;
  cursor: pointer;
  padding: 0;
  transition: all 0.15s ease;
  user-select: none;
}

.func-btn:hover {
  border-color: #409eff;
  color: #409eff;
  background: #ecf5ff;
}

.func-btn:active {
  transform: scale(0.95);
  background: #d9ecff;
}

.func-sign {
  font-weight: bold;
}

/* 截图 / 录制 / 关闭：等宽语义色按钮 */
.ptz-actions {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}

.action-btn {
  flex: 1;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  color: #fff;
  cursor: pointer;
  padding: 0;
  transition: all 0.15s ease;
  user-select: none;
}

.act-capture { background: #409eff; }
.act-capture:hover { background: #66b1ff; box-shadow: 0 4px 12px rgba(64, 158, 255, 0.35); }

.act-record { background: #67c23a; }
.act-record:hover { background: #85cf60; box-shadow: 0 4px 12px rgba(103, 194, 58, 0.35); }

.act-record.is-recording { background: #f56c6c; }
.act-record.is-recording:hover { background: #f78989; box-shadow: 0 4px 12px rgba(245, 108, 108, 0.35); }

.act-close { background: #909399; }
.act-close:hover { background: #a6a9ad; box-shadow: 0 4px 12px rgba(144, 147, 153, 0.35); }

.action-btn:active {
  transform: scale(0.95);
  filter: brightness(0.92);
}

/* 录制中红点闪烁 */
.rec-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #fff;
  animation: rec-blink 1s ease-in-out infinite;
}

@keyframes rec-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
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

@media (max-width: 1100px) {
  .right-panel { width: 320px; }
  .video-grid { grid-template-columns: 1fr; grid-auto-rows: minmax(240px, 1fr); }
}

@media (max-width: 760px) {
  .monitoring-screen { flex-direction: column; overflow-y: auto; }
  .video-container { flex: 0 0 auto; min-height: 52%; height: auto; }
  .video-grid { grid-auto-rows: 240px; }
  .right-panel { width: 100%; height: auto; min-height: 420px; border-left: 0; border-top: 1px solid #dcdfe6; }
  .camera-list-container { height: 180px; }
  .ptz-control-panel { max-height: 520px; }
  .ptz-actions { position: sticky; bottom: 0; padding-top: 8px; background: #fff; }
}

.monitoring-screen { padding-top:72px;background:#edf4f9; }
.monitor-page-head { position:absolute;top:0;left:0;right:0;z-index:12;height:72px;display:flex;align-items:center;justify-content:space-between;padding:10px 20px;background:linear-gradient(90deg,#f5faff,#eef6fb);border-bottom:1px solid #cadde9; }
.monitor-page-head span { color:#167eaa;font-size:10px;font-weight:700;letter-spacing:1.4px; }
.monitor-page-head h1 { margin:3px 0 0;color:#173d5b;font-size:22px;line-height:1.15; }
.monitor-page-head p { color:#6e879a;font-size:12px; }
.video-container { min-width:0;padding:16px 18px; }
.video-grid { grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr));grid-auto-rows:auto;gap:16px;align-content:start; }
.video-item { height:auto;aspect-ratio:16/9;border:0;border-radius:8px;box-shadow:0 10px 26px rgba(20,55,82,.12); }
.video-item.active { border:2px solid #37b6d4; }
.zoom-viewport .video-canvas,.zoom-viewport .video-element { object-fit:contain; }
.right-panel { width:clamp(300px,25vw,380px);height:100%;border-left:1px solid #c7dce9;box-shadow:-5px 0 20px rgba(20,55,82,.045); }
.camera-list-container { height:min(32vh,320px); }
.panel-header { padding:14px 16px;border-bottom:1px solid #e2ecf3; }
@media (max-width:900px) { .monitor-page-head p { display:none; } .right-panel { width:300px; } }
</style>
