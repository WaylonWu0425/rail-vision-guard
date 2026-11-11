<template>
  <main class="image-detection" aria-label="智能检测工作台">
    <header class="workspace-header">
      <div class="heading-block">
        <div class="eyebrow">车站视频监控 · 实时分析</div>
        <div class="title-row">
          <h1>智能检测</h1>
          <span class="title-divider" aria-hidden="true"></span>
          <p>实时画面分析与告警取证</p>
        </div>
      </div>

      <div class="camera-selector">
        <label for="detection-camera">检测摄像头</label>
        <el-select
          id="detection-camera"
          :model-value="currentCamera?.id"
          placeholder="请选择在线摄像头"
          :loading="loading"
          filterable
          @change="selectCameraById"
        >
          <el-option
            v-for="camera in onlineCameras"
            :key="camera.id"
            :label="camera.name || `摄像头 ${camera.id}`"
            :value="camera.id"
          />
        </el-select>
      </div>

      <div class="status-cluster" aria-label="运行状态">
        <div class="status-item">
          <span class="status-dot" :class="currentCamera ? 'is-success' : 'is-muted'"></span>
          <div><small>设备连接</small><strong>{{ currentCamera ? '设备在线' : '未选择设备' }}</strong></div>
        </div>
        <div class="status-item">
          <span class="status-dot" :class="detectionService.ready ? 'is-success' : 'is-danger'"></span>
          <div><small>识别与跟踪</small><strong>{{ detectionService.ready ? `person / car · ${detectionService.tracking || '跟踪就绪'}` : '服务异常' }}</strong></div>
        </div>
        <div class="status-item">
          <span class="status-dot" :class="currentTaskStatus.dotClass"></span>
          <div><small>检测任务</small><strong>{{ currentTaskStatus.label }}</strong></div>
        </div>
      </div>

      <div class="header-actions">
        <el-button @click="$router.push('/originalRecognition')">人车识别</el-button>
        <el-button
          v-if="currentCamera && !isDetectionActive(currentCamera.id)"
          type="primary"
          :disabled="!detectionService.ready"
          @click="startDetection(currentCamera)"
        >
          <el-icon><VideoPlay /></el-icon>启动检测
        </el-button>
        <el-button
          v-else-if="currentCamera"
          type="warning"
          plain
          @click="stopDetection(currentCamera.id)"
        >
          <el-icon><VideoPause /></el-icon>停止检测
        </el-button>
        <el-button
          v-if="currentCamera && isDetectionActive(currentCamera.id) && streamStates[currentCamera.id] === 'error'"
          @click="restartDetection(currentCamera)"
        >
          <el-icon><RefreshRight /></el-icon>重新连接
        </el-button>
        <el-button
          circle
          aria-label="全屏查看检测画面"
          :disabled="!currentCamera"
          @click="currentCamera && toggleFullscreen(currentCamera)"
        >
          <el-icon><FullScreen /></el-icon>
        </el-button>
      </div>
    </header>

    <section class="workspace-body">
      <div class="main-column">
        <section class="monitor-card">
          <div class="card-heading monitor-heading">
            <div>
              <h2>{{ currentCamera ? (currentCamera.name || `摄像头 ${currentCamera.id}`) : '实时检测画面' }}</h2>
              <p>{{ monitorSubtitle }}</p>
            </div>
            <div class="monitor-legend" aria-label="图层说明">
              <span><i class="legend-box is-detection"></i>模型目标</span>
              <span><i class="legend-box is-region"></i>警戒区域</span>
              <span><i class="legend-box is-event"></i>事件提示</span>
            </div>
          </div>

          <div class="monitor-stage">
            <div v-if="loading" class="empty-state"><span class="state-spinner"></span>正在加载摄像头...</div>
            <div v-else-if="!currentCamera" class="empty-state">
              <strong>暂无可用画面</strong>
              <span>请从顶部选择一台在线摄像头</span>
            </div>
            <div v-else class="video-item" :data-camera-id="currentCamera.id">
              <div class="stream-wrapper">
                <img
                  v-if="isDetectionActive(currentCamera.id)"
                  :src="streamUrl(currentCamera.id)"
                  :alt="`${currentCamera.name || `摄像头 ${currentCamera.id}`} YOLO 检测视频流`"
                  @load="handleStreamLoad(currentCamera.id)"
                  @error="handleStreamError(currentCamera.id)"
                />
                <div v-else class="stream-idle">
                  <div class="idle-symbol"><el-icon><VideoPlay /></el-icon></div>
                  <strong>检测任务未启动</strong>
                  <span>启动后系统才会连接视频流、运行人员与车辆识别并生成真实事件。</span>
                  <el-button type="primary" :disabled="!detectionService.ready" @click="startDetection(currentCamera)">启动检测</el-button>
                </div>
                <svg
                  v-if="isCurrentRegionCamera(currentCamera.id)"
                  class="region-overlay"
                  :class="{ drawing: regionDrawing }"
                  viewBox="0 0 1000 1000"
                  preserveAspectRatio="none"
                  aria-label="警戒区域绘制层"
                  @click.stop="addRegionPoint($event, currentCamera.id)"
                >
                  <polygon v-if="regionRule.points.length >= 3" :points="regionPolygonPoints" class="region-polygon" />
                  <polyline v-else-if="regionRule.points.length > 1" :points="regionPolygonPoints" class="region-polyline" />
                  <circle
                    v-for="(point, index) in regionRule.points"
                    :key="`${currentCamera.id}-${index}`"
                    :cx="point.x * 1000"
                    :cy="point.y * 1000"
                    r="9"
                    class="region-point"
                  />
                </svg>
                <div class="camera-overlay-name">
                  <span class="live-dot" :class="isDetectionActive(currentCamera.id) ? 'is-live' : ''"></span>
                  {{ currentCamera.name || `摄像头 ${currentCamera.id}` }}
                </div>
              </div>
              <div v-if="streamStates[currentCamera.id] === 'error'" class="stream-error" role="alert">
                <strong>检测画面连接失败</strong>
                <span>请确认检测服务与摄像头在线，然后点击顶部“重新连接”。</span>
              </div>
            </div>
          </div>

          <div class="monitor-footer">
            <span>{{ regionStateText }}</span>
            <span>推理设备：{{ currentPerformance.deviceName || detectionService.deviceName }}</span>
            <span>运行性能：{{ performanceText }}</span>
            <span>异物功能：固定机位受控原型</span>
          </div>
        </section>

        <section class="events-card">
          <div class="card-heading events-heading">
            <div>
              <h2>近期检测事件</h2>
              <p>仅展示系统已写入的告警与证据，不生成模拟结果</p>
            </div>
            <el-radio-group v-model="eventFilter" size="small">
              <el-radio-button label="current">当前摄像头</el-radio-button>
              <el-radio-button label="all">全部未处理</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="alertScrollContainer" class="events-scroll">
            <div v-if="filteredAlerts.length === 0" class="events-empty">
              <span>暂无符合条件的检测事件</span>
            </div>
            <article
              v-for="alert in filteredAlerts"
              :key="alert.id"
              class="event-row"
              :class="`level-${Number(alert.level)}`"
            >
              <button
                v-if="getDetectionEvent(alert.id)?.snapshotFile"
                class="event-thumb"
                :aria-label="`查看告警 ${alert.id} 的证据截图`"
                @click="openEvidence(getDetectionEvent(alert.id).snapshotFile)"
              >
                <img :src="evidenceUrl(getDetectionEvent(alert.id).snapshotFile)" alt="告警证据截图" />
              </button>
              <div v-else class="event-thumb placeholder" aria-hidden="true">无截图</div>
              <div class="event-summary">
                <div class="event-title-line">
                  <el-tag :type="getAlertTypeByLevel(alert.level)" size="small">{{ getAlertLevelText(alert.level) }}</el-tag>
                  <strong>{{ alert.title || alert.content || '检测事件' }}</strong>
                </div>
                <p>{{ alert.description || detectionEventTypeLabel(getDetectionEvent(alert.id)?.eventType) }}</p>
                <span>{{ getCameraNameById(alert.cameraId) }} · {{ formatEventDate(alert.createTime) }}</span>
              </div>
              <div class="event-review">
                <template v-if="getDetectionEvent(alert.id)">
                  <span>
                    {{ getDetectionEvent(alert.id).label || '目标' }}
                    <template v-if="getDetectionEvent(alert.id).trackId"> #{{ getDetectionEvent(alert.id).trackId }}</template>
                    · {{ formatConfidence(getDetectionEvent(alert.id).confidence) }}
                    <template v-if="getDetectionEvent(alert.id).durationSeconds != null"> · {{ Number(getDetectionEvent(alert.id).durationSeconds).toFixed(1) }} 秒</template>
                  </span>
                  <el-tag size="small" :type="reviewTagType(getDetectionEvent(alert.id).reviewStatus)">
                    {{ reviewLabel(getDetectionEvent(alert.id).reviewStatus) }}
                  </el-tag>
                </template>
                <span v-else>系统告警</span>
              </div>
              <div class="event-actions">
                <el-button size="small" @click="viewAlertCamera(alert.cameraId)">查看画面</el-button>
                <el-button v-if="getDetectionEvent(alert.id)" size="small" type="primary" plain @click="openRelatedRecording(getDetectionEvent(alert.id))">关联录像</el-button>
                <el-button size="small" type="success" plain @click="markAlertAsRead(alert)">标记已处理</el-button>
              </div>
            </article>
          </div>
        </section>
      </div>

      <aside class="rule-panel" aria-label="检测规则配置">
        <div class="rule-panel-header">
          <div>
            <h2>检测规则</h2>
            <p>{{ currentCamera ? `应用于 ${currentCamera.name || `摄像头 ${currentCamera.id}`}` : '请先选择摄像头' }}</p>
          </div>
          <el-tag size="small" :type="ruleStateTag.type">{{ ruleStateTag.label }}</el-tag>
        </div>

        <el-tabs v-model="activeRuleTab" class="rule-tabs" stretch>
          <el-tab-pane label="区域规则" name="intrusion">
            <div class="rule-content">
              <div class="rule-intro">
                <strong>轨迹级区域规则</strong>
                <span>目标进入指定区域并持续达到阈值后，同一轨迹只产生一次告警。</span>
              </div>

              <label class="field-label" for="region-name">规则名称</label>
              <el-input id="region-name" v-model="regionRule.name" maxlength="64" placeholder="例如：站台边缘警戒区" />

              <div class="field-block">
                <label class="field-label">判定目标</label>
                <p class="field-help">选择该区域需要监测的目标类别</p>
                <el-checkbox-group v-model="regionRule.targetClasses" class="target-class-group">
                  <el-checkbox-button value="person">人员</el-checkbox-button>
                  <el-checkbox-button value="car">车辆</el-checkbox-button>
                </el-checkbox-group>
              </div>

              <div class="field-row">
                <div>
                  <label class="field-label">停留阈值</label>
                  <p class="field-help">过滤短暂经过，减少重复提示</p>
                </div>
                <div class="number-field">
                  <el-input-number v-model="regionRule.dwellSeconds" :min="0.5" :max="60" :step="0.5" />
                  <span>秒</span>
                </div>
              </div>

              <div class="field-row">
                <div>
                  <label class="field-label">二次冷却</label>
                  <p class="field-help">跟踪中断后抑制短时间重复事件</p>
                </div>
                <div class="number-field">
                  <el-input-number v-model="regionRule.cooldownSeconds" :min="0" :max="600" :step="5" />
                  <span>秒</span>
                </div>
              </div>

              <div class="field-row">
                <div>
                  <label class="field-label">启用规则</label>
                  <p class="field-help">保存后在检测任务中生效</p>
                </div>
                <el-switch v-model="regionRule.enabled" :disabled="regionRule.points.length < 3" />
              </div>

              <div class="drawing-status" :class="{ active: regionDrawing }">
                <div class="drawing-status-top">
                  <strong>{{ regionDrawing ? '正在绘制警戒区域' : regionRule.points.length >= 3 ? '警戒区域已定义' : '尚未定义警戒区域' }}</strong>
                  <span>{{ regionRule.points.length }} 个顶点</span>
                </div>
                <p>{{ regionDrawing ? '请在左侧画面顺序点击至少 3 个点，完成后保存。' : '区域会以橙色半透明多边形显示在画面上。' }}</p>
              </div>

              <div class="drawing-actions">
                <el-button type="primary" plain :disabled="!currentCamera" @click="startRegionDrawing">
                  {{ regionRule.points.length ? '重新绘制' : '开始绘制' }}
                </el-button>
                <el-button :disabled="regionRule.points.length === 0" @click="undoRegionPoint">撤销一点</el-button>
                <el-button :disabled="regionRule.points.length === 0" @click="clearRegionPoints">清空</el-button>
              </div>

              <div class="rule-notice">
                当前模型只识别人员与车辆；系统按目标轨迹ID分别计时并抑制重复告警。
              </div>

              <el-button
                class="primary-rule-action"
                type="primary"
                size="large"
                :disabled="!currentCamera || regionRule.points.length < 3 || regionRule.targetClasses.length === 0"
                @click="saveRegionRule"
              >保存并应用规则</el-button>
            </div>
          </el-tab-pane>

          <el-tab-pane label="异物遗留" name="foreign">
            <div class="rule-content">
              <div class="prototype-banner">
                <strong>受控场景原型</strong>
                <span>仅适用于固定机位、固定光照，不能等同于通用异物识别。</span>
              </div>

              <div class="baseline-card" :class="{ ready: foreignObjectRule.baselineReady }">
                <div class="baseline-icon"></div>
                <div>
                  <strong>{{ foreignObjectRule.baselineReady ? '空场景基准已建立' : '待建立空场景基准' }}</strong>
                  <p>{{ foreignObjectRule.baselineReady ? '镜头或光照变化后请重新采集。' : '移除画面中的临时人员和物体后再采集。' }}</p>
                </div>
              </div>

              <el-alert
                v-if="foreignObjectRule.baselineReady && !currentBaselineHealth.valid"
                :title="currentBaselineHealth.message || '当前基线已失效，请重新采集'"
                type="error"
                :closable="false"
                show-icon
              />

              <div class="field-row">
                <div>
                  <label class="field-label">静止持续时间</label>
                  <p class="field-help">达到阈值后产生原型提示</p>
                </div>
                <div class="number-field">
                  <el-input-number v-model="foreignObjectRule.dwellSeconds" :min="2" :max="300" :step="1" />
                  <span>秒</span>
                </div>
              </div>

              <div class="field-row">
                <div>
                  <label class="field-label">启用原型</label>
                  <p class="field-help">必须先完成基准采集</p>
                </div>
                <el-switch v-model="foreignObjectRule.enabled" :disabled="!foreignObjectRule.baselineReady" />
              </div>

              <ol class="workflow-steps">
                <li><span>1</span>固定摄像头与现场显示位置</li>
                <li><span>2</span>保持空场景并采集基准</li>
                <li><span>3</span>放入静止物体观察提示</li>
              </ol>

              <el-button
                class="primary-rule-action"
                type="warning"
                size="large"
                :loading="capturingBaseline"
                :disabled="!currentCamera || !isDetectionActive(currentCamera.id)"
                @click="captureBaseline"
              >{{ foreignObjectRule.baselineReady ? '重新采集并应用基准' : '采集当前空场景并启用' }}</el-button>
              <el-button
                v-if="foreignObjectRule.baselineReady"
                class="secondary-rule-action"
                text
                type="danger"
                @click="clearBaseline"
              >清除当前基准</el-button>
            </div>
          </el-tab-pane>
        </el-tabs>

        <div class="service-note" :class="{ error: !detectionService.ready }" role="status">
          <span class="status-dot" :class="detectionService.ready ? 'is-success' : 'is-danger'"></span>
          <div>
            <strong>{{ detectionService.ready ? '检测服务可用' : '检测服务不可用' }}</strong>
            <p>{{ detectionService.ready ? `${detectionService.deviceName} · ${detectionService.tracking || '目标检测'} · ${detectionService.classes.join('、') || 'person、car'}` : detectionService.message }}</p>
          </div>
        </div>
      </aside>
    </section>
  </main>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useRouter } from 'vue-router';
import { FullScreen, VideoPlay, VideoPause, RefreshRight } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getAllCameras, searchCamera } from "@/http/api/camera.js";
import { getUndisposedAlarmInfo, updateAlarmInfoById } from '@/http/api/alarm.js'
import { getRecordingMatch } from '@/http/api/recording.js';
import { createTask } from '@/http/api/task.js';
const router = useRouter();
// 摄像头数据
const cameras = ref([]);
const displayedCameras = reactive([]);
const currentCamera = ref(null);
const loading = ref(true);
const searchKeyword = ref('');

// 危险状况列表
const alerts = ref([]);
const detectionEvents = ref([]);
const autoScroll = ref(true);
const alertScrollContainer = ref(null);
const alarmTimer = ref(null); // 添加定时器引用
const healthTimer = ref(null);
const streamStates = reactive({});
const detectionTasks = reactive({});
const streamTokens = reactive({});
const detectionBaseUrl = process.env.VUE_APP_DETECTION_BASE_URL || '/detection';
const detectionService = reactive({
  ready: false,
  classes: [],
  device: 'cpu',
  deviceName: 'CPU',
  tracking: '',
  modelVersion: '',
  message: '正在检查检测服务'
});
const activeRuleTab = ref('intrusion');
const eventFilter = ref('current');
const regionDrawing = ref(false);
const regionRule = reactive({
  cameraId: null,
  name: '警戒区域',
  points: [],
  enabled: true,
  dwellSeconds: 2,
  targetClasses: ['person'],
  cooldownSeconds: 30
});
const foreignObjectRule = reactive({
  baselineReady: false,
  enabled: true,
  dwellSeconds: 8,
  minAreaRatio: 0.005
});
const capturingBaseline = ref(false);
const regionSnapshot = ref('');

const serializeRegionRule = () => JSON.stringify({
  cameraId: regionRule.cameraId,
  name: regionRule.name,
  points: regionRule.points,
  enabled: regionRule.enabled,
  dwellSeconds: regionRule.dwellSeconds,
  targetClasses: regionRule.targetClasses,
  cooldownSeconds: regionRule.cooldownSeconds
});

const regionDirty = computed(() => Boolean(regionSnapshot.value) && serializeRegionRule() !== regionSnapshot.value);

const currentTaskStatus = computed(() => {
  if (!currentCamera.value) return { label: '未选择', dotClass: 'is-muted' };
  const cameraId = currentCamera.value.id;
  const task = detectionTasks[cameraId];
  if (streamStates[cameraId] === 'error') return { label: '连接异常', dotClass: 'is-danger' };
  if (!task?.started) return { label: '未启动', dotClass: 'is-muted' };
  if (task.state === 'stopping') return { label: '停止中', dotClass: 'is-warning' };
  if (task.connected || task.state === 'running') return { label: '运行中', dotClass: 'is-success' };
  return { label: '连接中', dotClass: 'is-warning' };
});

const currentPerformance = computed(() => {
  if (!currentCamera.value) return {};
  return detectionTasks[currentCamera.value.id]?.performance || {};
});

const currentBaselineHealth = computed(() => {
  if (!currentCamera.value) return { valid: true, message: '' };
  const task = detectionTasks[currentCamera.value.id] || {};
  return {
    valid: task.foreignBaselineValid !== false,
    message: task.foreignBaselineMessage || ''
  };
});

const performanceText = computed(() => {
  const performance = currentPerformance.value;
  if (!performance.inferenceMs) return '等待性能数据';
  return `${performance.inferenceMs} ms · ${performance.inferenceFps || 0} FPS · ${performance.trackCount || 0} 条轨迹`;
});

const monitorSubtitle = computed(() => {
  if (!currentCamera.value) return '选择在线摄像头后可启动检测任务';
  if (!detectionService.ready) return detectionService.message;
  if (streamStates[currentCamera.value.id] === 'error') return '视频流连接异常，检测任务需要重新连接';
  if (isDetectionActive(currentCamera.value.id)) return 'YOLO 人员与车辆识别正在运行';
  return '设备在线，检测任务尚未启动';
});

const regionStateText = computed(() => {
  if (!currentCamera.value) return '警戒区域：未选择摄像头';
  if (regionDrawing.value) return `警戒区域：正在绘制（${regionRule.points.length} 个顶点）`;
  if (regionRule.points.length < 3) return '警戒区域：未设置';
  if (regionDirty.value) return '警戒区域：有未保存修改';
  return regionRule.enabled ? '警戒区域：已启用' : '警戒区域：已保存但停用';
});

const ruleStateTag = computed(() => {
  if (!currentCamera.value) return { label: '未选择设备', type: 'info' };
  if (activeRuleTab.value === 'foreign') {
    if (!foreignObjectRule.baselineReady) return { label: '待建基准', type: 'warning' };
    return foreignObjectRule.enabled
      ? { label: '原型已启用', type: 'success' }
      : { label: '原型已停用', type: 'info' };
  }
  if (regionRule.points.length < 3) return { label: regionDrawing.value ? '绘制中' : '未设置', type: 'info' };
  if (regionDirty.value) return { label: '待保存', type: 'warning' };
  return regionRule.enabled
    ? { label: '已启用', type: 'success' }
    : { label: '已停用', type: 'info' };
});

const filteredAlerts = computed(() => {
  const rows = [...alerts.value].sort((a, b) => new Date(b.createTime || 0) - new Date(a.createTime || 0));
  if (eventFilter.value === 'current' && currentCamera.value) {
    return rows.filter(alert => String(alert.cameraId) === String(currentCamera.value.id)).slice(0, 20);
  }
  return rows.slice(0, 20);
});

const regionPolygonPoints = computed(() => regionRule.points
  .map(point => `${Math.round(point.x * 1000)},${Math.round(point.y * 1000)}`)
  .join(' '));

const streamUrl = (cameraId) => `${detectionBaseUrl}/video_feed/${encodeURIComponent(cameraId)}?v=${streamTokens[cameraId] || 0}`;
const evidenceUrl = (filename) => filename ? `${detectionBaseUrl}/evidence/${encodeURIComponent(filename)}` : '';
const getDetectionEvent = (alarmId) => detectionEvents.value.find(event => Number(event.alarmId) === Number(alarmId));
const formatConfidence = (value) => value == null ? '—' : `${Math.round(Number(value) * 100)}%`;
const detectionEventTypeLabel = (eventType) => {
  if (eventType === 'region_intrusion') return '区域入侵（实时模型）';
  if (eventType === 'foreign_object') return '新增静止物体（受控原型）';
  if (eventType === 'object_detection') return '目标检测（实时模型）';
  return '检测事件';
};
const reviewLabel = (status) => {
  if (status === 'confirmed') return '人工确认';
  if (status === 'rejected') return '人工驳回';
  return '待人工复核';
};
const reviewTagType = (status) => {
  if (status === 'confirmed') return 'success';
  if (status === 'rejected') return 'info';
  return 'warning';
};
const isDetectionActive = (cameraId) => Boolean(detectionTasks[cameraId]?.started);
const detectionLabel = (cameraId) => {
  const task = detectionTasks[cameraId];
  if (!task?.started) return '未启动';
  if (task.state === 'stopping') return '停止中';
  if (task.connected || task.state === 'running') return '检测中';
  return task.lastError || task.state === 'reconnecting' ? '重连中' : '正在连接';
};
const detectionTagType = (cameraId) => {
  const task = detectionTasks[cameraId];
  if (!task?.started) return 'info';
  return task.connected ? 'success' : 'warning';
};
const openEvidence = (filename) => {
  const url = evidenceUrl(filename);
  if (url) window.open(url, '_blank', 'noopener');
};

const refreshDetectionTask = async (cameraId) => {
  try {
    const response = await fetch(`${detectionBaseUrl}/cameras/${encodeURIComponent(cameraId)}/status`, { cache: 'no-store' });
    const data = await response.json();
    detectionTasks[cameraId] = data;
    if (!data.started) streamStates[cameraId] = 'idle';
  } catch (error) {
    detectionTasks[cameraId] = { started: false, lastError: '无法读取检测任务状态' };
  }
};

const refreshDisplayedTaskStates = () => Promise.all(displayedCameras.map(camera => refreshDetectionTask(camera.id)));

const startDetection = async (camera) => {
  if (!detectionService.ready) {
    ElMessage.error('YOLO检测服务未就绪，请先启动检测服务并检查数据库连接');
    return;
  }
  try {
    streamStates[camera.id] = 'connecting';
    const response = await fetch(`${detectionBaseUrl}/cameras/${encodeURIComponent(camera.id)}/start`, { method: 'POST' });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.message || '启动失败');
    detectionTasks[camera.id] = result.data;
    streamTokens[camera.id] = Date.now();
    ElMessage.success(result.created ? '检测任务已启动，正在连接摄像头' : '检测任务已在运行');
  } catch (error) {
    streamStates[camera.id] = 'error';
    ElMessage.error(`启动检测失败：${error.message || '请确认摄像头在线'}`);
  }
};

const stopDetection = async (cameraId) => {
  try {
    const response = await fetch(`${detectionBaseUrl}/cameras/${encodeURIComponent(cameraId)}/stop`, { method: 'POST' });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.message || '停止失败');
    detectionTasks[cameraId] = { started: false, connected: false };
    streamStates[cameraId] = 'idle';
    ElMessage.success('检测任务已停止，摄像头连接已释放');
  } catch (error) {
    ElMessage.error(`停止检测失败：${error.message || '检测服务不可用'}`);
  }
};

const restartDetection = async (camera) => {
  if (!camera) return;
  // 后端 start 接口会复用既有 worker；先请求停止可以释放已失效的 RTSP 连接。
  if (isDetectionActive(camera.id)) await stopDetection(camera.id);
  await startDetection(camera);
};

const openRelatedRecording = async (event) => {
  if (!event?.cameraId || !event?.createdAt) {
    ElMessage.info('该告警没有可用于关联录像的时间信息');
    return;
  }
  try {
    const response = await getRecordingMatch(event.cameraId, event.createdAt);
    if (!response.data?.success || !response.data?.data?.filename) {
      ElMessage.info(response.data?.msg || '没有覆盖此告警时刻的录像');
      return;
    }
    router.push({ path: '/video', query: { recording: response.data.data.filename } });
  } catch (error) {
    ElMessage.error(`查询关联录像失败：${error.message || '请检查录像服务'}`);
  }
};

const reviewDetectionEvent = async (event, status) => {
  if (!event?.id) return;
  const action = status === 'confirmed' ? '确认该事件' : '驳回该提示';
  try {
    const { value } = await ElMessageBox.prompt(
      `请填写${action}的说明（可留空；最多500字）。`,
      action,
      { confirmButtonText: '保存复核', cancelButtonText: '取消', inputType: 'textarea', inputPlaceholder: '例如：画面已核实，需生成现场处置任务。' }
    );
    const response = await fetch(`${detectionBaseUrl}/events/${encodeURIComponent(event.id)}/review`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, reason: value || '' })
    });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.message || '复核保存失败');
    event.reviewStatus = result.data.reviewStatus;
    event.reviewReason = result.data.reviewReason;
    ElMessage.success(status === 'confirmed' ? '事件已人工确认' : '提示已人工驳回');
  } catch (error) {
    if (error === 'cancel' || error?.action === 'cancel' || error?.action === 'close') return;
    ElMessage.error(`保存复核失败：${error.message || '检测服务不可用'}`);
  }
};

const createTaskFromEvent = async (event) => {
  if (!event?.id || event.reviewStatus !== 'confirmed') {
    ElMessage.warning('请先人工确认该事件，再生成任务');
    return;
  }
  try {
    await ElMessageBox.confirm(
      '将创建一条待分配任务，并关联当前检测事件；任务创建后可在作业管理中补充人员和时限。',
      '生成处置任务',
      { confirmButtonText: '创建任务', cancelButtonText: '取消', type: 'warning' }
    );
    const eventName = detectionEventTypeLabel(event.eventType);
    const response = await createTask({
      title: `${eventName}待核查`,
      description: `来源检测事件 #${event.id}；摄像头 #${event.cameraId}；发生时间 ${event.createdAt || '未记录'}；${event.reviewReason || '已由值班人员确认。'}`,
      type: '智能检测',
      priority: '高'
    });
    const taskId = Number(response.data?.data?.taskId);
    if (!response.data?.success || !Number.isInteger(taskId) || taskId <= 0) {
      throw new Error(response.data?.message || '任务创建后未返回编号');
    }
    const linkResponse = await fetch(`${detectionBaseUrl}/events/${encodeURIComponent(event.id)}/task`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ taskId })
    });
    const linkResult = await linkResponse.json();
    if (!linkResponse.ok || !linkResult.success) {
      throw new Error(`任务 #${taskId} 已创建，但事件关联失败：${linkResult.message || '请在作业管理中手工记录来源事件'}`);
    }
    event.linkedTaskId = taskId;
    ElMessage.success(`已创建并关联任务 #${taskId}`);
  } catch (error) {
    if (error === 'cancel' || error?.action === 'cancel' || error?.action === 'close') return;
    ElMessage.error(`生成任务失败：${error.message || '请检查任务服务'}`);
  }
};

const handleStreamLoad = (cameraId) => {
  streamStates[cameraId] = 'connected';
};

const handleStreamError = (cameraId) => {
  streamStates[cameraId] = 'error';
};

const resetRegionRule = (cameraId) => {
  regionRule.cameraId = cameraId;
  regionRule.name = '警戒区域';
  regionRule.points = [];
  regionRule.enabled = true;
  regionRule.dwellSeconds = 2;
  regionRule.targetClasses = ['person'];
  regionRule.cooldownSeconds = 30;
  regionDrawing.value = false;
  regionSnapshot.value = serializeRegionRule();
};

const resetForeignObjectRule = () => {
  foreignObjectRule.baselineReady = false;
  foreignObjectRule.enabled = true;
  foreignObjectRule.dwellSeconds = 8;
  foreignObjectRule.minAreaRatio = 0.005;
};

const loadForeignObjectRule = async (cameraId) => {
  if (!cameraId) return;
  try {
    const response = await fetch(`${detectionBaseUrl}/foreign-object/${encodeURIComponent(cameraId)}`, { cache: 'no-store' });
    const result = await response.json();
    if (!response.ok || !result.success || !result.data) {
      resetForeignObjectRule();
      return;
    }
    foreignObjectRule.baselineReady = Boolean(result.data.baselineReady);
    foreignObjectRule.enabled = Boolean(result.data.enabled);
    foreignObjectRule.dwellSeconds = Number(result.data.dwellSeconds || 8);
    foreignObjectRule.minAreaRatio = Number(result.data.minAreaRatio || 0.005);
  } catch (error) {
    resetForeignObjectRule();
  }
};

const loadRegionRule = async (cameraId) => {
  if (!cameraId) return;
  try {
    const response = await fetch(`${detectionBaseUrl}/regions/${encodeURIComponent(cameraId)}`, { cache: 'no-store' });
    const result = await response.json();
    if (!response.ok || !result.success || !result.data) {
      resetRegionRule(cameraId);
      loadForeignObjectRule(cameraId);
      return;
    }
    const data = result.data;
    regionRule.cameraId = cameraId;
    regionRule.name = data.name || '警戒区域';
    regionRule.points = Array.isArray(data.points) ? data.points : [];
    regionRule.enabled = Boolean(data.enabled);
    regionRule.dwellSeconds = Number(data.dwellSeconds || 2);
    regionRule.targetClasses = Array.isArray(data.targetClasses) && data.targetClasses.length
      ? data.targetClasses
      : ['person'];
    regionRule.cooldownSeconds = Number(data.cooldownSeconds ?? 30);
    regionDrawing.value = false;
    regionSnapshot.value = serializeRegionRule();
    loadForeignObjectRule(cameraId);
  } catch (error) {
    resetRegionRule(cameraId);
    loadForeignObjectRule(cameraId);
    ElMessage.warning('无法读取警戒区域规则');
  }
};

const isCurrentRegionCamera = (cameraId) => currentCamera.value && currentCamera.value.id === cameraId && regionRule.cameraId === cameraId;

const startRegionDrawing = () => {
  if (!currentCamera.value) return;
  regionRule.cameraId = currentCamera.value.id;
  regionRule.points = [];
  regionDrawing.value = true;
  ElMessage.info('请在视频画面内顺序点击至少3个顶点');
};

const addRegionPoint = (event, cameraId) => {
  if (!regionDrawing.value || !isCurrentRegionCamera(cameraId)) return;
  const rect = event.currentTarget.getBoundingClientRect();
  if (!rect.width || !rect.height || regionRule.points.length >= 20) return;
  regionRule.points.push({
    x: Number(((event.clientX - rect.left) / rect.width).toFixed(6)),
    y: Number(((event.clientY - rect.top) / rect.height).toFixed(6))
  });
};

const undoRegionPoint = () => {
  regionRule.points.pop();
};

const clearRegionPoints = () => {
  regionRule.points = [];
  regionDrawing.value = false;
};

const saveRegionRule = async () => {
  if (!currentCamera.value) return;
  if (regionRule.points.length < 3) {
    ElMessage.warning('警戒区域至少需要3个顶点');
    return;
  }
  try {
    const response = await fetch(`${detectionBaseUrl}/regions/${encodeURIComponent(currentCamera.value.id)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: regionRule.name,
        points: regionRule.points,
        enabled: regionRule.enabled,
        dwellSeconds: regionRule.dwellSeconds,
        targetClasses: regionRule.targetClasses,
        cooldownSeconds: regionRule.cooldownSeconds
      })
    });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.message || '保存失败');
    regionRule.cameraId = currentCamera.value.id;
    regionRule.name = result.data.name;
    regionRule.points = result.data.points;
    regionRule.enabled = result.data.enabled;
    regionRule.dwellSeconds = Number(result.data.dwellSeconds);
    regionRule.targetClasses = Array.isArray(result.data.targetClasses) ? result.data.targetClasses : ['person'];
    regionRule.cooldownSeconds = Number(result.data.cooldownSeconds ?? 30);
    regionDrawing.value = false;
    regionSnapshot.value = serializeRegionRule();
    ElMessage.success('警戒区域已保存，检测服务将在下一帧生效');
  } catch (error) {
    ElMessage.error(`保存警戒区域失败：${error.message || '检测服务不可用'}`);
  }
};

const captureBaseline = async () => {
  if (!currentCamera.value) return;
  if (!isDetectionActive(currentCamera.value.id)) {
    ElMessage.warning('请先启动检测并等待画面连接后再采集基准');
    return;
  }
  capturingBaseline.value = true;
  try {
    const response = await fetch(`${detectionBaseUrl}/foreign-object/${encodeURIComponent(currentCamera.value.id)}/baseline`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        enabled: foreignObjectRule.enabled,
        dwellSeconds: foreignObjectRule.dwellSeconds,
        minAreaRatio: foreignObjectRule.minAreaRatio
      })
    });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.message || '基准采集失败');
    foreignObjectRule.baselineReady = true;
    foreignObjectRule.enabled = Boolean(result.data.enabled);
    foreignObjectRule.dwellSeconds = Number(result.data.dwellSeconds);
    foreignObjectRule.minAreaRatio = Number(result.data.minAreaRatio);
    ElMessage.success('空场景基准已保存；请保持镜头和显示器位置不变');
  } catch (error) {
    ElMessage.error(`采集基准失败：${error.message || '请先确认检测画面已正常显示'}`);
  } finally {
    capturingBaseline.value = false;
  }
};

const clearBaseline = async () => {
  if (!currentCamera.value) return;
  try {
    const response = await fetch(`${detectionBaseUrl}/foreign-object/${encodeURIComponent(currentCamera.value.id)}`, { method: 'DELETE' });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.message || '清除失败');
    resetForeignObjectRule();
    ElMessage.success('异物基准已清除');
  } catch (error) {
    ElMessage.error(`清除基准失败：${error.message || '检测服务不可用'}`);
  }
};

const checkDetectionService = async () => {
  try {
    const response = await fetch(`${detectionBaseUrl}/health`, { cache: 'no-store' });
    const data = await response.json();
    detectionService.ready = Boolean(data.modelReady && data.databaseReady);
    detectionService.classes = Array.isArray(data.modelClasses) ? data.modelClasses : [];
    detectionService.device = data.device || 'cpu';
    detectionService.deviceName = data.deviceName || (data.device || 'CPU');
    detectionService.tracking = data.tracking || '';
    detectionService.modelVersion = data.modelVersion || data.model || '';
    detectionService.message = data.modelError
      ? `模型不可用：${data.modelError}`
      : data.databaseReady === false
        ? '检测服务无法连接数据库'
        : response.ok ? '检测服务已就绪' : '检测服务尚未就绪';
    if (response.ok) refreshDisplayedTaskStates();
  } catch (error) {
    detectionService.ready = false;
    detectionService.classes = [];
    detectionService.tracking = '';
    detectionService.message = 'YOLO检测服务未启动';
  }
};

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

const getDetectionEvents = async () => {
  try {
    const response = await fetch(`${detectionBaseUrl}/events?limit=200`, { cache: 'no-store' });
    const result = await response.json();
    if (response.ok && result.success) {
      detectionEvents.value = Array.isArray(result.data) ? result.data : [];
    }
  } catch (error) {
    // 检测服务不可用时保留主告警列表，不干扰其他页面功能。
    detectionEvents.value = [];
  }
};

// 获取在线摄像头列表
const onlineCameras = computed(() => {
  return cameras.value.filter(camera => camera.status == 0);
});

const selectCameraById = (cameraId) => {
  const camera = onlineCameras.value.find(item => String(item.id) === String(cameraId));
  if (!camera) return;
  displayedCameras.splice(0, displayedCameras.length, camera);
  currentCamera.value = camera;
  if (!streamStates[camera.id]) streamStates[camera.id] = 'idle';
  loadRegionRule(camera.id);
  refreshDetectionTask(camera.id);
};

// 获取所有摄像头数据
const fetchCameras = async () => {
  try {
    loading.value = true;
    const response = await getAllCameras();
    cameras.value = response.data || [];
    if (displayedCameras.length === 0) {
      const firstOnlineCamera = cameras.value.find(camera => camera.status == 0);
      if (firstOnlineCamera) {
        displayedCameras.push(firstOnlineCamera);
        currentCamera.value = firstOnlineCamera;
        streamStates[firstOnlineCamera.id] = 'connecting';
        loadRegionRule(firstOnlineCamera.id);
        refreshDetectionTask(firstOnlineCamera.id);
      }
    }
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
    delete streamStates[camera.id];
  } else {
    // 添加到显示列表
    displayedCameras.push(camera);
    streamStates[camera.id] = 'connecting';
    
    // 设置为当前选中的摄像头
    currentCamera.value = camera;
    loadRegionRule(camera.id);
    refreshDetectionTask(camera.id);
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

const formatEventDate = (time) => {
  if (!time) return '时间未记录';
  const date = new Date(time);
  if (Number.isNaN(date.getTime())) return String(time);
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${month}-${day} ${formatTime(time)}`;
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
  loadRegionRule(cameraId);
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

const markAlertAsRead = (alert) => {
  const index = alerts.value.findIndex(item => String(item.id) === String(alert?.id));
  if (index >= 0) markAsRead(index);
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
  getDetectionEvents();
  
  // 设置每5秒获取一次数据
  alarmTimer.value = setInterval(() => {
    getUndisposedAlarmData();
    getDetectionEvents();
  }, 5000);
};

// 组件挂载与卸载
onMounted(() => {
  fetchCameras();
  checkDetectionService();
  healthTimer.value = setInterval(checkDetectionService, 5000);
  setupAlarmTimer(); // 启动定时获取警告信息
});

onUnmounted(() => {
  // 清理资源
  if (alarmTimer.value) {
    clearInterval(alarmTimer.value);
    alarmTimer.value = null;
  }
  if (healthTimer.value) {
    clearInterval(healthTimer.value);
    healthTimer.value = null;
  }
});
</script>

<style scoped>
.image-detection {
  display: flex;
  width: 100%;
  height: 100%;
  background-color: #f0f2f5;
  overflow-x: hidden;
  overflow-y: auto;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

h3 {
  text-align: center;
}

.detection-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.detection-title h3 {
  margin: 0;
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
  gap: 15px;
}

.video-item {
  position: relative;
  background-color: #000;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
  aspect-ratio: 16 / 9;
  min-height: 300px;
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

.stream-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.video-item img {
  width: 100%;
  height: 100%;
  object-fit: fill;
}

.region-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 6;
}

.region-overlay.drawing {
  pointer-events: auto;
  cursor: crosshair;
}

.region-polygon {
  fill: rgba(245, 158, 11, 0.20);
  stroke: #f59e0b;
  stroke-width: 5;
  vector-effect: non-scaling-stroke;
}

.region-polyline {
  fill: none;
  stroke: #f59e0b;
  stroke-width: 5;
  vector-effect: non-scaling-stroke;
}

.region-point {
  fill: #fff;
  stroke: #f59e0b;
  stroke-width: 5;
  vector-effect: non-scaling-stroke;
}

.stream-error {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  padding: 12px;
  border-radius: 4px;
  color: #fff;
  background: rgba(0, 0, 0, 0.72);
  text-align: center;
  z-index: 8;
}

.stream-idle {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  color: #d8e3ef;
  background: linear-gradient(135deg, #182a3b, #253f56);
  text-align: center;
  line-height: 1.6;
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
  height: 240px;
}

.region-panel {
  flex: 0 0 auto;
  border-bottom: 1px solid #dcdfe6;
}

.region-form {
  display: grid;
  gap: 9px;
  padding: 10px;
}

.region-option,
.region-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.region-option > span:first-child {
  color: #606266;
  font-size: 13px;
}

.region-hint {
  margin: 0;
  color: #909399;
  font-size: 12px;
  line-height: 1.45;
}

.foreign-object-rule {
  display: grid;
  gap: 8px;
  padding-top: 10px;
  border-top: 1px dashed #dcdfe6;
}

.foreign-object-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 13px;
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

.alert-evidence {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  color: #606266;
  font-size: 12px;
}

.alert-evidence img {
  width: 88px;
  height: 56px;
  object-fit: cover;
  border: 1px solid #dcdfe6;
  border-radius: 3px;
  cursor: zoom-in;
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

@media (max-width: 1180px) {
  .right-panel { width: 340px; }
  .video-grid { grid-template-columns: 1fr; }
}

@media (max-width: 760px) {
  .image-detection { flex-direction: column; overflow-y: auto; }
  .video-container { flex: 0 0 auto; min-height: 50%; height: auto; padding: 10px; }
  .detection-title { align-items: flex-start; flex-direction: column; }
  .video-item { min-height: 220px; }
  .right-panel { width: 100%; height: auto; min-height: 520px; border-left: 0; border-top: 1px solid #dcdfe6; }
  .camera-list-container { height: 180px; }
  .region-panel { max-height: 400px; overflow-y: auto; }
  .alert-evidence { flex-wrap: wrap; }
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

<style scoped>
* {
  box-sizing: border-box;
}

.image-detection {
  --primary: #1976d2;
  --primary-dark: #0f4f91;
  --surface: #ffffff;
  --surface-soft: #f7f9fc;
  --canvas: #f3f6fa;
  --text: #152235;
  --muted: #66758a;
  --border: #dce4ee;
  --success: #1f9d63;
  --warning: #d88918;
  --danger: #d94a4a;
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  height: 100%;
  padding: 14px;
  overflow-x: hidden;
  overflow-y: auto;
  color: var(--text);
  background: var(--canvas);
  font-family: "Microsoft YaHei", "PingFang SC", system-ui, sans-serif;
}

.workspace-header {
  flex: 0 0 76px;
  display: grid;
  grid-template-columns: minmax(250px, auto) 220px minmax(330px, 1fr) auto;
  align-items: center;
  gap: 20px;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface);
  box-shadow: 0 4px 16px rgba(32, 61, 92, 0.05);
}

.eyebrow {
  margin-bottom: 4px;
  color: var(--primary);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-row h1,
.card-heading h2,
.rule-panel-header h2 {
  margin: 0;
  color: var(--text);
  font-weight: 700;
}

.title-row h1 {
  font-size: 22px;
  letter-spacing: -0.02em;
}

.title-row p {
  margin: 0;
  color: var(--muted);
  font-size: 12px;
  white-space: nowrap;
}

.title-divider {
  width: 1px;
  height: 14px;
  background: var(--border);
}

.camera-selector label,
.field-label {
  display: block;
  margin-bottom: 6px;
  color: #43536a;
  font-size: 12px;
  font-weight: 700;
}

.camera-selector :deep(.el-select) {
  width: 100%;
}

.status-cluster {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 22px;
  min-width: 0;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 88px;
}

.status-item > div {
  display: grid;
  min-width: 0;
}

.status-item small {
  color: #8390a1;
  font-size: 10px;
  line-height: 1.3;
}

.status-item strong {
  overflow: hidden;
  color: #26364c;
  font-size: 12px;
  line-height: 1.5;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-dot {
  flex: 0 0 8px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #9aa7b7;
  box-shadow: 0 0 0 4px rgba(154, 167, 183, 0.12);
}

.status-dot.is-success {
  background: var(--success);
  box-shadow: 0 0 0 4px rgba(31, 157, 99, 0.12);
}

.status-dot.is-warning {
  background: var(--warning);
  box-shadow: 0 0 0 4px rgba(216, 137, 24, 0.12);
}

.status-dot.is-danger {
  background: var(--danger);
  box-shadow: 0 0 0 4px rgba(217, 74, 74, 0.12);
}

.header-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.workspace-body {
  flex: 0 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 1040px) minmax(440px, 1fr);
  align-items: start;
  gap: 12px;
}

.main-column {
  min-width: 0;
  display: grid;
  grid-template-rows: auto auto;
  gap: 12px;
}

.monitor-card,
.events-card,
.rule-panel {
  min-height: 0;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface);
  box-shadow: 0 4px 16px rgba(32, 61, 92, 0.05);
}

.monitor-card,
.events-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.events-card {
  min-height: 460px;
}

.card-heading {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
}

.card-heading h2,
.rule-panel-header h2 {
  font-size: 15px;
}

.card-heading p,
.rule-panel-header p {
  margin: 3px 0 0;
  color: var(--muted);
  font-size: 11px;
}

.monitor-legend {
  display: flex;
  align-items: center;
  gap: 14px;
  color: #66758a;
  font-size: 11px;
}

.monitor-legend span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.legend-box {
  width: 10px;
  height: 10px;
  border: 2px solid var(--primary);
  border-radius: 2px;
}

.legend-box.is-region {
  border-color: #f0a020;
  background: rgba(240, 160, 32, 0.18);
}

.legend-box.is-event {
  border-color: #ec6a5c;
  background: #ec6a5c;
}

.monitor-stage {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  overflow: visible;
  background:
    linear-gradient(rgba(28, 48, 69, 0.65), rgba(20, 37, 54, 0.65)),
    repeating-linear-gradient(0deg, transparent 0 31px, rgba(123, 161, 196, 0.035) 31px 32px),
    #172a3d;
}

.video-item {
  position: relative;
  width: 100%;
  height: auto;
  max-width: none;
  max-height: none;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  border: 0;
  border-radius: 0;
  background: #08121d;
  box-shadow: none;
}

.stream-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.video-item img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #08121d;
}

.camera-overlay-name {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 7;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 9px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 5px;
  color: #f4f8fc;
  background: rgba(10, 24, 38, 0.72);
  backdrop-filter: blur(6px);
  font-size: 12px;
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #8c98a5;
}

.live-dot.is-live {
  background: #35c67b;
  animation: livePulse 1.8s ease-out infinite;
}

.stream-idle,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  height: 100%;
  padding: 24px;
  color: #d9e5ef;
  text-align: center;
}

.stream-idle {
  background: radial-gradient(circle at 50% 40%, rgba(32, 90, 137, 0.32), transparent 54%);
}

.stream-idle strong,
.empty-state strong {
  color: #f4f8fc;
  font-size: 17px;
}

.stream-idle span,
.empty-state span {
  max-width: 460px;
  color: #aebfce;
  font-size: 12px;
  line-height: 1.6;
}

.idle-symbol {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border: 1px solid rgba(91, 159, 219, 0.4);
  border-radius: 50%;
  color: #79b9f0;
  background: rgba(28, 91, 145, 0.2);
  font-size: 22px;
}

.empty-state {
  min-height: 260px;
  color: #7e8da0;
}

.empty-state strong {
  color: #405067;
}

.empty-state span {
  color: #7e8da0;
}

.state-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #cbd8e6;
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.stream-error {
  position: absolute;
  inset: 50% auto auto 50%;
  z-index: 8;
  display: grid;
  gap: 5px;
  width: min(420px, 82%);
  padding: 14px 16px;
  transform: translate(-50%, -50%);
  border: 1px solid rgba(255, 142, 142, 0.52);
  border-radius: 7px;
  color: #ffd9d9;
  background: rgba(75, 22, 28, 0.9);
  text-align: center;
}

.stream-error span {
  font-size: 12px;
  line-height: 1.55;
}

.region-overlay {
  position: absolute;
  inset: 0;
  z-index: 6;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.region-overlay.drawing {
  cursor: crosshair;
  pointer-events: auto;
}

.region-polygon {
  fill: rgba(245, 158, 11, 0.2);
  stroke: #f5a623;
  stroke-width: 4;
  vector-effect: non-scaling-stroke;
}

.region-polyline {
  fill: none;
  stroke: #f5a623;
  stroke-width: 4;
  vector-effect: non-scaling-stroke;
}

.region-point {
  fill: #ffffff;
  stroke: #f5a623;
  stroke-width: 4;
  vector-effect: non-scaling-stroke;
}

.monitor-footer {
  flex: 0 0 32px;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 0 16px;
  border-top: 1px solid var(--border);
  color: #718096;
  background: #fbfcfe;
  font-size: 10px;
}

.monitor-footer span::before {
  content: "";
  display: inline-block;
  width: 4px;
  height: 4px;
  margin: 0 6px 2px 0;
  border-radius: 50%;
  background: #9aa9bb;
}

.events-heading {
  padding-block: 10px;
}

.events-scroll {
  flex: 0 0 auto;
  overflow: visible;
}

.events-empty {
  display: grid;
  place-items: center;
  min-height: 180px;
  color: #7f8da0;
  font-size: 12px;
}

.event-row {
  position: relative;
  display: grid;
  grid-template-columns: 84px minmax(180px, 1fr) 132px auto;
  align-items: center;
  gap: 12px;
  min-height: 80px;
  padding: 10px 14px 10px 16px;
  border-bottom: 1px solid #e7edf4;
  background: #ffffff;
  transition: background-color 0.18s ease;
}

.event-row::before {
  content: "";
  position: absolute;
  inset: 12px auto 12px 0;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: #4b91d1;
}

.event-row.level-0::before { background: var(--danger); }
.event-row.level-1::before { background: var(--warning); }
.event-row:hover { background: #f8fbff; }

.event-thumb {
  width: 84px;
  height: 54px;
  padding: 0;
  overflow: hidden;
  border: 1px solid #d6e0eb;
  border-radius: 5px;
  background: #eef3f8;
  cursor: zoom-in;
}

.event-thumb img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.event-thumb.placeholder {
  display: grid;
  place-items: center;
  color: #93a0af;
  font-size: 10px;
  cursor: default;
}

.event-summary,
.event-review {
  min-width: 0;
}

.event-title-line {
  display: flex;
  align-items: center;
  gap: 7px;
}

.event-title-line strong {
  overflow: hidden;
  color: #26364c;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-summary p {
  overflow: hidden;
  margin: 5px 0 3px;
  color: #617086;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-summary > span,
.event-review > span {
  color: #8996a6;
  font-size: 10px;
}

.event-review {
  display: grid;
  justify-items: start;
  gap: 5px;
}

.event-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
  white-space: nowrap;
}

.rule-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: sticky;
  top: 0;
  height: calc(100vh - 88px);
}

.rule-panel-header {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px 10px;
}

.rule-tabs {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.rule-tabs :deep(.el-tabs__header) {
  flex: 0 0 auto;
  margin: 0 16px;
}

.rule-tabs :deep(.el-tabs__content) {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.rule-content {
  display: grid;
  gap: 16px;
  padding: 16px;
}

.rule-intro {
  display: grid;
  gap: 4px;
  padding-bottom: 2px;
}

.rule-intro strong {
  font-size: 13px;
}

.rule-intro span,
.field-help,
.drawing-status p,
.baseline-card p,
.prototype-banner span,
.service-note p {
  margin: 0;
  color: var(--muted);
  font-size: 11px;
  line-height: 1.55;
}

.field-block {
  display: grid;
  gap: 6px;
  padding: 10px 0 12px;
  border-bottom: 1px solid #edf1f5;
}

.field-block .field-label {
  margin-bottom: 0;
}

.target-class-group {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  width: 100%;
}

.target-class-group :deep(.el-checkbox-button__inner) {
  width: 100%;
  padding: 8px 12px;
}

.field-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 12px 0;
  border-top: 1px solid #edf1f5;
  border-bottom: 1px solid #edf1f5;
}

.field-row + .field-row {
  margin-top: -17px;
  border-top: 0;
}

.field-row .field-label {
  margin-bottom: 2px;
}

.number-field {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--muted);
  font-size: 11px;
}

.number-field :deep(.el-input-number) {
  width: 116px;
}

.drawing-status,
.baseline-card,
.prototype-banner,
.rule-notice {
  border: 1px solid #dbe5f0;
  border-radius: 7px;
  background: var(--surface-soft);
}

.drawing-status {
  padding: 12px;
}

.drawing-status.active {
  border-color: #f0b253;
  background: #fff9ee;
}

.drawing-status-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 4px;
}

.drawing-status-top strong {
  font-size: 12px;
}

.drawing-status-top span {
  color: #7a8797;
  font-size: 10px;
}

.drawing-actions {
  display: grid;
  grid-template-columns: 1.25fr 1fr 0.75fr;
  gap: 7px;
}

.drawing-actions :deep(.el-button) {
  width: 100%;
  margin: 0;
}

.rule-notice {
  padding: 10px 12px;
  border-color: #d7e6f6;
  color: #4d6d8d;
  background: #f1f7fd;
  font-size: 11px;
  line-height: 1.55;
}

.primary-rule-action {
  width: 100%;
  margin-top: 2px;
}

.secondary-rule-action {
  width: 100%;
  margin: -8px 0 0 !important;
}

.prototype-banner {
  display: grid;
  gap: 3px;
  padding: 11px 12px;
  border-color: #f0d6a9;
  background: #fff9ef;
}

.prototype-banner strong {
  color: #9a6215;
  font-size: 12px;
}

.baseline-card {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 13px;
}

.baseline-card.ready {
  border-color: #bfe4d1;
  background: #f2fbf6;
}

.baseline-card strong {
  color: #31445a;
  font-size: 12px;
}

.baseline-icon {
  flex: 0 0 34px;
  width: 34px;
  height: 34px;
  border: 2px solid #9aabbd;
  border-radius: 50%;
  box-shadow: inset 0 0 0 7px #ffffff;
  background: #9aabbd;
}

.baseline-card.ready .baseline-icon {
  border-color: var(--success);
  background: var(--success);
}

.workflow-steps {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.workflow-steps li {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #58687d;
  font-size: 11px;
}

.workflow-steps span {
  display: grid;
  place-items: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  color: #276ba8;
  background: #eaf3fb;
  font-size: 10px;
  font-weight: 700;
}

.service-note {
  flex: 0 0 auto;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin: 10px 12px 12px;
  padding: 10px 12px;
  border: 1px solid #cfe6d9;
  border-radius: 7px;
  background: #f4faf7;
}

.service-note.error {
  border-color: #f0caca;
  background: #fff6f6;
}

.service-note .status-dot {
  margin-top: 5px;
}

.service-note strong {
  color: #34465b;
  font-size: 11px;
}

.image-detection :deep(.el-button) {
  border-radius: 5px;
  cursor: pointer;
}

.image-detection :deep(.el-button:focus-visible),
.event-thumb:focus-visible {
  outline: 2px solid #4b9fea;
  outline-offset: 2px;
}

.image-detection :deep(.el-input__wrapper),
.image-detection :deep(.el-select__wrapper) {
  border-radius: 5px;
  box-shadow: 0 0 0 1px #d5dfeb inset;
}

.image-detection :deep(.el-input__wrapper:hover),
.image-detection :deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px #8bbce9 inset;
}

.events-scroll,
.rule-tabs :deep(.el-tabs__content) {
  scrollbar-width: thin;
  scrollbar-color: #b8c6d5 transparent;
}

@keyframes livePulse {
  0% { box-shadow: 0 0 0 0 rgba(53, 198, 123, 0.42); }
  70% { box-shadow: 0 0 0 7px rgba(53, 198, 123, 0); }
  100% { box-shadow: 0 0 0 0 rgba(53, 198, 123, 0); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 1380px) {
  .workspace-header {
    grid-template-columns: minmax(210px, auto) 190px minmax(280px, 1fr) auto;
    gap: 12px;
  }

  .status-cluster { gap: 12px; }
  .workspace-body { grid-template-columns: minmax(0, 1fr) 400px; }
  .event-row { grid-template-columns: 72px minmax(150px, 1fr) 110px auto; gap: 9px; }
  .event-thumb { width: 72px; height: 48px; }
  .event-actions :deep(.el-button) { padding-inline: 8px; }
}

@media (max-width: 1120px) {
  .image-detection { overflow-y: auto; }
  .workspace-header { grid-template-columns: 1fr 210px auto; height: auto; }
  .status-cluster { display: none; }
  .workspace-body { grid-template-columns: 1fr 300px; min-height: 720px; }
  .monitor-legend { display: none; }
  .event-review { display: none; }
  .event-row { grid-template-columns: 64px minmax(130px, 1fr) auto; }
}

@media (prefers-reduced-motion: reduce) {
  .live-dot.is-live,
  .state-spinner {
    animation: none;
  }
}

:fullscreen.video-item {
  width: 100vw;
  max-width: none;
  height: 100vh;
  max-height: none;
  border: 0;
  border-radius: 0;
}

/* 视频工作台：画面优先，规则与事件保留原有操作 */
.image-detection { background:linear-gradient(135deg,#eef5fa,#f5f8fb 54%,#ecf4f8); }
.workspace-header { border:0;border-bottom:2px solid #63b9d2;border-radius:8px 8px 4px 4px;background:linear-gradient(100deg,#fff,#f8fbfd);box-shadow:0 6px 22px rgba(23,65,95,.05); }
.workspace-body { grid-template-columns:minmax(0,1fr) minmax(390px,31%);gap:16px; }
.monitor-card,.events-card,.rule-panel { border:0;border-top:2px solid #81c5d9;border-radius:7px;background:#fff;box-shadow:0 6px 24px rgba(23,65,95,.055); }
.monitor-stage { background:#14283b; }
.card-heading,.rule-panel-header { background:linear-gradient(90deg,#f8fcfe,#fff); }
@media (max-width:1120px) { .workspace-body { grid-template-columns:minmax(0,1fr) 320px; } }
</style>
  
