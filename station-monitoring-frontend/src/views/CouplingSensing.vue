<template>
  <main class="media-workspace coupling-workspace" aria-label="连挂作业复核">
    <header class="media-heading">
      <div><h1>连挂作业记录</h1><p>按作业素材回看车钩画面、定位关键时刻并记录人工复核意见。</p></div>
      <button type="button" class="media-action" @click="openSavedReviews">已保存记录</button>
    </header>

    <section class="coupling-session" aria-label="本次作业素材概况">
      <div class="session-source">
        <span class="session-eyebrow">本次素材</span>
        <strong :title="file?.name || ''">{{ file?.name || '尚未选择录像或图片' }}</strong>
        <small>{{ file ? (isVideo ? '本地录像' : '本地图片') : '打开素材后可开始回看与复核' }} · {{ file ? '未关联现场作业与设备' : '无作业关联' }}</small>
      </div>
      <div class="session-readout"><span>已检查画面</span><strong>{{ records.length }}</strong><small>{{ records.length ? '本次检测记录' : '尚无检测记录' }}</small></div>
      <div class="session-readout"><span>人工复核</span><strong>{{ reviewedCount }}</strong><small>{{ reviewedCount ? '已判断的检测帧' : '尚无帧判断' }}</small></div>
      <div class="session-mobile"><span>现场手机测距</span><strong>未关联记录</strong><small>本页暂未接收 APK 的测量结果</small></div>
    </section>

    <section class="media-bar" aria-label="作业录像操作">
      <span class="coupling-step">01 打开素材</span>
      <input id="coupling-file" ref="sourceInput" class="source-input" type="file" tabindex="-1"
        accept=".mp4,.avi,.mov,.mkv,.webm,.ogg,image/jpeg,image/png,image/webp" @change="selectFile" />
      <button type="button" class="media-action" :class="{ 'media-action--primary': !file }" @click="sourceInput?.click()">
        {{ file ? '更换素材' : '打开作业录像或图片' }}
      </button>
      <button v-if="file" type="button" class="media-action" @click="clearFile">清除</button>
      <span v-if="file" class="coupling-step">02 查找画面</span>
      <button v-if="file" type="button" class="media-action" :class="{ 'media-action--primary': !hasPrediction && !scanning && !reviewInProgress }"
        :disabled="!canInfer" @click="predictCurrentFrame">{{ predicting ? '识别中…' : '识别当前画面' }}</button>
      <label v-if="isVideo" class="coupling-scan-option">抽帧间隔
        <select v-model.number="scanInterval" :disabled="scanning"><option :value="1">1 秒</option><option :value="2">2 秒</option><option :value="5">5 秒</option></select>
      </label>
      <button v-if="isVideo && !scanning" type="button" class="media-action" :disabled="!canInfer" @click="scanVideo">扫描录像</button>
      <button v-if="scanning" type="button" class="media-action" @click="stopScan">停止扫描</button>
      <button v-if="analyzedFrame" type="button" class="media-action" @click="analyzedFrame = ''">返回原始画面</button>
      <button v-if="isVideo && duration" type="button" class="media-action" :disabled="seeking || scanning" @click="captureFrame">保存当前帧</button>
      <span v-if="converting || scanning || scanProgress.done || !serviceReady" class="media-status" role="status">
        {{ converting ? '正在准备录像…' : scanning ? `扫描中 ${scanProgress.done}/${scanProgress.total} 帧` : scanProgress.done ? `已检查 ${scanProgress.done}/${scanProgress.total} 帧` : '识别服务暂不可用' }}
      </span>
      <p v-if="inferenceError" class="media-feedback coupling-error" role="alert">{{ inferenceError }}</p>
    </section>

    <div class="media-columns">
      <div class="media-main">
        <section class="media-panel media-viewer" aria-label="作业画面">
          <header class="media-panel-head">
            <h2 class="media-source-title" :title="file?.name">作业画面 · {{ file?.name || '未选择素材' }}</h2>
            <span class="media-status">{{ file ? (isVideo ? '历史录像' : '现场图片') : '未打开素材' }}</span>
          </header>
          <div class="media-surface" :class="{ 'is-empty': !file }">
            <video v-if="url && isVideo" v-show="!analyzedFrame" ref="video" :src="url" crossorigin="anonymous" controls playsinline preload="metadata"
              @timeupdate="updateTime" @loadedmetadata="onVideoLoaded" @seeking="seeking = true" @seeked="onVideoSeeked" @error="onVideoError" />
            <img v-if="analyzedFrame" :src="analyzedFrame" alt="标有模型检测框的画面" />
            <img v-else-if="url && !isVideo" :src="url" alt="所选现场图片" />
            <div v-if="!url" class="media-placeholder">
              <strong>{{ converting ? '正在准备录像…' : file ? '画面暂不可用' : '尚未打开作业素材' }}</strong>
              <p class="media-help">{{ converting ? '录像就绪后可播放。' : file ? '请按上方提示处理后重试。' : '打开录像后，可定位检测画面并记录复核结论。' }}</p>
            </div>
            <span v-if="url" class="media-stamp">{{ analyzedFrame ? '检测标注 · 需人工复核' : '原始画面' }}</span>
          </div>

          <section v-if="isVideo && duration" class="coupling-timeline" aria-label="作业时间轴">
            <header class="media-panel-head"><h2>作业时间轴</h2><span class="media-status">{{ timeText }}</span></header>
            <div class="timeline-control">
              <input aria-label="定位视频时间" type="range" min="0" :max="duration" step="any"
                :value="seconds" :disabled="converting || predicting" @change="seekVideoTime(Number($event.target.value))" />
              <div v-if="records.length" class="time-track" aria-label="检测标记">
                <button v-for="record in records" :key="record.id" type="button" class="time-marker"
                  :class="{ selected: activeRecord?.id === record.id }" :style="{ left: markerPosition(record) + '%' }"
                  :title="`${record.time} · ${record.detections.length} 个目标 · ${reviewLabel(record.review)}`"
                  :aria-label="`查看 ${record.time} 的检测记录`" @click="selectRecord(record)"></button>
              </div>
            </div>
          </section>
        </section>

        <section v-if="records.length" class="media-panel coupling-records" aria-label="本次检测记录">
          <header class="media-panel-head">
            <div><h2>关键画面与检测记录</h2><p class="media-help">点击记录定位原录像。扫描仅检查抽取的画面，未扫描的时刻不代表没有目标。</p></div>
            <div class="media-actions"><span class="media-status">{{ records.length }} 条</span><button type="button" class="media-action" @click="exportRecords">导出记录</button></div>
          </header>
          <div class="record-list" tabindex="0" role="region" aria-label="检测记录列表">
            <div v-for="record in records" :key="record.id" class="record-row" :class="{ selected: selectedRecordId === record.id }">
              <button type="button" class="record-open" :aria-pressed="selectedRecordId === record.id" @click="selectRecord(record)">
                <img :src="record.frame" alt="" />
                <span><strong>{{ record.time }} · {{ record.detections.length }} 个检测目标</strong><small>{{ record.detections.length ? record.detections.map(item => `${targetLabel(item.label)} ${(item.confidence * 100).toFixed(1)}%`).join('、') : '此帧未检出目标' }}</small></span>
              </button>
              <div class="record-review"><label :for="`review-${record.id}`">帧判断</label>
                <select :id="`review-${record.id}`" v-model="record.review"><option value="pending">待复核</option><option value="confirmed">目标确认</option><option value="false_positive">预测有误</option><option value="insufficient">证据不足</option></select>
              </div>
            </div>
          </div>
        </section>
      </div>

      <aside class="media-side" aria-label="帧证据与复核">
        <div class="coupling-side-heading"><span class="coupling-step">03 核对证据</span><span>人工确认作业情况</span></div>
        <section v-if="file" class="media-panel current-evidence" aria-label="当前帧证据">
          <header class="media-panel-head"><h2>当前帧证据</h2><span class="media-status" role="status">{{ evidenceStatus }}</span></header>
          <div class="current-evidence-content">
            <p v-if="hasPrediction && !detections.length" class="media-help">当前帧未检出货车或车钩。</p>
            <p v-else-if="!hasPrediction && serviceReady && !scanning && !predicting && !converting" class="media-help">可先识别当前画面，也可直接复核原画面。</p>
            <ul v-if="detections.length" class="detected-targets" aria-label="当前帧检测目标">
              <li v-for="(item, index) in detections" :key="index"><span>{{ targetLabel(item.label) }}</span><span>置信度 {{ (item.confidence * 100).toFixed(1) }}%</span></li>
            </ul>
            <p class="media-help coupling-boundary">连挂状态由现场作业人员确认。</p>
          </div>
        </section>
        <CouplerReviewArchive :key="sourceRevision" ref="reviewArchive" class="media-panel" :source="file" :record="activeRecord"
          :owner="owner" :reviewer="reviewer" :can-capture="canCaptureReview"
          :capture="captureReviewEvidence" @seek="seekVideoTime" @draft-change="reviewInProgress = $event" />

        <details v-if="file && isVideo && duration" class="media-panel media-disclosure">
          <summary>录音与加速度对齐</summary>
          <CouplerSynchronization :key="sourceRevision" ref="synchronization"
            :video-duration="duration" :video-seconds="seconds" :can-seek="!converting && !predicting"
            hide-seek @seek="seekVideoTime" />
        </details>
        <details v-if="file" class="media-panel media-disclosure">
          <summary>网页参考面距离估算（需标定）</summary>
          <CouplerRanging ref="ranging" :api="API" :ready="rangingReady" :source="file"
            :can-load="canCaptureReview" :load-frame="loadRangingFrame" embedded />
        </details>
        <details v-if="captures.length" class="media-panel media-disclosure">
          <summary>已保存当前帧（{{ captures.length }}）</summary>
          <section aria-label="已保存截图">
            <div v-for="item in captures" :key="item.id" class="capture">
              <img :src="item.url" alt="录像原始截图" /><div><strong>{{ item.time }}</strong><a :href="item.url" :download="item.filename">下载图片</a></div>
            </div>
          </section>
        </details>
        <details v-if="showFieldTrial" class="media-panel media-disclosure">
          <summary>试用与技术信息</summary>
          <section class="trial-details">
            <label v-if="file" class="coupling-scan-option">识别输入配置
              <select v-model="inferenceProfile" :disabled="predicting || scanning"><option value="web640">网页 640</option><option value="apk320" :disabled="!apkProfileReady">安卓输入对照 320</option></select>
            </label>
            <template v-if="activeRecord">
              <p>{{ activeRecord.model }} · {{ activeRecord.profile }} · {{ processingMs }} ms</p>
              <p v-for="(item, index) in detections" :key="index">{{ item.label }} · {{ item.box.join(', ') }} px</p>
            </template>
            <CouplerTrial :key="sourceRevision" :source="file" :reviewer="reviewer" />
          </section>
        </details>
      </aside>
    </div>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useStore } from 'vuex';
import '@/assets/style/media-workspace.css';
import CouplerRanging from './CouplerRanging.vue';
import CouplerSynchronization from './CouplerSynchronization.vue';
import CouplerReviewArchive from './CouplerReviewArchive.vue';
import CouplerTrial from './CouplerTrial.vue';
import { sourceIdentity } from '../utils/couplerSync';
const file = ref(null), url = ref(''), video = ref(null), seconds = ref(0), duration = ref(0), captures = ref([]);
const serviceReady = ref(false), predicting = ref(false), converting = ref(false), converted = ref(false), inferenceError = ref(''), analyzedFrame = ref('');
const detections = ref([]), hasPrediction = ref(false), processingMs = ref(null), records = ref([]), selectedRecordId = ref(null);
const inferenceProfile = ref('web640');
const apkProfileReady = ref(false);
const rangingReady = ref(false);
const synchronization = ref(null), ranging = ref(null), sourceRevision = ref(0);
const reviewArchive = ref(null), sourceInput = ref(null), seeking = ref(false);
const reviewInProgress = ref(false);
const store = useStore();
const owner = computed(() => {
  const id = store.state.user?.userInfo?.id;
  return id == null ? '' : String(id);
});
const reviewer = computed(() => store.state.user?.userInfo?.username || owner.value);
const scanning = ref(false), scanInterval = ref(2), scanProgress = ref({ done: 0, total: 0 });
let scanGeneration = 0, scanAbort = null;
const API = 'http://127.0.0.1:5003';
const showFieldTrial = process.env.VUE_APP_FIELD_TRIAL_ENABLED === 'true';
function targetLabel(label) {
  if (['coupler_far', 'couplers', 'coupler_near'].includes(label)) return '车钩';
  return label === 'freight car' ? '货车' : label;
}
const isVideo = computed(() => !!file.value && (file.value.type.startsWith('video/') || /\.(avi|mov|mkv|mp4|webm|ogg)$/i.test(file.value.name)));
const fmt = value => `${String(Math.floor(value / 60)).padStart(2, '0')}:${String(Math.floor(value % 60)).padStart(2, '0')}`;
const timeText = computed(() => isVideo.value && duration.value ? `${fmt(seconds.value)} / ${fmt(duration.value)}` : '无时间数据');
const activeRecord = computed(() => records.value.find(item => item.id === selectedRecordId.value) || null);
const reviewedCount = computed(() => records.value.filter(item => item.review !== 'pending').length);
const canInfer = computed(() => Boolean(file.value && url.value) && serviceReady.value && !predicting.value
  && !scanning.value && !converting.value && !seeking.value && (!isVideo.value || Boolean(duration.value)));
const canCaptureReview = computed(() => Boolean(file.value && url.value) && !converting.value
  && !scanning.value && !predicting.value && !seeking.value && (!isVideo.value || Boolean(duration.value)));
const evidenceStatus = computed(() => {
  if (converting.value) return '录像准备中';
  if (seeking.value && !scanning.value) return '正在定位';
  if (scanning.value) return '扫描中';
  if (predicting.value) return '识别中';
  if (hasPrediction.value) return reviewLabel(activeRecord.value?.review);
  return serviceReady.value ? '尚未识别' : '识别暂不可用';
});
function openSavedReviews() {
  reviewArchive.value?.openSavedRecords();
}
function onVideoSeeked() {
  seeking.value = false;
  updateTime();
}

function seekVideoTime(target) {
  const element = video.value;
  if (!element || predicting.value || !Number.isFinite(target) || target < 0 || target > duration.value) return;
  stopScan();
  element.pause();
  resetPrediction();
  element.currentTime = target;
  seconds.value = target;
}

async function captureReviewEvidence() {
  const source = file.value;
  const record = activeRecord.value;
  const snapshot = await loadRangingFrame();
  const time = snapshot.videoSeconds ?? null;
  if (!source || file.value !== source || (isVideo.value && !Number.isFinite(time))) {
    throw new Error('作业素材已切换，请重新提取证据。');
  }
  let originalFrame = snapshot.src;
  if (originalFrame.startsWith('blob:')) {
    originalFrame = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error('无法读取原始图片。'));
      reader.readAsDataURL(source);
    });
  }
  if (file.value !== source) throw new Error('作业素材已切换，请重新提取证据。');
  const alignedRecord = record && (time == null || Math.abs(time - record.seconds) < .001);
  return {
    source: sourceIdentity(source), frameRef: snapshot.frameRef, videoSeconds: time,
    originalFrame,
    prediction: alignedRecord ? {
      id: record.id, model: record.model, profile: record.profile,
      detections: record.detections, annotatedFrame: record.frame, frameReview: record.review,
    } : null,
    synchronized: time == null ? null : synchronization.value?.snapshotAt(time) || null,
    ranging: ranging.value?.snapshotFor(snapshot.frameRef) || null,
  };
}

async function loadRangingFrame() {
  const source = file.value;
  if (!source || !url.value) throw new Error('请先打开现场图片或视频');
  const fileRef = `${source.name.slice(0, 110)} · ${source.size} B · ${source.lastModified}`;
  if (!isVideo.value) return { src: url.value, frameRef: fileRef + ' · 原始图片' };

  const element = video.value;
  if (!element || element.readyState < 2 || !element.videoWidth) throw new Error('请等待原始视频帧解码后再取帧');
  element.pause();
  const target = records.value.find(item => item.id === selectedRecordId.value)?.seconds ?? element.currentTime;
  await seekForScan(element, target);
  if (file.value !== source) throw new Error('作业素材已切换');
  const canvas = document.createElement('canvas');
  canvas.width = element.videoWidth;
  canvas.height = element.videoHeight;
  canvas.getContext('2d').drawImage(element, 0, 0);
  return {
    src: canvas.toDataURL('image/jpeg', .95), videoSeconds: element.currentTime,
    frameRef: `${fileRef} · ${element.currentTime.toFixed(3)} s`,
  };
}
function stopScan() { scanGeneration += 1; scanAbort?.abort(); scanAbort = null; scanning.value = false; }
function clearFile() {
  sourceRevision.value += 1;
  stopScan();
  if (url.value.startsWith('blob:')) URL.revokeObjectURL(url.value);
  else if (url.value.startsWith(`${API}/media/`)) fetch(url.value, { method: 'DELETE' }).catch(() => {});
  captures.value.forEach(item => URL.revokeObjectURL(item.url));
  captures.value = [];
  records.value = [];
  file.value = null;
  url.value = '';
  seconds.value = 0;
  duration.value = 0;
  seeking.value = false;
  reviewInProgress.value = false;
  converting.value = false;
  converted.value = false;
  scanProgress.value = { done: 0, total: 0 };
  resetPrediction();
}
function resetPrediction() { analyzedFrame.value = ''; detections.value = []; hasPrediction.value = false; processingMs.value = null; selectedRecordId.value = null; inferenceError.value = ''; }
function selectFile(event) {
  clearFile();
  const selected = event.target.files?.[0];
  if (!selected) return;
  if (!(selected.type.startsWith('video/') || selected.type.startsWith('image/') || /\.(avi|mov|mkv|mp4|webm|ogg)$/i.test(selected.name))) return;
  file.value = selected;
  event.target.value = '';
  // Browsers may leave AVI at 0:00 without firing a media error. Convert known unsupported containers immediately.
  if (/\.(avi|mkv|mov)$/i.test(selected.name)) convertVideo(selected);
  else url.value = URL.createObjectURL(selected);
}
function updateTime() {
  seconds.value = video.value?.currentTime || 0;
  duration.value = Number.isFinite(video.value?.duration) ? video.value.duration : 0;
  const selected = records.value.find(item => item.id === selectedRecordId.value);
  if (!selected || Math.abs(seconds.value - selected.seconds) > .35) resetPrediction();
}
function markerPosition(record) { return duration.value > 0 ? Math.max(0, Math.min(100, record.seconds / duration.value * 100)) : 0; }
function reviewLabel(value) { return { pending: '待复核', confirmed: '目标确认', false_positive: '预测有误', insufficient: '证据不足' }[value] || '待复核'; }
function exportRecords() {
  if (!file.value || !records.value.length) return;
  const payload = { format: 'rail-vision-coupling-review-v1', exportedAt: new Date().toISOString(),
    source: { name: file.value.name, size: file.value.size, lastModified: file.value.lastModified,
      note: '文件名与大小仅作来源描述，未校验原文件哈希' },
    records: records.value.map(({ id, seconds: timeSeconds, time, detections: objects, processingMs: elapsed,
      frame, profile, review }) => ({ id, timeSeconds, time, detections: objects, processingMs: elapsed,
      profile, review, reviewLabel: reviewLabel(review), annotatedFrame: frame })) };
  const downloadUrl = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }));
  const link = document.createElement('a'); link.href = downloadUrl; link.download = '作业感知复核记录.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);
}
function selectRecord(record) {
  if (predicting.value) return;
  if (scanning.value) stopScan();
  if (isVideo.value && video.value) { video.value.pause(); video.value.currentTime = record.seconds; seconds.value = record.seconds; }
  selectedRecordId.value = record.id; detections.value = record.detections; processingMs.value = record.processingMs;
  analyzedFrame.value = record.frame; hasPrediction.value = true; inferenceError.value = '';
}
function onVideoLoaded() { updateTime(); inferenceError.value = ''; }
async function onVideoError() {
  if (!file.value || converting.value) return;
  if (converted.value) { inferenceError.value = '转换完成后仍无法播放，请换用较短的 MP4/H.264 文件。'; return; }
  await convertVideo(file.value);
}
async function convertVideo(selectedFile) {
  if (!serviceReady.value) { inferenceError.value = '此录像需要转换，转换服务暂不可用。请联系运维或选择可直接播放的 MP4。'; return; }
  converting.value = true;
  inferenceError.value = '';
  try {
    const response = await fetch(`${API}/transcode-link`, { method: 'POST', body: selectedFile, headers: { 'Content-Type': 'application/octet-stream' } });
    if (!response.ok) { const data = await response.json(); throw new Error(data.error || '视频转换失败'); }
    const media = await response.json();
    if (file.value !== selectedFile) return;
    if (url.value.startsWith('blob:')) URL.revokeObjectURL(url.value);
    converted.value = true;
    url.value = media.url;
    await new Promise(resolve => setTimeout(resolve, 0));
    video.value?.load();
  } catch (error) { if (file.value === selectedFile) inferenceError.value = error instanceof TypeError ? '连接视频转换服务失败，请重试或联系运维。' : error.message || '视频转换失败'; }
  finally { if (file.value === selectedFile) converting.value = false; }
}
async function predictCurrentFrame() {
  if (!canInfer.value) return;
  predicting.value = true; inferenceError.value = '';
  const sourceFile = file.value;
  let frameSeconds = 0;
  try {
    let blob = file.value;
    if (isVideo.value) {
      const element = video.value;
      if (!element || element.readyState < 2) throw new Error('请先播放到需要识别的画面');
      element.pause();
      frameSeconds = element.currentTime;
      const canvas = document.createElement('canvas'); canvas.width = element.videoWidth; canvas.height = element.videoHeight;
      canvas.getContext('2d').drawImage(element, 0, 0);
      blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', .9));
    }
    if (!blob) throw new Error('无法读取当前画面');
    const result = await requestPrediction(blob, inferenceProfile.value);
    if (file.value !== sourceFile || isVideo.value && Math.abs((video.value?.currentTime ?? -1) - frameSeconds) > .04) return;
    storePrediction(result, frameSeconds);
  } catch (error) { inferenceError.value = error.message || '无法连接本机识别服务'; }
  finally { predicting.value = false; }
}
async function requestPrediction(blob, profile, signal) {
  const endpoint = profile === 'apk320' ? '/predict?profile=apk320' : '/predict';
  const response = await fetch(`${API}${endpoint}`, { method: 'POST', body: blob,
    headers: { 'Content-Type': blob.type || 'image/jpeg' }, signal });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || '推理失败');
  return result;
}
function storePrediction(result, frameSeconds) {
  const record = { id: crypto.randomUUID(), seconds: frameSeconds, time: isVideo.value ? fmt(frameSeconds) : '图片',
    detections: result.detections, processingMs: result.processingMs, frame: result.frame,
    profile: result.profile || 'web640', model: 'best12_20', review: 'pending' };
  records.value.unshift(record); records.value = records.value.slice(0, 60);
  selectedRecordId.value = record.id; detections.value = result.detections;
  processingMs.value = result.processingMs; analyzedFrame.value = result.frame; hasPrediction.value = true;
}
function seekForScan(element, target) {
  return new Promise((resolve, reject) => {
    if (!element.seeking && Math.abs(element.currentTime - target) < .04 && element.readyState >= 2) { resolve(); return; }
    let timer;
    const finish = error => { clearTimeout(timer); element.removeEventListener('seeked', onSeeked);
      element.removeEventListener('loadeddata', onLoadedData); element.removeEventListener('error', onError);
      error ? reject(error) : resolve(); };
    const onSeeked = () => { if (element.readyState >= 2) finish(); };
    const onLoadedData = () => { if (Math.abs(element.currentTime - target) < .04 && element.readyState >= 2) finish(); };
    const onError = () => finish(new Error('视频定位失败'));
    timer = setTimeout(() => finish(new Error('视频定位超时')), 8000);
    element.addEventListener('seeked', onSeeked, { once: true });
    element.addEventListener('loadeddata', onLoadedData);
    element.addEventListener('error', onError, { once: true });
    try { if (Math.abs(element.currentTime - target) >= .04) element.currentTime = target; }
    catch { finish(new Error('无法跳转到指定视频时刻')); }
  });
}
async function scanVideo() {
  const element = video.value, sourceFile = file.value;
  if (!element || !sourceFile || !duration.value || !canInfer.value) return;
  element.pause(); scanning.value = true; inferenceError.value = '';
  const generation = ++scanGeneration, profile = inferenceProfile.value;
  const sampleTimes = [], step = Math.max(scanInterval.value, duration.value / 60);
  for (let t = 0; t < duration.value && sampleTimes.length < 60; t += step) sampleTimes.push(t);
  scanProgress.value = { done: 0, total: sampleTimes.length };
  try {
    for (const target of sampleTimes) {
      if (generation !== scanGeneration || sourceFile !== file.value) break;
      await seekForScan(element, target);
      if (generation !== scanGeneration || sourceFile !== file.value) break;
      const canvas = document.createElement('canvas'); canvas.width = element.videoWidth; canvas.height = element.videoHeight;
      canvas.getContext('2d').drawImage(element, 0, 0);
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', .85));
      if (!blob) throw new Error('无法读取视频帧');
      scanAbort = new AbortController();
      const result = await requestPrediction(blob, profile, scanAbort.signal);
      if (generation !== scanGeneration || sourceFile !== file.value) break;
      storePrediction(result, element.currentTime);
      scanProgress.value = { done: scanProgress.value.done + 1, total: sampleTimes.length };
    }
  } catch (error) { if (generation === scanGeneration && error.name !== 'AbortError') inferenceError.value = error.message || '扫描失败'; }
  finally { if (generation === scanGeneration) { scanAbort = null; scanning.value = false; } }
}
onMounted(async () => {
  try {
    const response = await fetch(`${API}/health`);
    const health = await response.json();
    serviceReady.value = response.ok && health.ready;
    apkProfileReady.value = health.profiles?.includes('apk320') || false;
    rangingReady.value = response.ok && health.ranging === 'rail-coupler-ranging-v1';
  } catch {
    serviceReady.value = false;
    apkProfileReady.value = false;
    rangingReady.value = false;
  }
});
function captureFrame() {
  const element = video.value, source = file.value;
  if (!element || element.readyState < 2 || !element.videoWidth) return;
  const canvas = document.createElement('canvas'); canvas.width = element.videoWidth; canvas.height = element.videoHeight;
  element.pause();
  const capturedAt = element.currentTime;
  canvas.getContext('2d').drawImage(element, 0, 0);
  canvas.toBlob(blob => {
    if (!blob || file.value !== source) return;
    const time = fmt(capturedAt);
    captures.value.unshift({ id: crypto.randomUUID(), url: URL.createObjectURL(blob), time,
      filename: `source-frame-${Math.floor(capturedAt * 1000)}ms.png` });
  }, 'image/png');
}
onBeforeUnmount(clearFile);
</script>

<style scoped>
.coupling-session { display: grid; grid-template-columns: minmax(0, 2fr) repeat(3, minmax(125px, 1fr)); gap: 1px; margin: 0 0 12px; border: 1px solid var(--media-line); background: var(--media-line); border-radius: 5px; overflow: hidden; }
.coupling-session > div { display: grid; align-content: center; gap: 3px; min-width: 0; min-height: 73px; padding: 10px 14px; background: var(--media-panel); }
.coupling-session span, .coupling-session small { color: var(--media-muted); font-size: 12px; line-height: 1.4; }
.coupling-session strong { font-size: 15px; line-height: 1.3; font-weight: 650; }
.session-source strong { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.session-readout strong { font-variant-numeric: tabular-nums; font-size: 19px; }
.session-mobile strong { font-size: 13px; color: var(--media-muted); }
.coupling-step { flex: none; color: var(--media-accent); font-size: 12px; font-weight: 650; letter-spacing: .02em; }
.coupling-side-heading { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 3px 2px 0; color: var(--media-muted); font-size: 12px; }
.source-input { position: absolute; width: 1px; height: 1px; clip-path: inset(50%); overflow: hidden; }
.coupling-error { flex-basis: 100%; }
.coupling-scan-option { display: inline-flex; align-items: center; gap: 7px; color: var(--media-muted); font-size: 13px; }
.coupling-scan-option select, .record-review select { min-height: 36px; border: 1px solid var(--media-line); border-radius: 4px; background: #123450; color: var(--media-text); padding: 4px 7px; font: inherit; }
.coupling-timeline { padding-bottom: 9px; }
.coupling-timeline .media-panel-head { min-height: 35px; padding-block: 6px 3px; }
.timeline-control { padding: 0 14px; }
.timeline-control input { display: block; width: 100%; margin: 0; min-height: 24px; accent-color: #9fddfc; }
.time-track { position: relative; height: 2px; margin: 5px 8px 12px; background: var(--media-line); }
.time-marker { position: absolute; top: 50%; transform: translate(-50%, -50%); width: 14px; height: 14px; border-radius: 50%; border: 2px solid var(--media-panel); background: #8ecdea; cursor: pointer; padding: 0; }
.time-marker.selected { background: #ffd09a; z-index: 1; }
.record-list, .detected-targets { max-height: clamp(112px, 17dvh, 220px); overflow: auto; }
.record-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 5px 12px; border-top: 1px solid var(--media-line); }
.record-row.selected { background: #153a55; }
.record-open { display: flex; align-items: center; gap: 10px; min-width: 0; width: 100%; text-align: left; border: 0; background: transparent; color: var(--media-text); cursor: pointer; padding: 3px 0; font: inherit; font-size: 13px; }
.record-open img { width: 72px; height: 40px; object-fit: contain; background: #061522; flex: none; }
.record-open span { min-width: 0; display: grid; gap: 3px; }
.record-open strong, .record-open small { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.record-open small { color: var(--media-muted); }
.record-review { display: flex; align-items: center; gap: 7px; font-size: 13px; white-space: nowrap; }
.current-evidence-content { padding: 0 13px 11px; }
.current-evidence-content ul { margin: 0; padding: 0; list-style: none; }
.current-evidence-content li { display: flex; justify-content: space-between; gap: 8px; padding: 5px 0; border-bottom: 1px solid var(--media-line); font-size: 13px; }
.coupling-boundary { margin-top: 6px !important; }
.capture { display: flex; align-items: center; gap: 9px; padding: 6px 0; border-top: 1px solid var(--media-line); }
.capture img { width: 85px; height: 48px; object-fit: contain; background: #061522; }
.capture div { display: grid; gap: 3px; font-size: 13px; }
.capture a { color: var(--media-accent); }
.trial-details p { margin: 5px 0; }
@media (max-width: 560px) {
  .coupling-session { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .session-source { grid-column: 1 / -1; }
  .record-row { flex-wrap: wrap; }
  .record-open { flex-basis: 100%; }
}
</style>
