<template>
  <main class="media-workspace original-page" aria-label="人车识别">
    <header class="media-heading">
      <div><h1>人车识别</h1><p>导入站场录像，查看目标检测结果，回看关键画面。</p></div>
      <router-link v-if="alarmEvent" class="media-action" :to="{ path: '/alarm', query: { kind: 'danger', event: alarmEvent } }">返回告警核查</router-link>
    </header>

    <section class="media-bar recognition-bar" aria-label="识别操作">
      <div class="recognition-source">
        <span class="media-status">来源</span>
        <div class="mode-buttons" role="group" aria-label="识别来源">
          <button v-for="item in modes" :key="item.value" type="button" class="media-action"
            :aria-pressed="mode === item.value" :disabled="active || starting || savingClip" @click="selectMode(item.value)">{{ item.label }}</button>
        </div>
      </div>

      <div v-if="mode === 'image' || mode === 'video'" class="source-control">
        <input id="original-file" ref="fileInput" :key="mode" class="file-input" tabindex="-1" type="file"
          :accept="mode === 'image' ? '.jpg,.jpeg,.png,.webp,.bmp' : '.mp4,.avi,.mov,.mkv,.webm,.wmv,.flv,.mpg,.mpeg'"
          :disabled="active || starting || savingClip" @change="selectFile" />
        <button type="button" class="media-action" :disabled="active || starting || savingClip" @click="openFile">{{ mode === 'image' ? '选择图片' : '选择本地视频' }}</button>
        <span v-if="file" class="media-source-title media-status" :title="sourceName">{{ sourceName }} · {{ formatSize(file.size) }}</span>
        <span v-else class="media-status source-limit">{{ mode === 'image' ? '最大 16 MB' : '最大 512 MB' }}</span>
      </div>
      <div v-else-if="mode === 'usb'" class="source-control">
        <label class="media-status" for="original-usb">本机摄像头编号</label>
        <el-input-number id="original-usb" v-model="deviceIndex" :min="0" :max="9" :disabled="active || starting" @change="clearResult()" />
      </div>
      <div v-else class="source-control">
        <el-select v-model="cameraId" aria-label="选择网络摄像头" placeholder="选择网络摄像头" :disabled="active || starting" :loading="loadingCameras" @change="clearResult()">
          <el-option v-for="camera in cameras" :key="camera.id" :value="camera.id" :label="camera.name || `摄像头 ${camera.id}`" />
        </el-select>
        <button type="button" class="media-action" :disabled="active || starting || loadingCameras" @click="loadCameras">刷新设备</button>
      </div>

      <div class="media-actions recognition-controls">
        <button v-if="!active" type="button" class="media-action media-action--primary" :disabled="starting || !connected || !hasInput" @click="start()">{{ starting ? '正在启动…' : mode === 'video' ? '开始录像识别' : '开始识别' }}</button>
        <button v-if="active && job?.mode === 'video'" type="button" class="media-action"
          :disabled="controlling || job.state === 'loading' || job.state === 'stopping'"
          @click="control(job.state === 'paused' ? 'resume' : 'pause')">{{ job.state === 'paused' ? '继续识别' : '暂停识别' }}</button>
        <button v-if="active" type="button" class="media-action" :disabled="controlling || job.state === 'stopping'" @click="control('stop')">停止识别</button>
        <button v-if="!connected" type="button" class="media-action" @click="connect">重新连接</button>
        <span v-if="!connected" class="media-status" data-tone="attention" role="status">{{ connecting ? '正在连接识别服务' : '识别服务暂不可用' }}</span>
      </div>
      <p v-if="error || cameraError && mode === 'rtsp'" class="media-feedback recognition-error" role="alert">{{ error || cameraError }}</p>
      <p v-if="linkedLoading || linkedFeedback" class="linked-feedback" role="status" :data-tone="linkedFeedback && !recording ? 'attention' : undefined">
        {{ linkedLoading ? '正在加载系统录像…' : linkedFeedback }}
      </p>
    </section>

    <div class="media-columns recognition-columns">
      <section class="media-panel media-viewer viewer-card" aria-label="识别画面">
        <header class="media-panel-head">
          <h2 class="media-source-title" :title="sourceName">{{ sourceName }}</h2>
          <span class="media-status" :data-tone="job?.state === 'failed' || pollFailed ? 'attention' : undefined" role="status">{{ statusText }}</span>
        </header>
        <div class="media-surface recognition-surface">
          <RecognitionFrame v-if="currentFrame" :frame="currentFrame" :annotated="view === 'annotated'" :selected="selectedTarget" :zoom="zoom"
            :region="visibleRegion" :edit-region="editingVisibleRegion" @region-point="addReviewPoint" />
          <img v-if="showSource && previewUrl && !previewUnavailable && mode === 'image'" :src="previewUrl" alt="所选图片的原始画面" @error="previewUnavailable = true" />
          <video v-if="previewUrl && mode === 'video'" v-show="showSource && !previewUnavailable"
            ref="previewVideo" crossorigin="anonymous" :src="previewUrl" muted playsinline preload="metadata" aria-label="所选录像的原始画面"
            @loadedmetadata="loadVideoMetadata" @timeupdate="updatePlayhead" @play="videoPlaying = true"
            @pause="onVideoPause" @ended="onVideoPause" @error="onPreviewError" />
          <div v-if="!currentFrame && !(showSource && previewUrl && !previewUnavailable)" class="media-placeholder">
            <strong>{{ placeholderTitle }}</strong>
            <p class="media-help">{{ placeholderHint }}</p>
            <button v-if="!hasInput && (mode === 'image' || mode === 'video')" type="button" class="media-action placeholder-action" @click="openFile">
              {{ mode === 'image' ? '选择图片' : '选择本地视频' }}
            </button>
          </div>
          <span v-if="currentFrame || showSource && previewUrl && !previewUnavailable" class="media-stamp">
            {{ currentFrame ? (view === 'annotated' ? '检测标注' : '同帧原画') : '原始画面' }}
            <template v-if="heldFrame"> · 已固定</template>
          </span>
          <span v-if="cameraInterrupted" class="stale-frame media-stamp">画面已中断 · 最后更新 {{ lastFrameTime }}</span>
        </div>
        <div v-if="canPlay || currentFrame || latestFrame" class="viewer-controls">
          <div class="media-actions">
            <button v-if="canPlay" type="button" class="media-action" @click="togglePlayback">{{ videoPlaying ? '暂停回放' : '播放原录像' }}</button>
            <button v-if="canPlay && showSource && !active" type="button" class="media-action" :disabled="starting || !connected || videoPlaying" @click="recognizePlayhead">识别当前画面</button>
            <button v-if="currentFrame" type="button" class="media-action" @click="toggleAnnotation">{{ view === 'annotated' ? '查看同帧原画' : '查看检测标注' }}</button>
            <button v-if="currentFrame" type="button" class="media-action" :disabled="editingVisibleRegion" :aria-pressed="zoom > 1" @click="zoom = zoom > 1 ? 1 : 2">{{ zoom > 1 ? '恢复画面' : '放大画面' }}</button>
            <button v-if="latestFrame && (heldFrame || view === 'source')" type="button" class="media-action" @click="followLatest">{{ active ? '跟随识别' : '查看最后检测帧' }}</button>
          </div>
          <span class="media-status frame-clock">{{ frameDescription }}</span>
        </div>
        <div v-if="mode === 'video' && hasInput" class="review-timeline">
          <div class="timeline-label">
            <span>{{ canPlay ? '录像时间轴' : '录像预览尚未就绪' }}</span>
            <span v-if="job?.totalFrames">已处理 {{ job.frameIndex || 0 }} / {{ job.totalFrames }} 帧</span>
          </div>
          <input v-if="canPlay" aria-label="录像播放位置" type="range" min="0" :max="duration" step="0.01" :value="displaySeconds" @input="seekOriginal($event.target.value)" />
          <div v-if="canPlay && (timelineClips.length || eventSeconds != null)" class="clip-markers" role="group" aria-label="录像片段标记">
            <button v-if="eventSeconds != null" type="button" class="clip-marker event-marker"
              :style="{ left: markerPosition(eventSeconds) }" aria-label="回到告警时刻" @click="seekOriginal(eventSeconds)">告警</button>
            <button v-for="(clip, index) in timelineClips" :key="clip.id" type="button" class="clip-marker"
              :style="{ left: markerPosition(clip.at), top: markerTop(index) }"
              :class="{ 'is-selected': clip.id === selectedClip?.id }"
              :aria-label="'复核标记 ' + (index + 1) + ' · ' + timecode(clip.at)" @click="selectClip(clip)">{{ index + 1 }}</button>
          </div>
          <div v-if="canPlay" class="timeline-label">
            <div class="media-actions">
              <button type="button" class="media-action skip-action" @click="seekOriginal(displaySeconds - 5)">后退 5 秒</button>
              <button type="button" class="media-action skip-action" @click="seekOriginal(displaySeconds + 5)">前进 5 秒</button>
            </div>
            <span class="frame-clock">{{ timecode(displaySeconds) }} / {{ timecode(duration) }}</span>
          </div>
        </div>
      </section>

      <aside class="media-side" aria-label="识别结果与说明">
        <section class="media-panel recognition-results" aria-label="当前帧检测结果">
          <header class="media-panel-head"><h2>当前帧检测结果</h2><span v-if="currentFrame" class="media-status">{{ currentFrame.mediaSeconds == null ? '第 ' + currentFrame.frameIndex + ' 帧' : timecode(currentFrame.mediaSeconds) }}</span></header>
          <template v-if="currentFrame">
            <div class="recognition-counts">
              <div v-for="(count, label) in currentFrame.counts" :key="label">{{ detectionLabel(label) }}框 <strong>{{ count }}</strong></div>
            </div>
            <div v-if="currentFrame.detections.length" class="recognition-list" role="group" aria-label="检测目标列表">
              <button v-for="(row, index) in currentFrame.detections" :key="index" type="button" class="target-row"
                :aria-pressed="selectedTarget === index" @click="focusTarget(index)">
                <span class="target-dot" :class="row.label" aria-hidden="true"></span><span>{{ detectionLabel(row.label) }} {{ index + 1 }}</span><span aria-hidden="true">›</span>
              </button>
            </div>
            <p v-else class="media-help result-note">当前帧未检出目标。</p>
            <p v-if="targetDetails" class="target-details media-help">
              <strong>{{ detectionLabel(targetDetails.label) }} {{ selectedTarget + 1 }}</strong>
              <span>模型置信度 {{ (targetDetails.confidence * 100).toFixed(1) }}%</span>
              <span v-if="regionMatches">{{ regionMatches[selectedTarget] ? '框底中心在复核区域内' : '框底中心在复核区域外' }}</span>
            </p>
          </template>
          <p v-else class="media-help result-note">{{ resultNote }}</p>
        </section>
        <section v-if="mode === 'video' && (job?.mode === 'video' || detectionSamples.length)"
          class="media-panel" aria-label="检测画面回看">
          <header class="media-panel-head"><h2>检测画面回看</h2></header>
          <div class="detection-sample-content">
            <p class="media-help">{{ detectionSamples.length ? '点击时刻核对同帧原画和检测框。这里保留含检测框的部分画面。' : active ? '正在识别，含检测框的部分画面会出现在这里。' : '本次没有保留含检测框的画面。' }}</p>
            <ul v-if="detectionSamples.length" class="clip-list" aria-label="识别时刻">
              <li v-for="sample in detectionSamples" :key="sample.frameIndex">
                <button type="button" class="target-row" :aria-pressed="heldFrame === sample" @click="showDetectionSample(sample)">
                  <span class="frame-clock">{{ timecode(sample.mediaSeconds) }}</span>
                  <span>{{ detectionSummary(sample.counts) }}</span>
                  <span aria-hidden="true">›</span>
                </button>
              </li>
            </ul>
          </div>
        </section>
        <details v-if="localInput && currentFrame && !active" class="media-panel media-disclosure">
          <summary>画面区域复核</summary>
          <div class="review-region-controls">
            <p class="media-help">{{ editingVisibleRegion ? '沿边界依次点击画面添加顶点，也可以输入百分比坐标。' : '按目标框底边中心判断与手绘区域的关系，仅用于当前帧复核。' }}</p>
            <p v-if="regionMatches" class="media-status" role="status">区域内目标框 {{ regionMatches.filter(Boolean).length }} 个</p>
            <div class="media-actions">
              <button v-if="!editingVisibleRegion" type="button" class="media-action" @click="beginReviewRegion">{{ regionMatches ? '重新绘制' : '绘制复核区域' }}</button>
              <template v-else>
                <button type="button" class="media-action media-action--primary" :disabled="regionPoints.length < 3" @click="finishReviewRegion">查看区域结果</button>
                <button type="button" class="media-action" :disabled="!regionPoints.length" @click="undoReviewPoint">撤销顶点</button>
              </template>
              <button v-if="editingVisibleRegion || regionMatches" type="button" class="media-action" @click="resetReviewRegion">{{ editingVisibleRegion ? '取消' : '清除区域' }}</button>
            </div>
            <form v-if="editingVisibleRegion" class="review-region-coordinates" @submit.prevent="addReviewCoordinate">
              <label>横向（%）<input v-model.number="regionX" required type="number" min="0" max="100" step="any" /></label>
              <label>纵向（%）<input v-model.number="regionY" required type="number" min="0" max="100" step="any" /></label>
              <button type="submit" class="media-action" :disabled="regionPoints.length >= 20">添加顶点</button>
            </form>
            <p v-if="editingVisibleRegion" class="media-status">{{ regionPoints.length }} / 20 个顶点</p>
            <p v-if="editingVisibleRegion && regionMessage" class="media-feedback" role="alert">{{ regionMessage }}</p>
          </div>
        </details>
        <section v-if="mode === 'video'" class="media-panel clip-panel" aria-label="片段复核">
          <header class="media-panel-head"><h2>片段复核</h2><span class="media-status">{{ recording ? '交接可查' : '本次页面' }}</span></header>
          <div class="clip-content">
            <p v-if="reviewListError" class="media-feedback" role="status">{{ reviewListError }}</p>
            <p v-if="recording && !clips.length && !draft && !reviewListError && !linkedLoading" class="media-help">这段录像暂无复核记录。</p>
            <template v-if="!draft">
              <button type="button" class="media-action media-action--primary" :disabled="!canPlay || localLimitReached" @click="beginClip">标记当前片段</button>
              <p v-if="!canPlay || !clips.length || localLimitReached" class="media-help">
                {{ !canPlay ? '载入可播放的录像后，在关键时刻标记片段。' : localLimitReached ? '本次已保留 12 段，可删除一段后继续标记。' : '以当前时刻为参考，默认取前后各 5 秒。' }}
              </p>
            </template>
            <form v-else class="clip-form" @submit.prevent="saveClip">
              <p class="media-help">代表时刻 {{ timecode(draft.at) }} · {{ draft.frame ? '已保留同帧检测结果' : '使用原录像画面' }}</p>
              <div class="clip-range">
                <label>起点（秒）<input v-model.number="draft.start" type="number" min="0" :max="draft.at" step="any" required /></label>
                <label>终点（秒）<input v-model.number="draft.end" type="number" :min="draft.at" :max="duration" step="any" required /></label>
              </div>
              <label>复核意见<select v-model="draft.outcome" required><option value="" disabled>请选择</option><option v-for="(label, key) in outcomes" :key="key" :value="key">{{ label }}</option></select></label>
              <label>补充说明（选填）<textarea v-model.trim="draft.note" maxlength="200" rows="2" /></label>
              <p v-if="clipMessage" class="media-feedback" role="alert">{{ clipMessage }}</p>
              <div class="media-actions"><button type="submit" class="media-action media-action--primary" :disabled="savingClip">{{ savingClip ? '正在保存…' : '保存复核' }}</button><button type="button" class="media-action" :disabled="savingClip" @click="cancelClip">取消</button></div>
            </form>
            <div v-if="selectedClip" class="clip-selected">
              <p class="media-help">{{ timecode(selectedClip.start) }} – {{ timecode(selectedClip.end) }} · {{ outcomes[selectedClip.outcome] }}</p>
              <p v-if="selectedClip.reviewerId" class="media-help">复核人 #{{ selectedClip.reviewerId }} · {{ formatReviewTime(selectedClip.createdAt) }}</p>
              <p v-if="selectedClip.note" class="media-help">{{ selectedClip.note }}</p>
              <div class="media-actions">
                <button type="button" class="media-action" :disabled="!canPlay" @click="playClip(selectedClip)">回看该片段</button>
                <button v-if="selectedClip.frame" type="button" class="media-action" @click="selectClip(selectedClip)">代表检测帧</button>
                <button v-if="!selectedClip.reviewerId" type="button" class="media-action" @click="removeClip(selectedClip.id)">删除标记</button>
              </div>
            </div>
            <ul v-if="clips.length" class="clip-list" aria-label="录像复核记录">
              <li v-for="clip in clips" :key="clip.id">
                <button type="button" class="target-row" :aria-pressed="clip.id === selectedClip?.id" @click="selectClip(clip)">
                  <span>{{ timecode(clip.at) }}</span><span>{{ outcomes[clip.outcome] }}</span><span aria-hidden="true">›</span>
                </button>
              </li>
            </ul>
          </div>
        </section>
        <details class="media-panel media-disclosure model-info">
          <summary>识别说明与技术信息</summary>
          <div class="model-details">
            <p class="media-help">已产生的业务告警可在「告警中心」查看。</p>
            <label v-if="localInput && profiles.length > 1" class="inference-profile">
              识别配置
              <select v-model="profile" :disabled="active || starting || savingClip">
                <option v-for="item in profiles" :key="item.id" :value="item.id">
                  {{ item.inputSize === 1280 ? '细节复核' : '标准识别' }} · {{ item.inputSize }}
                </option>
              </select>
            </label>
            <dl>
              <div><dt>模型</dt><dd>{{ inference?.model || '—' }}</dd></div>
              <div><dt>识别类别</dt><dd>{{ (inference?.classes ?? ['person', 'car']).map(detectionLabel).join('、') }}</dd></div>
              <div><dt>{{ frameInference ? '本帧推理输入' : '默认推理输入' }}</dt><dd>{{ inference?.inputSize ?? 640 }} · 整图</dd></div>
              <div><dt>阈值</dt><dd>置信度 {{ inference?.confidence ?? 0.25 }} / NMS IoU {{ inference?.iou ?? 0.7 }}</dd></div>
              <div><dt>运行设备</dt><dd>{{ inference?.device?.toUpperCase() || 'CPU' }}</dd></div>
              <div v-if="currentFrame"><dt>本帧耗时</dt><dd>{{ currentFrame.processingMs }} ms</dd></div>
              <div v-if="currentFrame"><dt>平均处理频率</dt><dd>{{ currentFrame.completedHz }} 帧/秒</dd></div>
            </dl>
          </div>
        </details>
      </aside>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import RecognitionFrame from '@/components/RecognitionFrame.vue';
import { detectionInReviewRegion, regionError } from '@/utils/reviewRegion';
import { detectionLabel } from '@/utils/detectionLabels';
import { getRecordingMatch, getRecordingFile, getRecordingReviews, saveRecordingReview } from '@/http/api/recording.js';
import '@/assets/style/media-workspace.css';

// Local-only service. No footage is sent to a cloud service or business database.
const API = 'http://127.0.0.1:5002/original';
const modes = [{ value: 'image', label: '图片' }, { value: 'video', label: '本地视频' }, { value: 'usb', label: '本机摄像头' }, { value: 'rtsp', label: '网络摄像头' }];
const mode = ref('video'), file = ref(null), deviceIndex = ref(0), cameraId = ref(null);
const cameras = ref([]), loadingCameras = ref(false), cameraError = ref('');
const connected = ref(false), connecting = ref(false), starting = ref(false), controlling = ref(false), error = ref('');
const config = ref(null), profile = ref('full640');
const profiles = computed(() => config.value?.profiles ?? []);
const localInput = computed(() => mode.value === 'image' || mode.value === 'video');
const job = ref(null), latestFrame = ref(null), heldFrame = ref(null);
const detectionSamples = ref([]);
const sampleLimit = 12;
const view = ref('source'), selectedTarget = ref(null), zoom = ref(1);
const duration = ref(0), playhead = ref(0), videoPlaying = ref(false), pollFailed = ref(false);
const clips = ref([]), selectedClip = ref(null), draft = ref(null), clipMessage = ref('');
const recording = ref(null), linkedLoading = ref(false), linkedFeedback = ref(''), reviewListError = ref('');
const eventSeconds = ref(null), savingClip = ref(false);
const route = useRoute(), router = useRouter();
const alarmEvent = computed(() => typeof route.query.event === 'string' ? route.query.event : null);
let linkedAbort = null;
let initialSeek = null;
let singleFrameSeconds = null;
const clipLimit = 12;
const outcomes = { visible: '画面中可见目标', misread: '疑似误检', unclear: '画面不足，无法判断' };
const localLimitReached = computed(() => !recording.value && clips.value.length >= clipLimit);
const timelineClips = computed(() => {
  const markers = clips.value.slice(0, clipLimit);
  if (selectedClip.value && !markers.some(clip => clip.id === selectedClip.value.id)) markers.push(selectedClip.value);
  return markers;
});
let clipPlaybackEnd = null;
const fileInput = ref(null), previewVideo = ref(null), previewUrl = ref(''), previewUnavailable = ref(false), previewConverting = ref(false), previewConverted = ref(false);
let token = '', timer = null, disposed = false, generation = 0, pollRevision = 0;
let previewGeneration = 0, previewAbort = null;
const requests = new Set();
const active = computed(() => job.value && ['loading', 'running', 'paused', 'stopping'].includes(job.value.state));
const hasInput = computed(() => ['image', 'video'].includes(mode.value) ? Boolean(file.value) : mode.value === 'usb' ? Number.isInteger(deviceIndex.value) : Boolean(cameraId.value));
const showSource = computed(() => view.value === 'source');
const currentFrame = computed(() => showSource.value ? null : heldFrame.value || latestFrame.value);
const regionFrame = ref(null), regionPoints = ref([]), editingRegion = ref(false), regionMessage = ref('');
const regionX = ref(50), regionY = ref(50);
const visibleRegion = computed(() => currentFrame.value && currentFrame.value === regionFrame.value ? regionPoints.value : []);
const editingVisibleRegion = computed(() => Boolean(currentFrame.value && currentFrame.value === regionFrame.value && editingRegion.value));
const regionMatches = computed(() => {
  if (editingVisibleRegion.value || visibleRegion.value.length < 3) return null;
  const frame = currentFrame.value;
  return frame.detections.map(target => detectionInReviewRegion(target.box, frame.width, frame.height, visibleRegion.value));
});
const frameInference = computed(() => currentFrame.value?.inference);
const inference = computed(() => frameInference.value || config.value);
const targetDetails = computed(() => currentFrame.value?.detections[selectedTarget.value]);
const canPlay = computed(() => mode.value === 'video' && duration.value > 0 && !previewUnavailable.value);
const displaySeconds = computed(() => currentFrame.value?.mediaSeconds ?? playhead.value);
const cameraInterrupted = computed(() => ['usb', 'rtsp'].includes(mode.value) && Boolean(latestFrame.value)
  && (pollFailed.value || job.value?.state === 'failed' || active.value && job.value?.frameUpdatedAt && Date.now() - Date.parse(job.value.frameUpdatedAt) > 10000));
const lastFrameTime = computed(() => latestFrame.value?.frameUpdatedAt
  ? new Date(latestFrame.value.frameUpdatedAt).toLocaleTimeString('zh-CN', { hour12: false }) : '时间未知');
const sourceName = computed(() => {
  if (recording.value) return recording.value.originalName || recording.value.filename;
  if (file.value) return file.value.name;
  if (mode.value === 'usb') return `本机摄像头 ${deviceIndex.value}`;
  if (mode.value === 'rtsp' && cameraId.value) {
    return cameras.value.find(camera => camera.id === cameraId.value)?.name || `摄像头 ${cameraId.value}`;
  }
  return '识别画面';
});
const statusText = computed(() => pollFailed.value ? '识别连接中断' : starting.value ? '正在启动' : ({ loading: '正在读取画面', running: '识别中', paused: '已暂停', stopping: '正在停止', finished: '识别完成', stopped: '已停止', failed: '识别失败' }[job.value?.state] || (hasInput.value ? '待开始' : '未选择素材')));
const placeholderTitle = computed(() => previewConverting.value ? '正在准备录像' : active.value || starting.value ? '正在准备识别' : hasInput.value ? '等待开始识别' : '尚未选择画面');
const placeholderHint = computed(() => {
  if (active.value || starting.value) return '首帧结果将在画面就绪后显示。';
  if (previewConverting.value) return '录像就绪后可预览。';
  if (previewUnavailable.value) return '当前文件无法直接预览，可尝试开始识别。';
  return hasInput.value ? (mode.value === 'video' ? '点击上方「开始录像识别」查看结果。' : '点击上方「开始识别」查看结果。') : '请在上方选择文件或摄像头。';
});
const resultNote = computed(() => pollFailed.value || job.value?.state === 'failed' ? '识别暂不可用，请查看上方提示。'
  : showSource.value && canPlay.value && job.value ? '该时刻未载入检测结果。可继续看原画，或打开已保留的检测帧。'
  : active.value || starting.value ? '正在等待第一帧结果。' : '开始识别后在这里核对模型结果。');
const frameDescription = computed(() => {
  const frame = currentFrame.value;
  if (!frame) return '';
  const index = frame.mode === 'image' && frame.mediaSeconds != null ? '选定画面' : `第 ${frame.frameIndex} 帧`;
  return frame.mediaSeconds == null ? index : index + ' · ' + timecode(frame.mediaSeconds);
});
const formatSize = size => size < 1024 * 1024 ? `${(size / 1024).toFixed(1)} KB` : `${(size / 1024 / 1024).toFixed(1)} MB`;
function detectionSummary(counts) {
  return Object.entries(counts).filter(([, count]) => count > 0)
    .map(([label, count]) => `${detectionLabel(label)}框 ${count}`).join(' · ');
}
function timecode(seconds) {
  const centiseconds = Math.max(0, Math.round(Number(seconds) * 100));
  const minutes = Math.floor(centiseconds / 6000);
  const remainder = (centiseconds % 6000) / 100;
  return `${String(minutes).padStart(2, '0')}:${remainder.toFixed(2).padStart(5, '0')}`;
}
const formatReviewTime = value => new Date(value).toLocaleString('zh-CN', { hour12: false });
const markerPosition = seconds => {
  const fraction = Math.max(0, Math.min(1, seconds / duration.value));
  return `calc(${fraction * 100}% - ${fraction * 16}px + 8px)`;
};
const markerTop = index => ((index + Number(eventSeconds.value != null)) % 2) * 23 + 'px';
function openFile() { fileInput.value?.click(); }
function clearResult(keepDetectionSamples = false) {
  resetReviewRegion();
  if (!keepDetectionSamples) detectionSamples.value = [];
  generation++;
  clearTimeout(timer);
  job.value = null;
  latestFrame.value = heldFrame.value = selectedTarget.value = null;
  view.value = 'source';
  zoom.value = 1;
  pollFailed.value = false;
  singleFrameSeconds = null;
  error.value = '';
}
function releasePreview() {
  previewGeneration++;
  previewAbort?.abort();
  previewAbort = null;
  previewVideo.value?.pause();
  if (previewUrl.value.startsWith('blob:')) URL.revokeObjectURL(previewUrl.value);
  else if (previewUrl.value.startsWith('http://127.0.0.1:5003/media/')) fetch(previewUrl.value, { method: 'DELETE' }).catch(() => {});
  previewUrl.value = '';
  previewUnavailable.value = previewConverting.value = previewConverted.value = false;
  duration.value = playhead.value = 0;
  videoPlaying.value = false;
  clipPlaybackEnd = null;
}
function loadVideoMetadata() {
  const seconds = previewVideo.value?.duration;
  duration.value = Number.isFinite(seconds) && seconds > 0 ? seconds : 0;
  if (initialSeek != null && canPlay.value) {
    if (initialSeek > duration.value) {
      linkedFeedback.value = '告警时刻超出实际录像时长，请手动核对。';
      eventSeconds.value = null;
    } else seekOriginal(initialSeek);
    initialSeek = null;
  }
}
function updatePlayhead() {
  if (!showSource.value || !previewVideo.value) return;
  const video = previewVideo.value;
  if (clipPlaybackEnd != null && video.currentTime >= clipPlaybackEnd) {
    video.currentTime = clipPlaybackEnd;
    clipPlaybackEnd = null;
    video.pause();
  }
  playhead.value = video.currentTime;
}
function onVideoPause() {
  videoPlaying.value = false;
  clipPlaybackEnd = null;
}
function seekOriginal(seconds) {
  if (!canPlay.value || !previewVideo.value || !Number.isFinite(Number(seconds))) return;
  view.value = 'source';
  heldFrame.value = selectedTarget.value = null;
  zoom.value = 1;
  clipPlaybackEnd = null;
  playhead.value = Math.min(duration.value, Math.max(0, Number(seconds)));
  previewVideo.value.currentTime = playhead.value;
}
async function togglePlayback() {
  const video = previewVideo.value;
  if (!video) return;
  if (!video.paused) { video.pause(); return; }
  if (!showSource.value) seekOriginal(displaySeconds.value);
  try { await video.play(); }
  catch (e) { if (e.name !== 'AbortError') error.value = '录像无法播放，请检查素材编码。'; }
}
function beginClip() {
  if (!canPlay.value || localLimitReached.value) return;
  previewVideo.value?.pause();
  heldFrame.value = currentFrame.value;
  const at = Math.max(0, Math.min(duration.value, currentFrame.value?.mediaSeconds ?? previewVideo.value.currentTime));
  selectedClip.value = null;
  clipMessage.value = '';
  draft.value = { id: crypto.randomUUID(), at, start: Math.max(0, at - 5), end: Math.min(duration.value, at + 5),
    frame: heldFrame.value?.mediaSeconds != null ? heldFrame.value : null, outcome: '', note: '' };
}
function cancelClip() {
  draft.value = null;
  clipMessage.value = '';
}
async function saveClip() {
  if (!draft.value || !canPlay.value || localLimitReached.value || savingClip.value) return;
  const { at, start, end, outcome } = draft.value;
  if (!Object.hasOwn(outcomes, outcome) || !Number.isFinite(start) || !Number.isFinite(end)
      || start < 0 || end > duration.value || start > at || end < at || start >= end) {
    clipMessage.value = '请填写包含代表时刻的有效区间和复核意见。';
    return;
  }
  let clip = { ...draft.value, source: sourceName.value };
  const recordingId = recording.value?.id;
  if (recordingId) {
    savingClip.value = true;
    try {
      const { data } = await saveRecordingReview(recordingId, { start, end, at, outcome, note: clip.note, requestId: clip.id });
      if (disposed || recording.value?.id !== recordingId || draft.value?.id !== clip.id) return;
      clip = { ...clip, ...data, frame: data.at === at ? clip.frame : null };
    } catch (e) {
      if (!disposed) clipMessage.value = e.message || '保存失败，请重试。';
      return;
    } finally { savingClip.value = false; }
  }
  const previousClips = clips.value.filter(item => item.id !== clip.id);
  const keepFrames = new Set(previousClips.filter(item => item.frame).slice(1 - clipLimit).map(item => item.id));
  clips.value = [...previousClips.map(item => item.frame && !keepFrames.has(item.id) ? { ...item, frame: null } : item), clip]
    .sort((a, b) => a.at - b.at);
  cancelClip();
  selectClip(clip);
}
function selectClip(clip) {
  selectedClip.value = clip;
  previewVideo.value?.pause();
  if (!clip.frame) { seekOriginal(clip.at); return; }
  heldFrame.value = clip.frame;
  selectedTarget.value = null;
  zoom.value = 1;
  view.value = 'annotated';
}
async function playClip(clip) {
  const video = previewVideo.value;
  if (!video || !canPlay.value) return;
  selectedClip.value = clip;
  const wasPlaying = !video.paused;
  seekOriginal(clip.start);
  clipPlaybackEnd = clip.end;
  if (!wasPlaying) await togglePlayback();
}
function removeClip(id) {
  clips.value = clips.value.filter(clip => clip.id !== id);
  if (selectedClip.value?.id === id) selectedClip.value = null;
}
function clearClips() {
  clips.value = [];
  selectedClip.value = null;
  cancelClip();
}
function focusTarget(index) {
  heldFrame.value = currentFrame.value;
  selectedTarget.value = selectedTarget.value === index ? null : index;
  view.value = 'annotated';
}
function resetReviewRegion() {
  regionFrame.value = null;
  regionPoints.value = [];
  editingRegion.value = false;
  regionMessage.value = '';
}
function beginReviewRegion() {
  if (!currentFrame.value || !localInput.value || active.value) return;
  resetReviewRegion();
  heldFrame.value = regionFrame.value = currentFrame.value;
  zoom.value = 1;
  editingRegion.value = true;
}
function addReviewPoint(point) {
  if (!editingVisibleRegion.value) return;
  if (regionPoints.value.length >= 20) {
    regionMessage.value = '最多添加 20 个顶点。';
    return;
  }
  regionPoints.value.push(point);
  regionMessage.value = '';
}
function undoReviewPoint() {
  regionPoints.value.pop();
  regionMessage.value = '';
}
function addReviewCoordinate() {
  if (![regionX.value, regionY.value].every(value => Number.isFinite(value) && value >= 0 && value <= 100)) return;
  addReviewPoint({ x: regionX.value / 100, y: regionY.value / 100 });
}
function finishReviewRegion() {
  if (!editingVisibleRegion.value) return;
  regionMessage.value = regionError(regionPoints.value);
  if (!regionMessage.value) editingRegion.value = false;
}
function toggleAnnotation() {
  heldFrame.value = currentFrame.value;
  view.value = view.value === 'annotated' ? 'raw' : 'annotated';
}
function followLatest() {
  previewVideo.value?.pause();
  heldFrame.value = selectedTarget.value = null;
  zoom.value = 1;
  view.value = 'annotated';
}
function rememberDetectionSample(frame) {
  if (frame.mode !== 'video' || !Number.isFinite(frame.mediaSeconds) || !frame.detections.length) return;
  const samples = detectionSamples.value;
  const last = samples[samples.length - 1];
  const videoLength = duration.value || (frame.sourceFps > 0 ? frame.totalFrames / frame.sourceFps : 0);
  const spacing = Math.max(2, videoLength / sampleLimit);
  if (samples.length >= sampleLimit || (last && frame.mediaSeconds - last.mediaSeconds < spacing)) return;
  samples.push(frame);
}
function showDetectionSample(frame) {
  previewVideo.value?.pause();
  heldFrame.value = frame;
  selectedTarget.value = null;
  zoom.value = 1;
  view.value = 'annotated';
}
function onPreviewError() {
  if (mode.value !== 'video' || !file.value || previewConverting.value) return;
  duration.value = 0;
  if (previewConverted.value) { previewUnavailable.value = true; return; }
  if (previewUrl.value.startsWith('blob:')) URL.revokeObjectURL(previewUrl.value);
  previewUrl.value = '';
  prepareVideoPreview(file.value);
}
async function prepareVideoPreview(selected) {
  const mine = previewGeneration;
  previewConverting.value = true;
  previewAbort = new AbortController();
  try {
    const response = await fetch('http://127.0.0.1:5003/transcode-link', {
      method: 'POST', body: selected, headers: { 'Content-Type': 'application/octet-stream' }, signal: previewAbort.signal
    });
    if (!response.ok) throw new Error('转码失败');
    const playable = await response.json();
    if (mine === previewGeneration && file.value === selected) { previewConverted.value = true; previewUrl.value = playable.url; }
  } catch (_) { if (mine === previewGeneration && file.value === selected) previewUnavailable.value = true; }
  finally { if (mine === previewGeneration) { previewAbort = null; previewConverting.value = false; } }
}

async function api(path, options = {}) {
  const abort = new AbortController(); requests.add(abort);
  const deadline = setTimeout(() => abort.abort(), path === '/jobs' ? 180000 : 10000);
  try {
    const response = await fetch(`${API}${path}`, { ...options, signal: abort.signal,
      headers: { ...options.headers, ...(options.method ? { 'X-Original-Token': token } : {}) } });
    const data = await response.json();
    if (!response.ok || !data.success) throw new Error(data.message || '识别请求失败');
    return data;
  } finally { clearTimeout(deadline); requests.delete(abort); }
}
async function connect() {
  if (connecting.value) return;
  connecting.value = true;
  error.value = '';
  try {
    const { token: sessionToken, ...settings } = await api('/config');
    if (disposed) return;
    token = sessionToken;
    config.value = settings;
    if (!profiles.value.some(item => item.id === profile.value)) profile.value = settings.defaultProfile || 'full640';
    connected.value = true;
  }
  catch (_) { if (!disposed) { connected.value = false; error.value = '无法连接识别服务。请重试，仍失败时联系运维。'; } }
  finally { connecting.value = false; }
}
function selectMode(value) {
  if (value === mode.value || active.value || starting.value) return;
  detachRecording();
  releasePreview(); clearResult(); clearClips(); mode.value = value; file.value = null;
  if (value === 'rtsp') loadCameras();
}
function selectFile(event) {
  detachRecording();
  releasePreview(); clearResult(); clearClips(); file.value = event.target.files[0] || null;
  if (!file.value) return;
  if (file.value.size > (mode.value === 'image' ? 16 : 512) * 1024 * 1024) {
    error.value = '文件超过允许大小，请缩小图片或截取较短视频。'; file.value = null; event.target.value = ''; return;
  }
  preparePreview(file.value);
}
function preparePreview(selected) {
  if (mode.value === 'video' && /\.(avi|mov|mkv|wmv|flv|mpg|mpeg)$/i.test(selected.name)) prepareVideoPreview(selected);
  else previewUrl.value = URL.createObjectURL(selected);
}
function detachRecording() {
  linkedAbort?.abort();
  linkedAbort = null;
  linkedLoading.value = false;
  recording.value = eventSeconds.value = initialSeek = null;
  linkedFeedback.value = reviewListError.value = '';
  if (route.query.recording || route.query.camera || route.query.at) router.replace({ path: '/originalRecognition' });
}
async function loadLinkedRecording() {
  const { recording: recordId, camera, at } = route.query;
  if (!recordId && !camera && !at) return;
  if (active.value || starting.value || savingClip.value) {
    linkedFeedback.value = '请先完成当前识别或保存，再打开系统录像。';
    return;
  }
  linkedAbort?.abort();
  const request = new AbortController();
  linkedAbort = request;
  releasePreview(); clearResult(); clearClips();
  mode.value = 'video';
  file.value = recording.value = eventSeconds.value = initialSeek = null;
  linkedFeedback.value = reviewListError.value = '';
  linkedLoading.value = true;
  try {
    let source, reviews;
    if (recordId) {
      if (!/^\d+$/.test(recordId)) throw new Error('录像编号无效。');
      const response = await getRecordingReviews(recordId, request.signal);
      ({ source, reviews } = response.data);
    } else {
      if (typeof camera !== 'string' || !/^\d+$/.test(camera) || typeof at !== 'string' || !Number.isFinite(Date.parse(at))) {
        throw new Error('告警缺少有效的摄像头编号或发生时间。');
      }
      const { data } = await getRecordingMatch(camera, at);
      if (!data?.success || !data.data?.filename) throw new Error(data?.msg || '没有覆盖该告警时刻的录像。');
      source = data.data;
    }
    if (request.signal.aborted || disposed) return;
    const { data: media } = await getRecordingFile(source.filename, request.signal);
    if (request.signal.aborted || disposed) return;
    recording.value = source;
    if (typeof at === 'string' && source.startedAt) {
      const offset = (Date.parse(at) - Date.parse(source.startedAt)) / 1000;
      if (Number.isFinite(offset) && offset >= 0) eventSeconds.value = initialSeek = offset;
    }
    linkedFeedback.value = typeof at === 'string'
      ? eventSeconds.value == null ? '已打开关联录像。录制开始时间缺失或不一致，请手动定位。' : '已匹配告警录像，定位 ' + timecode(eventSeconds.value) : '';
    file.value = new File([media], source.filename, { type: media.type });
    preparePreview(file.value);
    if (!reviews) {
      try { reviews = (await getRecordingReviews(source.id, request.signal)).data.reviews; }
      catch (_) { if (!request.signal.aborted) reviewListError.value = '交接记录暂不可用，仍可回看录像。'; }
    }
    if (!request.signal.aborted && !disposed) {
      clips.value = (reviews || []).map(clip => ({ ...clip, frame: null })).sort((a, b) => a.at - b.at);
    }
  } catch (e) {
    if (!request.signal.aborted && !disposed) linkedFeedback.value = e.message || '无法打开系统录像。';
  } finally {
    if (linkedAbort === request) linkedLoading.value = false;
  }
}
async function loadCameras() {
  loadingCameras.value = true; cameraError.value = '';
  try { const data = await api('/cameras'); if (!disposed) cameras.value = data.data; }
  catch (e) { if (!disposed) cameraError.value = e.message; }
  finally { loadingCameras.value = false; }
}
async function recognizePlayhead() {
  const video = previewVideo.value;
  if (!canPlay.value || active.value || starting.value || !connected.value || !video) return;
  if (!video.paused || video.seeking || video.readyState < 2) {
    error.value = '请暂停录像，并在当前画面加载完成后识别。';
    return;
  }
  const at = video.currentTime;
  const source = file.value;
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  if (!canvas.width || !canvas.height || canvas.width * canvas.height > 16_000_000) {
    error.value = '无法读取当前画面，或画面分辨率超出识别范围。';
    return;
  }
  try {
    const context = canvas.getContext('2d');
    if (!context) throw new Error('Video frame context unavailable');
    context.drawImage(video, 0, 0);
    const image = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.92));
    if (disposed || source !== file.value || active.value || starting.value) return;
    if (!image) throw new Error('Video frame encoding failed');
    await start(new File([image], '录像选定画面.jpg', { type: 'image/jpeg' }), at);
  } catch (_) {
    if (!disposed && source === file.value) error.value = '无法读取当前画面，请重试。';
  }
}
async function start(stillImage = null, at = null) {
  error.value = '';
  if (['image', 'video'].includes(mode.value) && !file.value) { error.value = '请先选择文件。'; return; }
  if (mode.value === 'rtsp' && !cameraId.value) { error.value = '请先选择网络摄像头。'; return; }
  if (file.value && file.value.size > (mode.value === 'image' ? 16 : 512) * 1024 * 1024) { error.value = '文件超过允许大小，请缩小图片或截取较短视频。'; return; }
  clearResult(Boolean(stillImage));
  singleFrameSeconds = at;
  starting.value = true;
  previewVideo.value?.pause();
  followLatest();
  const mine = generation;
  try {
    let options;
    if (['image', 'video'].includes(mode.value)) {
      const form = new FormData();
      form.append('mode', stillImage ? 'image' : mode.value);
      form.append('file', stillImage || file.value);
      if (profiles.value.length > 1) form.append('profile', profile.value);
      options = { method: 'POST', body: form };
    } else options = { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ mode: mode.value, deviceIndex: deviceIndex.value, cameraId: cameraId.value }) };
    const result = await api('/jobs', options);
    if (disposed || mine !== generation) return;
    job.value = result.data; poll(mine);
  } catch (e) { if (!disposed) { view.value = 'source'; error.value = e.message || '连接失败，请确认识别服务已启动。'; } }
  finally { starting.value = false; }
}
async function poll(mine) {
  if (disposed || mine !== generation || !job.value) return;
  const revision = ++pollRevision;
  try {
    const after = latestFrame.value?.frameIndex || 0;
    const { data } = await api(`/jobs/${job.value.id}/snapshot?after=${after}`);
    const { originalJpeg, ...status } = data;
    if (originalJpeg) {
      const image = new Image();
      image.src = `data:image/jpeg;base64,${originalJpeg}`;
      await image.decode();
      if (disposed || mine !== generation || revision !== pollRevision) return;
      latestFrame.value = { ...status, mediaSeconds: singleFrameSeconds ?? status.mediaSeconds, image: image.src };
      rememberDetectionSample(latestFrame.value);
    }
    if (disposed || mine !== generation || revision !== pollRevision) return;
    if (pollFailed.value) error.value = '';
    pollFailed.value = false;
    job.value = status;
    if (status.error) error.value = status.error;
    if (active.value) timer = setTimeout(() => poll(mine), 650);
  } catch (e) {
    if (disposed || mine !== generation || revision !== pollRevision) return;
    pollFailed.value = true;
    error.value = `暂时无法读取识别结果，正在重试。 ${e.message || ''}`;
    timer = setTimeout(() => poll(mine), 3000);
  }
}
async function control(action) {
  if (!job.value || controlling.value) return;
  controlling.value = true; error.value = '';
  try {
    await api(`/jobs/${job.value.id}/${action}`, { method: 'POST' });
    pollRevision++;
    clearTimeout(timer); timer = setTimeout(() => poll(generation), 100);
  } catch (e) { error.value = e.message; }
  finally { controlling.value = false; }
}
function leave() {
  if (job.value && active.value) fetch(`${API}/jobs/${job.value.id}/stop`, {
    method: 'POST', headers: { 'X-Original-Token': token }, keepalive: true }).catch(() => {});
}
onMounted(() => { connect(); window.addEventListener('pagehide', leave); });
watch(() => [route.query.recording, route.query.camera, route.query.at], loadLinkedRecording, { immediate: true });
onUnmounted(() => {
  leave(); releasePreview(); disposed = true; generation++; clearTimeout(timer);
  linkedAbort?.abort();
  requests.forEach(controller => controller.abort()); requests.clear();
  window.removeEventListener('pagehide', leave);
});
</script>

<style scoped>
.original-page { display: flex; flex-direction: column; padding-bottom: 14px; }
.recognition-columns { grid-template-columns: minmax(0, 1fr) clamp(278px, 25%, 430px); flex: 1; align-items: stretch; }
.viewer-card { display: flex; flex-direction: column; min-width: 0; align-self: stretch; }
.recognition-surface { flex: 1 0 clamp(200px, 33dvh, 440px); height: auto; }
.placeholder-action { margin-top: 12px; }
.stale-frame { inset: auto auto 10px 10px; color: #ffe0b7; }
.viewer-controls, .timeline-label { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 5px 12px; }
.viewer-controls { padding: 7px 12px; }
.viewer-controls .media-action, .skip-action { min-height: 32px; }
.frame-clock { font-variant-numeric: tabular-nums; white-space: nowrap; }
.review-timeline { border-top: 1px solid var(--media-line); padding: 7px 12px 8px; }
.timeline-label { font-size: 12px; color: var(--media-muted); }
.review-timeline input[type=range] { display: block; width: 100%; min-height: 24px; margin: 0; accent-color: var(--media-accent); }
.skip-action { background: transparent; border-color: transparent; padding-inline: 6px; }
.clip-markers { position: relative; height: 45px; }
.clip-marker { position: absolute; transform: translateX(-50%); display: grid; place-items: center; min-width: 25px; height: 22px; padding: 0 3px; border: 1px solid #457794; border-radius: 3px; background: #132e44; color: var(--media-text); font: inherit; font-size: 12px; cursor: pointer; }
.clip-marker:hover, .clip-marker:focus-visible, .clip-marker.is-selected { z-index: 1; background: #9dd7ed; color: #061522; }
.clip-marker:focus-visible { z-index: 2; }
.event-marker { color: #ffcf8f; border-color: #8e724b; }
.clip-content { display: grid; gap: 8px; padding: 0 13px 12px; }
.clip-content > .media-action { justify-self: start; }
.clip-form, .clip-selected { display: grid; gap: 7px; }
.clip-form label { display: grid; gap: 4px; font-size: 12px; color: var(--media-muted); }
.clip-form :is(input, select, textarea) { min-width: 0; width: 100%; min-height: 30px; border: 1px solid var(--media-line); border-radius: 4px; padding: 5px 7px; color: var(--media-text); background: var(--media-ground); font: inherit; }
.clip-form textarea { resize: vertical; }
.clip-range { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.clip-panel .media-action { min-height: 32px; }
.clip-selected { padding: 8px 0 2px; border-top: 1px solid var(--media-line); overflow-wrap: anywhere; }
.clip-list { list-style: none; margin: 0; padding: 0 3px; max-height: 128px; overflow: auto; }
.detection-sample-content { padding: 8px 13px; }
.detection-sample-content .media-help { margin: 0 0 5px; }
.recognition-source, .mode-buttons, .source-control { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; min-width: 0; }
.recognition-source > span { margin-right: 2px; }
.mode-buttons button[aria-pressed="true"] { background: #154669; border-color: #79c6ed; color: #fff; font-weight: 650; }
.source-control { flex: 1 1 220px; padding-inline-start: 13px; border-left: 1px solid var(--media-line); }
.source-control .el-select { width: min(220px, 100%); }
.source-control .media-source-title { max-width: clamp(95px, 17vw, 270px); }
.recognition-controls { margin-inline-start: auto; }
.recognition-error { flex-basis: 100%; }
.linked-feedback { flex-basis: 100%; font-size: 13px; color: var(--media-accent); }
.linked-feedback[data-tone=attention] { color: #ffcc9a; }
.file-input { position: absolute; width: 1px; height: 1px; clip-path: inset(50%); overflow: hidden; }
.recognition-results { padding-bottom: 12px; min-height: 110px; }
.recognition-counts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); padding: 3px 13px 12px; gap: 10px; }
.recognition-counts > div { border-left: 2px solid #32729c; padding: 6px 10px; font-size: 13px; color: var(--media-muted); }
.recognition-counts strong { margin-left: 5px; color: var(--media-text); font-size: 23px; font-variant-numeric: tabular-nums; }
.result-note { padding: 0 13px; }
.recognition-list { max-height: clamp(90px, 16dvh, 196px); overflow: auto; padding: 3px 13px; }
.target-row { display: grid; width: 100%; grid-template-columns: auto 1fr auto; align-items: center; gap: 9px; min-height: 34px; padding: 5px 7px; border: 0; border-bottom: 1px solid var(--media-line); background: none; color: var(--media-text); text-align: left; font: inherit; font-size: 13px; cursor: pointer; }
.target-row:hover, .target-row[aria-pressed=true] { background: #174663; }
.target-dot { width: 8px; height: 8px; border: 1px solid #76dcff; }
.target-dot.car { border-color: #f5cc8a; }
.target-details { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 6px 10px; margin: 8px 13px 0; }
.model-details { padding: 0 13px 11px; }
.model-details dl { font-size: 12px; }
.model-details dl div { display: flex; justify-content: space-between; gap: 8px; margin: 7px 0; }
.model-details dd { margin: 0; text-align: right; }
.inference-profile { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin: 10px 0; font-size: 13px; }
.inference-profile select { min-height: 36px; color: inherit; background: #102a42; border: 1px solid #49647d; border-radius: 4px; padding: 0 7px; }
.review-region-controls { padding: 0 13px 11px; display: grid; gap: 8px; }
.review-region-controls p { margin: 0; }
.review-region-coordinates { display: flex; flex-wrap: wrap; align-items: end; gap: 8px; }
.review-region-coordinates label { display: grid; gap: 3px; font-size: 12px; }
.review-region-coordinates input { width: 70px; min-height: 34px; color: inherit; background: #102a42; border: 1px solid #49647d; border-radius: 4px; padding: 0 6px; }
@media (max-width: 1050px) { .source-limit { display: none; } }
@media (min-width: 821px) and (min-height: 680px) {
  .recognition-columns { grid-template-rows: minmax(0, 1fr); }
  .recognition-columns > .media-side { overflow: auto; padding-inline-end: 2px; scrollbar-color: #46718c transparent; }
}
@media (max-width: 820px) {
  .original-page { display: block; }
  .recognition-columns { grid-template-columns: minmax(0, 1fr); }
  .recognition-surface { min-height: clamp(185px, 40dvh, 410px); }
  .source-control { border-left: 0; padding-inline-start: 0; }
  .recognition-controls { margin-inline-start: 0; }
}
</style>
