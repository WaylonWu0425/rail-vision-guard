<template>
  <div class="surveillance-dashboard">
    <!-- 视频监控网格 -->
    <div class="video-grid-area">
      <div
          v-for="camera in activeCameraStreams"
          :key="camera.id"
          class="camera-viewport"
          :class="{
          'active': selectedCameraControl?.id === camera.id,
          'fullscreen-mode': fullscreenCamera?.id === camera.id
        }"
          :data-camera-identifier="camera.id"
      >
        <div class="camera-viewport-header">
          <div class="camera-title-section">
            <span class="camera-name">{{ camera.name }}</span>
            <el-tag
                size="small"
                :type="camera.status === 0 ? 'success' : 'danger'"
                class="status-indicator"
            >
              {{ camera.status === 0 ? '在线' : '离线' }}
            </el-tag>
          </div>

          <div class="camera-action-bar">
            <el-button
                type="primary"
                size="small"
                @click="activateCameraControl(camera)"
                :disabled="!camera.status"
                plain
            >
              云台控制
            </el-button>
            <el-button
                type="info"
                size="small"
                @click="toggleFullscreenView(camera)"
                :icon="FullScreen"
                circle
            />
          </div>
        </div>

        <canvas
            ref="videoCanvasRefs"
            :id="`video-canvas-${camera.id}`"
            class="video-canvas-layer"
        />
        <video
            ref="videoPlayerRefs"
            :id="`video-player-${camera.id}`"
            class="video-player-layer"
        />
      </div>
    </div>

    <!-- 控制侧边栏 -->
    <div class="control-sidebar">
      <!-- 摄像头选择器 -->
      <div class="camera-selector-panel">
        <div class="panel-header-section">
          <h3 class="panel-title">监控设备列表</h3>
          <div class="search-toolbar">
            <el-input
                v-model="cameraSearchKeyword"
                placeholder="输入设备名称搜索"
                clearable
                @clear="refreshCameraList"
                @input="debouncedSearch"
            >
              <template #suffix>
                <el-icon @click="performCameraSearch">
                  <Search />
                </el-icon>
              </template>
            </el-input>
          </div>
        </div>

        <div class="camera-list-scrollable">
          <div class="camera-selection-list">
            <div
                v-for="camera in filteredCameraList"
                :key="camera.id"
                class="camera-selection-item"
                :class="{
                'selected': isCameraActive(camera.id),
                'offline': camera.status !== 0
              }"
                @click="toggleCameraStream(camera)"
            >
              <div class="camera-item-info">
                <span class="camera-display-name">{{ camera.name }}</span>
                <div class="camera-status-indicator">
                  <el-tag
                      size="small"
                      :type="camera.status === 0 ? 'success' : 'danger'"
                      class="status-badge"
                  >
                    {{ camera.status === 0 ? '在线' : '离线' }}
                  </el-tag>
                </div>
              </div>

              <div class="camera-item-actions">
                <el-button
                    size="small"
                    :type="isCameraActive(camera.id) ? 'success' : 'primary'"
                    :icon="VideoPlay"
                    :disabled="camera.status !== 0"
                    @click.stop="toggleCameraStream(camera)"
                    circle
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 云台控制面板 -->
      <div class="ptz-control-panel" v-if="selectedCameraControl">
        <div class="panel-header-section">
          <h3 class="panel-title">云台控制台</h3>
          <div class="selected-camera-info">
            <span class="camera-label">当前设备：</span>
            <span class="camera-value">{{ selectedCameraControl.name }}</span>
          </div>
        </div>

        <div class="ptz-control-area">
          <!-- 步长选择 -->
          <div class="control-step-selector">
            <span class="step-label">移动步长：</span>
            <el-select v-model="ptzStepValue" style="width: 100px;">
              <el-option
                  v-for="step in PTZ_STEP_OPTIONS"
                  :key="step"
                  :label="`${step}`"
                  :value="step"
              />
            </el-select>
          </div>

          <!-- 方向控制区 -->
          <div class="directional-control-grid">
            <el-button
                class="direction-control-btn"
                @mousedown="initiatePTZAction('LeftUp', false)"
                @mouseup="initiatePTZAction('LeftUp', true)"
            >
              <el-icon>
                <ArrowUpLeft />
              </el-icon>
            </el-button>

            <el-button
                class="direction-control-btn"
                @mousedown="initiatePTZAction('Up', false)"
                @mouseup="initiatePTZAction('Up', true)"
            >
              <el-icon>
                <ArrowUp />
              </el-icon>
            </el-button>

            <el-button
                class="direction-control-btn"
                @mousedown="initiatePTZAction('RightUp', false)"
                @mouseup="initiatePTZAction('RightUp', true)"
            >
              <el-icon>
                <ArrowUpRight />
              </el-icon>
            </el-button>

            <el-button
                class="direction-control-btn"
                @mousedown="initiatePTZAction('Left', false)"
                @mouseup="initiatePTZAction('Left', true)"
            >
              <el-icon>
                <ArrowLeft />
              </el-icon>
            </el-button>

            <el-button
                class="direction-control-btn center-control-btn"
                @click="resetCameraView"
            >
              中心复位
            </el-button>

            <el-button
                class="direction-control-btn"
                @mousedown="initiatePTZAction('Right', false)"
                @mouseup="initiatePTZAction('Right', true)"
            >
              <el-icon>
                <ArrowRight />
              </el-icon>
            </el-button>

            <el-button
                class="direction-control-btn"
                @mousedown="initiatePTZAction('LeftDown', false)"
                @mouseup="initiatePTZAction('LeftDown', true)"
            >
              <el-icon>
                <ArrowDownLeft />
              </el-icon>
            </el-button>

            <el-button
                class="direction-control-btn"
                @mousedown="initiatePTZAction('Down', false)"
                @mouseup="initiatePTZAction('Down', true)"
            >
              <el-icon>
                <ArrowDown />
              </el-icon>
            </el-button>

            <el-button
                class="direction-control-btn"
                @mousedown="initiatePTZAction('RightDown', false)"
                @mouseup="initiatePTZAction('RightDown', true)"
            >
              <el-icon>
                <ArrowDownRight />
              </el-icon>
            </el-button>
          </div>

          <!-- 镜头功能控制 -->
          <div class="lens-function-controls">
            <div class="function-control-row">
              <el-button
                  @mousedown="initiatePTZAction('ZoomWide', false)"
                  @mouseup="initiatePTZAction('ZoomWide', true)"
                  class="function-control-btn"
              >
                缩小变焦
              </el-button>
              <el-button
                  @mousedown="initiatePTZAction('ZoomTele', false)"
                  @mouseup="initiatePTZAction('ZoomTele', true)"
                  class="function-control-btn"
              >
                放大变焦
              </el-button>
            </div>

            <div class="function-control-row">
              <el-button
                  @mousedown="initiatePTZAction('FocusFar', false)"
                  @mouseup="initiatePTZAction('FocusFar', true)"
                  class="function-control-btn"
              >
                远景聚焦
              </el-button>
              <el-button
                  @mousedown="initiatePTZAction('FocusNear', false)"
                  @mouseup="initiatePTZAction('FocusNear', true)"
                  class="function-control-btn"
              >
                近景聚焦
              </el-button>
            </div>

            <div class="function-control-row">
              <el-button
                  @mousedown="initiatePTZAction('IrisSmall', false)"
                  @mouseup="initiatePTZAction('IrisSmall', true)"
                  class="function-control-btn"
              >
                缩小光圈
              </el-button>
              <el-button
                  @mousedown="initiatePTZAction('IrisLarge', false)"
                  @mouseup="initiatePTZAction('IrisLarge', true)"
                  class="function-control-btn"
              >
                放大光圈
              </el-button>
            </div>
          </div>

          <!-- 媒体操作区 -->
          <div class="media-operation-panel">
            <el-button
                type="primary"
                @click="captureVideoFrame"
                :loading="captureInProgress"
            >
              画面截图
            </el-button>

            <el-button
                type="success"
                @click="toggleRecordingState"
                :loading="recordingInProgress"
                :class="{ 'recording-active': isRecording }"
            >
              {{ isRecording ? '停止录制' : '开始录制' }}
            </el-button>

            <el-button
                type="warning"
                @click="terminateVideoStream"
            >
              关闭画面
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  ref,
  reactive,
  computed,
  onMounted,
  onUnmounted,
  nextTick,
  watch
} from 'vue'
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
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllCameras, searchCamera } from "@/http/api/camera.js"
import { useDebounceFn } from '@vueuse/core'

// ==================== 类型定义 ====================
/**
 * @typedef {Object} CameraDevice
 * @property {number} id - 摄像头ID
 * @property {string} name - 摄像头名称
 * @property {number} status - 摄像头状态 (0: 在线, 1: 离线)
 * @property {string} ip - IP地址
 * @property {number} port - 端口号
 * @property {string} username - 用户名
 * @property {string} password - 密码
 * @property {number} channel - 通道号
 */

/**
 * @typedef {Object} PlayerInstance
 * @property {Function} init - 初始化播放器
 * @property {Function} connect - 连接视频流
 * @property {Function} close - 关闭播放器
 * @property {Function} capture - 截图功能
 * @property {Function} startRecord - 开始/停止录制
 */

// ==================== 常量定义 ====================
const PTZ_STEP_OPTIONS = [1, 2, 3, 4, 5, 6, 7, 8]
const WS_RECONNECT_DELAY = 3000
const DEFAULT_VIDEO_GRID = { minWidth: '45%', height: '300px' }

// ==================== 响应式数据 ====================
// 设备列表
const cameraDeviceList = ref([])
const cameraSearchKeyword = ref('')
const filteredCameraList = computed(() => {
  if (!cameraSearchKeyword.value.trim()) {
    return cameraDeviceList.value
  }

  const keyword = cameraSearchKeyword.value.toLowerCase()
  return cameraDeviceList.value.filter(camera =>
      camera.name.toLowerCase().includes(keyword) ||
      camera.ip.includes(keyword)
  )
})

// 视频流状态
const activeCameraStreams = reactive([])
const videoCanvasRefs = ref([])
const videoPlayerRefs = ref([])
const videoPlayerInstances = reactive({})

// 云台控制
const selectedCameraControl = ref(null)
const ptzStepValue = ref(1)
const fullscreenCamera = ref(null)

// 录制状态
const isRecording = ref(false)
const captureInProgress = ref(false)
const recordingInProgress = ref(false)

// WebSocket连接
const cameraStatusSocket = ref(null)
const socketReconnectTimer = ref(null)

// ==================== 工具函数 ====================
/**
 * 显示通知消息
 * @param {string} message - 消息内容
 * @param {'success'|'error'|'warning'|'info'} type - 消息类型
 */
const displayNotification = (message, type = 'info') => {
  ElMessage[type](message)
}

/**
 * 格式化时间戳
 * @returns {string} 格式化后的时间字符串
 */
const getFormattedTimestamp = () => {
  return new Date().toISOString().replace(/[:.]/g, '-')
}

/**
 * 防抖搜索函数
 */
const debouncedSearch = useDebounceFn(() => {
  performCameraSearch()
}, 500)

// ==================== 摄像头数据管理 ====================
/**
 * 获取摄像头设备列表
 */
const fetchCameraDevices = async () => {
  try {
    const response = await getAllCameras()
    if (Array.isArray(response.data)) {
      cameraDeviceList.value = response.data.map(camera => ({
        ...camera,
        status: camera.status || 1
      }))
    } else {
      displayNotification('摄像头数据格式异常', 'warning')
    }
  } catch (error) {
    console.error('获取摄像头设备失败:', error)
    displayNotification('获取摄像头列表失败', 'error')
  }
}

/**
 * 搜索摄像头设备
 */
const performCameraSearch = async () => {
  const keyword = cameraSearchKeyword.value.trim()

  if (!keyword) {
    await fetchCameraDevices()
    return
  }

  try {
    const response = await searchCamera(keyword)
    if (Array.isArray(response.data)) {
      cameraDeviceList.value = response.data
    }
  } catch (error) {
    console.error('搜索摄像头失败:', error)
    displayNotification('搜索摄像头失败', 'error')
  }
}

/**
 * 刷新摄像头列表
 */
const refreshCameraList = () => {
  cameraSearchKeyword.value = ''
  fetchCameraDevices()
}

// ==================== 视频流管理 ====================
/**
 * 检查摄像头是否处于活动状态
 * @param {number} cameraId - 摄像头ID
 * @returns {boolean}
 */
const isCameraActive = (cameraId) => {
  return activeCameraStreams.some(camera => camera.id === cameraId)
}

/**
 * 切换摄像头视频流
 * @param {CameraDevice} camera - 摄像头设备
 */
const toggleCameraStream = async (camera) => {
  // 设备状态检查
  if (camera.status !== 0) {
    displayNotification('当前设备离线，无法开启视频流', 'warning')
    return
  }

  const cameraIndex = activeCameraStreams.findIndex(cam => cam.id === camera.id)

  if (cameraIndex !== -1) {
    // 关闭视频流
    await terminateSpecificCamera(camera)
  } else {
    // 开启视频流
    await activateVideoStream(camera)
  }
}

/**
 * 激活摄像头视频流
 * @param {CameraDevice} camera - 摄像头设备
 */
const activateVideoStream = async (camera) => {
  // 验证摄像头参数
  if (!camera.ip || !camera.username || !camera.password) {
    displayNotification('摄像头配置信息不完整', 'warning')
    return
  }

  try {
    // 添加到活动流列表
    activeCameraStreams.push(camera)

    // 等待DOM更新
    await nextTick()

    // 初始化播放器
    await initializeVideoPlayer(camera)

    // 设置为当前控制设备
    selectedCameraControl.value = camera

    displayNotification(`已开启 ${camera.name} 视频流`, 'success')
  } catch (error) {
    console.error('开启视频流失败:', error)

    // 清理失败的状态
    const index = activeCameraStreams.findIndex(cam => cam.id === camera.id)
    if (index !== -1) {
      activeCameraStreams.splice(index, 1)
    }

    displayNotification('开启视频流失败，请检查网络连接', 'error')
  }
}

/**
 * 初始化视频播放器
 * @param {CameraDevice} camera - 摄像头设备
 */
const initializeVideoPlayer = (camera) => {
  return new Promise((resolve, reject) => {
    try {
      const canvasElement = document.getElementById(`video-canvas-${camera.id}`)
      const videoElement = document.getElementById(`video-player-${camera.id}`)

      if (!canvasElement || !videoElement) {
        throw new Error('视频播放元素未找到')
      }

      // 检查 PlayerControl 是否可用
      if (typeof window.PlayerControl !== 'function') {
        throw new Error('视频播放器库未加载')
      }

      // 播放器配置
      const playerConfig = {
        wsURL: `ws://${camera.ip}/rtspoverwebsocket`,
        rtspURL: `rtsp://${camera.ip}/cam/realmonitor?channel=1&subtype=0&proto=Private3`,
        username: camera.username,
        password: camera.password,
        autoConnect: true
      }

      // 创建播放器实例
      const playerInstance = new window.PlayerControl(playerConfig)

      // 事件监听
      playerInstance.on('WorkerReady', () => {
        console.log(`播放器就绪: ${camera.name}`)
        playerInstance.connect()
      })

      playerInstance.on('PlayStart', () => {
        console.log(`开始播放: ${camera.name}`)
        resolve(playerInstance)
      })

      playerInstance.on('Error', (error) => {
        console.error(`播放器错误: ${camera.name}`, error)
        reject(new Error(`播放器初始化失败: ${error.message}`))
      })

      // 初始化播放器
      playerInstance.init(canvasElement, videoElement)

      // 保存实例引用
      videoPlayerInstances[camera.id] = playerInstance

    } catch (error) {
      console.error('播放器初始化异常:', error)
      reject(error)
    }
  })
}

/**
 * 终止特定摄像头视频流
 * @param {CameraDevice} camera - 摄像头设备
 */
const terminateSpecificCamera = async (camera) => {
  try {
    // 停止播放器
    if (videoPlayerInstances[camera.id]) {
      await videoPlayerInstances[camera.id].close()
      delete videoPlayerInstances[camera.id]
    }

    // 从活动流中移除
    const cameraIndex = activeCameraStreams.findIndex(cam => cam.id === camera.id)
    if (cameraIndex !== -1) {
      activeCameraStreams.splice(cameraIndex, 1)
    }

    // 清除当前控制选择
    if (selectedCameraControl.value?.id === camera.id) {
      selectedCameraControl.value = null
    }

    // 清除全屏状态
    if (fullscreenCamera.value?.id === camera.id) {
      fullscreenCamera.value = null
    }

    displayNotification(`已关闭 ${camera.name} 视频流`, 'success')

  } catch (error) {
    console.error('关闭视频流失败:', error)
    displayNotification('关闭视频流失败', 'error')
  }
}

/**
 * 激活摄像头控制
 * @param {CameraDevice} camera - 摄像头设备
 */
const activateCameraControl = (camera) => {
  if (!camera.status) {
    displayNotification('当前设备离线，无法控制', 'warning')
    return
  }

  selectedCameraControl.value = camera
}

// ==================== 云台控制 ====================
/**
 * 初始化云台控制操作
 * @param {string} controlType - 控制类型
 * @param {boolean} isStopAction - 是否为停止操作
 */
const initiatePTZAction = (controlType, isStopAction) => {
  if (!selectedCameraControl.value) {
    displayNotification('请先选择控制设备', 'warning')
    return
  }

  try {
    const controlCommand = {
      code: controlType,
      arg1: ptzStepValue.value,
      arg2: ['LeftUp', 'RightUp', 'LeftDown', 'RightDown'].includes(controlType) ? ptzStepValue.value : 0,
      arg3: 0
    }

    const actionType = isStopAction ? 'stop' : 'start'

    // 调用云台控制API
    if (typeof RPC !== 'undefined' && RPC.PTZManager) {
      RPC.PTZManager(
          actionType,
          selectedCameraControl.value.channel || 0,
          controlCommand
      )

      if (!isStopAction) {
        console.log(`云台控制: ${controlType}, 步长: ${ptzStepValue.value}`)
      }
    } else {
      console.warn('云台控制API不可用')
    }

  } catch (error) {
    console.error('云台控制失败:', error)
    displayNotification('云台控制操作失败', 'error')
  }
}

/**
 * 重置摄像头视图
 */
const resetCameraView = () => {
  if (!selectedCameraControl.value) {
    displayNotification('请先选择控制设备', 'warning')
    return
  }

  try {
    // 调用预置位复位
    if (typeof RPC !== 'undefined' && RPC.PTZManager) {
      RPC.PTZManager('preset', selectedCameraControl.value.channel || 0, {
        code: 'GotoPreset',
        arg1: 1, // 预置位1
        arg2: 0,
        arg3: 0
      })

      displayNotification('摄像头已复位到中心位置', 'success')
    }
  } catch (error) {
    console.error('摄像头复位失败:', error)
    displayNotification('摄像头复位失败', 'error')
  }
}

// ==================== 媒体操作 ====================
/**
 * 捕获视频画面
 */
const captureVideoFrame = () => {
  if (!selectedCameraControl.value || !videoPlayerInstances[selectedCameraControl.value.id]) {
    displayNotification('请先选择在线设备并开启视频流', 'warning')
    return
  }

  captureInProgress.value = true

  try {
    const timestamp = getFormattedTimestamp()
    const fileName = `surveillance_snapshot_${selectedCameraControl.value.name}_${timestamp}.jpg`

    videoPlayerInstances[selectedCameraControl.value.id].capture(fileName)

    displayNotification('画面截图已保存', 'success')
  } catch (error) {
    console.error('截图失败:', error)
    displayNotification('截图操作失败', 'error')
  } finally {
    captureInProgress.value = false
  }
}

/**
 * 切换录制状态
 */
const toggleRecordingState = async () => {
  if (!selectedCameraControl.value || !videoPlayerInstances[selectedCameraControl.value.id]) {
    displayNotification('请先选择在线设备并开启视频流', 'warning')
    return
  }

  recordingInProgress.value = true

  try {
    if (isRecording.value) {
      // 停止录制
      await videoPlayerInstances[selectedCameraControl.value.id].startRecord(false)
      isRecording.value = false
      displayNotification('视频录制已停止', 'success')
    } else {
      // 开始录制
      await videoPlayerInstances[selectedCameraControl.value.id].startRecord(true)
      isRecording.value = true
      displayNotification('开始录制视频', 'success')
    }
  } catch (error) {
    console.error('录制操作失败:', error)
    displayNotification('录制操作失败', 'error')
  } finally {
    recordingInProgress.value = false
  }
}

/**
 * 终止视频流
 */
const terminateVideoStream = async () => {
  if (!selectedCameraControl.value) {
    displayNotification('请先选择要关闭的设备', 'warning')
    return
  }

  try {
    await ElMessageBox.confirm(
        `确定要关闭 ${selectedCameraControl.value.name} 的视频流吗？`,
        '确认关闭',
        {
          confirmButtonText: '确定关闭',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    await terminateSpecificCamera(selectedCameraControl.value)

  } catch (error) {
    if (error !== 'cancel') {
      console.error('关闭确认失败:', error)
    }
  }
}

// ==================== 全屏管理 ====================
/**
 * 切换全屏视图
 * @param {CameraDevice} camera - 摄像头设备
 */
const toggleFullscreenView = (camera) => {
  if (!camera || !videoPlayerInstances[camera.id]) {
    displayNotification('无法切换该设备的全屏状态', 'warning')
    return
  }

  const viewportElement = document.querySelector(`.camera-viewport[data-camera-identifier="${camera.id}"]`)

  if (!viewportElement) {
    displayNotification('视频视图元素未找到', 'error')
    return
  }

  if (!document.fullscreenElement) {
    // 进入全屏
    viewportElement.requestFullscreen()
        .then(() => {
          fullscreenCamera.value = camera
        })
        .catch(error => {
          console.error('全屏请求失败:', error)
          displayNotification(`全屏切换失败: ${error.message}`, 'error')
        })
  } else {
    // 退出全屏
    document.exitFullscreen()
        .then(() => {
          fullscreenCamera.value = null
        })
        .catch(error => {
          console.error('退出全屏失败:', error)
          displayNotification(`退出全屏失败: ${error.message}`, 'error')
        })
  }
}

/**
 * 处理全屏变化事件
 */
const handleFullscreenChange = () => {
  if (!document.fullscreenElement) {
    fullscreenCamera.value = null
  }
}

// ==================== WebSocket 管理 ====================
/**
 * 初始化WebSocket连接
 */
const initializeStatusWebSocket = () => {
  // 关闭现有连接
  if (cameraStatusSocket.value) {
    cameraStatusSocket.value.close()
  }

  clearTimeout(socketReconnectTimer.value)

  try {
    cameraStatusSocket.value = new WebSocket("ws://localhost:8081/ws/cameraStatus")

    cameraStatusSocket.value.onopen = () => {
      console.log("设备状态WebSocket连接成功")
    }

    cameraStatusSocket.value.onmessage = (event) => {
      try {
        const statusUpdates = JSON.parse(event.data)
        if (Array.isArray(statusUpdates)) {
          updateDeviceStatus(statusUpdates)
        }
      } catch (error) {
        console.error("设备状态数据解析失败:", error)
      }
    }

    cameraStatusSocket.value.onclose = () => {
      console.log("设备状态WebSocket连接关闭")
      // 自动重连
      socketReconnectTimer.value = setTimeout(() => {
        initializeStatusWebSocket()
      }, WS_RECONNECT_DELAY)
    }

    cameraStatusSocket.value.onerror = (error) => {
      console.error("设备状态WebSocket错误:", error)
    }

  } catch (error) {
    console.error("WebSocket初始化失败:", error)
  }
}

/**
 * 更新设备状态
 * @param {Array} statusUpdates - 状态更新数组
 */
const updateDeviceStatus = (statusUpdates) => {
  statusUpdates.forEach(update => {
    const deviceIndex = cameraDeviceList.value.findIndex(device => device.id === update.id)

    if (deviceIndex !== -1) {
      // 更新设备状态
      cameraDeviceList.value[deviceIndex].status = update.status

      // 如果设备正在播放且状态变为离线，则自动关闭
      if (update.status !== 0 && isCameraActive(update.id)) {
        const cameraDevice = cameraDeviceList.value[deviceIndex]
        terminateSpecificCamera(cameraDevice).catch(console.error)
      }
    }
  })
}

// ==================== 生命周期管理 ====================
/**
 * 清理所有资源
 */
const cleanupResources = () => {
  // 停止所有视频流
  activeCameraStreams.forEach(camera => {
    if (videoPlayerInstances[camera.id]) {
      try {
        videoPlayerInstances[camera.id].close()
      } catch (error) {
        console.error(`关闭播放器 ${camera.name} 失败:`, error)
      }
    }
  })

  // 清空播放器实例
  Object.keys(videoPlayerInstances).forEach(key => {
    delete videoPlayerInstances[key]
  })

  // 清空活动流列表
  activeCameraStreams.splice(0, activeCameraStreams.length)

  // 关闭WebSocket连接
  if (cameraStatusSocket.value) {
    cameraStatusSocket.value.close()
    cameraStatusSocket.value = null
  }

  // 清除定时器
  if (socketReconnectTimer.value) {
    clearTimeout(socketReconnectTimer.value)
    socketReconnectTimer.value = null
  }
}

// ==================== 生命周期钩子 ====================
onMounted(() => {
  // 初始化摄像头列表
  fetchCameraDevices()

  // 初始化WebSocket连接
  initializeStatusWebSocket()

  // 添加全屏事件监听
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  // 清理所有资源
  cleanupResources()

  // 移除事件监听
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})

// ==================== 监听器 ====================
// 监听全屏摄像头变化
watch(fullscreenCamera, (newValue) => {
  if (newValue) {
    console.log(`进入全屏模式: ${newValue.name}`)
  } else {
    console.log('退出全屏模式')
  }
})

// 监听控制设备变化
watch(selectedCameraControl, (newValue) => {
  if (newValue) {
    console.log(`控制设备切换至: ${newValue.name}`)
  }
})
</script>

<style scoped>
.surveillance-dashboard {
  display: flex;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
  position: relative;
}

.video-grid-area {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(45%, 1fr));
  grid-auto-rows: minmax(300px, 1fr);
  gap: 12px;
  padding: 16px;
  overflow-y: auto;
  background: rgba(0, 0, 0, 0.85);
  position: relative;
}

.camera-viewport {
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.camera-viewport:hover {
  border-color: rgba(64, 158, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
}

.camera-viewport.active {
  border-color: #409eff;
  border-width: 3px;
}

.camera-viewport.fullscreen-mode {
  border-color: #67c23a;
  border-width: 3px;
}

.camera-viewport-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.8), transparent);
  color: #fff;
  z-index: 20;
  backdrop-filter: blur(5px);
}

.camera-title-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.camera-name {
  font-weight: 600;
  font-size: 14px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

.status-indicator {
  font-weight: 500;
  min-width: 50px;
  justify-content: center;
}

.camera-action-bar {
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.camera-viewport:hover .camera-action-bar {
  opacity: 1;
}

.video-canvas-layer,
.video-player-layer {
  width: 100%;
  height: 100%;
  object-fit: contain;
  position: absolute;
  top: 0;
  left: 0;
}

.video-canvas-layer {
  z-index: 5;
}

.video-player-layer {
  z-index: 4;
}

.control-sidebar {
  width: 340px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  border-left: 1px solid #e4e7ed;
  box-shadow: -2px 0 20px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.camera-selector-panel {
  flex-shrink: 0;
  height: 320px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.panel-header-section {
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
}

.panel-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.search-toolbar {
  margin-top: 8px;
}

.camera-list-scrollable {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.camera-selection-list {
  padding: 12px;
}

.camera-selection-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8f9fa;
  border: 1px solid transparent;
}

.camera-selection-item:hover {
  background: #f0f2f5;
  transform: translateX(4px);
}

.camera-selection-item.selected {
  background: linear-gradient(135deg, #ecf5ff, #d9ecff);
  border-color: #409eff;
}

.camera-selection-item.offline {
  opacity: 0.6;
  cursor: not-allowed;
}

.camera-item-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.camera-display-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.status-badge {
  width: 60px;
  justify-content: center;
}

.camera-item-actions {
  margin-left: 12px;
}

.ptz-control-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.selected-camera-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.camera-label {
  color: #909399;
  font-size: 12px;
}

.camera-value {
  font-weight: 600;
  color: #409eff;
}

.ptz-control-area {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

.control-step-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.step-label {
  font-weight: 500;
  color: #606266;
}

.directional-control-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 8px;
  padding: 16px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
}

.direction-control-btn {
  height: 50px;
  width: 100%;
  font-size: 20px;
  padding: 0;
  border-radius: 8px;
  transition: all 0.2s ease;
  background: #ffffff;
  border: 2px solid #e4e7ed;
}

.direction-control-btn:hover {
  background: #f0f2f5;
  border-color: #409eff;
  transform: scale(1.05);
}

.center-control-btn {
  grid-column: 2;
  grid-row: 2;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: white;
  border: none;
}

.center-control-btn:hover {
  background: linear-gradient(135deg, #66b1ff, #79bbff);
  transform: scale(1.05);
}

.lens-function-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
}

.function-control-row {
  display: flex;
  gap: 12px;
}

.function-control-btn {
  flex: 1;
  padding: 12px;
  border-radius: 6px;
  background: #ffffff;
  border: 2px solid #dcdfe6;
  transition: all 0.2s ease;
}

.function-control-btn:hover {
  background: #f0f2f5;
  border-color: #409eff;
}

.media-operation-panel {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
}

.media-operation-panel .el-button {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  font-weight: 500;
}

.recording-active {
  background: linear-gradient(135deg, #f56c6c, #f78989) !important;
  border-color: #f56c6c !important;
  color: white !important;
}

/* 全屏模式样式 */
:fullscreen .camera-viewport {
  width: 100vw !important;
  height: 100vh !important;
  border-radius: 0 !important;
  border: none !important;
  margin: 0 !important;
  padding: 0 !important;
}

:fullscreen .camera-viewport-header {
  padding: 16px 24px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.9), transparent);
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

/* 响应式设计 */
@media (max-width: 1200px) {
  .video-grid-area {
    grid-template-columns: repeat(auto-fill, minmax(40%, 1fr));
  }

  .control-sidebar {
    width: 300px;
  }
}

@media (max-width: 768px) {
  .surveillance-dashboard {
    flex-direction: column;
  }

  .video-grid-area {
    grid-template-columns: 1fr;
    grid-auto-rows: minmax(250px, 1fr);
  }

  .control-sidebar {
    width: 100%;
    height: 300px;
    border-left: none;
    border-top: 1px solid #e4e7ed;
  }

  .camera-selector-panel {
    height: 200px;
  }
}

/* 动画效果 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.recording-active {
  animation: pulse 1.5s infinite;
}
</style>