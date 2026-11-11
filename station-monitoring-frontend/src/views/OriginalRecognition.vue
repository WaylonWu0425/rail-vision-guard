<template>
  <main class="original-page" aria-label="人车识别">
    <header class="page-heading">
      <div class="heading-title"><span class="heading-icon"><el-icon :size="22"><Monitor /></el-icon></span>
        <div><h1>人车识别 <span>YOLOv8n / best.pt</span></h1><p>选择输入，查看原版模型的实际预测。不生成业务告警。</p></div></div>
      <div class="heading-actions"><span class="connection-state" :class="{ offline: !connected }" role="status"><i></i>{{ connected ? '本机原版识别服务已连接' : '识别服务未连接' }}</span>
        <el-button @click="$router.push('/imageDetection')">返回智能检测</el-button></div>
    </header>

    <div class="recognition-layout">
      <section class="viewer-card" aria-label="识别画面">
        <div class="viewer-heading"><div class="viewer-title"><span class="section-number">01</span><strong :title="job?.name || file?.name">{{ job?.name || file?.name || '识别画面' }}</strong></div>
          <span class="task-status" :class="{ running: active, failed: job?.state === 'failed' }" role="status">{{ statusText }}</span></div>
        <div class="picture-stage" :class="{ 'has-media': frameUrl || (previewUrl && !previewUnavailable) }">
          <img v-if="frameUrl" :src="frameUrl" alt="原版 best.pt 人车检测结果" />
          <img v-else-if="previewUrl && !previewUnavailable && mode === 'image'" :src="previewUrl" alt="所选图片原始预览，尚未运行识别" @error="previewUnavailable = true" />
          <video v-else-if="previewUrl && !previewUnavailable && mode === 'video'" ref="previewVideo" :src="previewUrl" controls muted playsinline preload="metadata" aria-label="所选视频原始预览，尚未运行识别" @error="previewUnavailable = true"></video>
          <div v-else class="empty-state"><span class="empty-icon"><el-icon :size="34"><Monitor /></el-icon></span>
            <strong>{{ active || starting ? '正在读取输入并加载原版模型' : hasInput ? '输入已就绪，可以开始识别' : '从一张图片或一段视频开始' }}</strong>
            <span v-if="active || starting">首次加载可能较慢，请等待；不会显示模拟结果。</span>
            <span v-else-if="previewUnavailable">浏览器无法预览此格式，不影响提交给识别服务。请点击右侧“开始识别”。</span>
            <span v-else>{{ hasInput ? '准备好后点击右侧“开始识别”，查看人车预测框。' : '支持图片、本地视频、本机摄像头与网络摄像头' }}</span>
            <el-button v-if="!file && ['image', 'video'].includes(mode) && !active && !starting" class="choose-action" @click="openFile">{{ mode === 'image' ? '选择图片' : '选择本地视频' }}</el-button>
            <div v-if="!hasInput" class="empty-steps"><span>1 选择输入</span><span>2 开始识别</span><span>3 查看结果</span></div>
          </div>
          <span v-if="previewUrl && !frameUrl && !previewUnavailable" class="preview-badge">原始预览 · 尚未识别</span>
          <span v-if="(active || starting) && !frameUrl && previewUrl" class="loading-badge" role="status">正在加载模型并读取输入…</span>
        </div>
        <div class="playback-controls">
          <span>{{ frameDescription }}</span>
          <div>
            <el-button v-if="job?.mode === 'video' && active" @click="control(job.state === 'paused' ? 'resume' : 'pause')" :disabled="controlling || job.state === 'loading'">
              {{ job.state === 'paused' ? '继续识别' : '暂停识别' }}</el-button>
            <el-button v-if="active" type="danger" plain :disabled="controlling" @click="control('stop')">停止识别</el-button>
          </div>
        </div>
        <div v-if="job?.totalFrames && job.mode === 'video'" class="progress-track" aria-label="视频识别进度">
          <div :style="{ width: `${Math.min(100, job.frameIndex / job.totalFrames * 100)}%` }"></div>
        </div>
        <p v-if="job?.mode === 'video'" class="viewer-note">逐帧计算，速度受本机性能影响；页面展示最近完成帧。</p>
        <details class="results-section" open>
          <summary class="section-heading"><h2><span class="section-number">02</span>当前帧检测结果</h2><span>{{ hasResult ? `人员 ${job.counts.person} · 汽车 ${job.counts.car}` : '等待识别' }} <el-icon><ArrowDown /></el-icon></span></summary>
          <el-table v-if="hasResult" :data="job.detections" empty-text="当前帧未检出目标；这不等于画面中一定无人" max-height="240">
            <el-table-column label="类别" width="120"><template #default="{ row }">{{ row.label === 'person' ? '人员' : '汽车' }} / {{ row.label }}</template></el-table-column>
            <el-table-column label="置信度" width="100"><template #default="{ row }">{{ (row.confidence * 100).toFixed(1) }}%</template></el-table-column>
            <el-table-column label="检测框 [左, 上, 右, 下] · 像素"><template #default="{ row }">{{ row.box.join(', ') }}</template></el-table-column>
          </el-table>
          <p v-else class="results-empty">{{ job?.state === 'failed' ? '任务失败，尚无检测结果。请根据右侧提示处理后重试。' : active || starting ? '正在等待第一帧预测结果…' : '开始识别后，这里将显示目标类别、置信度和位置。' }}</p>
        </details>
      </section>

      <aside class="side-column">
        <section class="settings-card">
        <div class="panel-heading"><h2>输入与操作</h2><span>先选来源，再开始识别</span></div>
        <div class="mode-buttons" role="group" aria-label="选择识别输入">
          <button v-for="item in modes" :key="item.value" :class="{ selected: mode === item.value }" :aria-pressed="mode === item.value" :disabled="active || starting" @click="selectMode(item.value)">{{ item.label }}</button>
        </div>

        <div v-if="mode === 'image' || mode === 'video'" class="source-input">
          <label for="original-file">{{ mode === 'image' ? '图片文件' : '本地视频文件' }}</label>
          <input id="original-file" ref="fileInput" :key="mode" class="file-input" type="file" :accept="mode === 'image' ? '.jpg,.jpeg,.png,.webp,.bmp' : '.mp4,.avi,.mov,.mkv,.webm'" :disabled="active || starting" @change="selectFile" />
          <button class="file-picker" :disabled="active || starting" @click="openFile">
            <span class="file-icon"><el-icon :size="22"><Upload /></el-icon></span>
            <span class="file-description"><strong :title="file?.name">{{ file?.name || (mode === 'image' ? '点击选择图片' : '点击选择本地视频') }}</strong><small>{{ file ? `${formatSize(file.size)} · 点击更换` : '文件仅在本机处理' }}</small></span>
            <el-icon><ArrowRight /></el-icon>
          </button>
          <p>{{ mode === 'image' ? 'JPG / PNG / WebP / BMP · 最大16 MB' : 'MP4 / AVI / MOV / MKV / WebM · 最大512 MB' }}</p>
        </div>
        <div v-else-if="mode === 'usb'" class="source-input">
          <label for="original-usb">本机摄像头编号</label>
          <el-input-number id="original-usb" v-model="deviceIndex" :min="0" :max="9" :disabled="active || starting" @change="clearResult" />
          <p>读取运行识别服务的这台电脑上的摄像头。默认编号0；被其他程序占用时请先关闭占用程序。</p>
        </div>
        <div v-else class="source-input">
          <label for="original-network">已配置的网络摄像头</label>
          <el-select id="original-network" v-model="cameraId" placeholder="请选择摄像头" :disabled="active || starting" :loading="loadingCameras" @change="clearResult">
            <el-option v-for="camera in cameras" :key="camera.id" :value="camera.id" :label="camera.name || `摄像头 ${camera.id}`" />
          </el-select>
          <el-button text :disabled="active || loadingCameras" @click="loadCameras">刷新设备列表</el-button>
          <p>直接读取设备主码流进行识别，不启动现有区域告警任务。</p>
          <p v-if="cameraError" class="error-text">{{ cameraError }}</p>
        </div>

        <p v-if="error" class="error-box" role="alert">{{ error }}</p>
        <div class="start-row"><el-button class="primary-start" type="primary" :loading="starting" :disabled="active || !connected || !hasInput" @click="start"><el-icon v-if="!starting"><VideoPlay /></el-icon>开始识别</el-button>
          <el-button v-if="!connected" @click="connect">重新连接</el-button></div>
        <p class="action-hint">{{ !connected ? '请先连接本机识别服务（5002端口）。' : active ? '任务运行中，请在画面下方暂停或停止。' : !hasInput ? '选择输入后即可开始。' : '已就绪；仅输出模型预测，不写入业务告警。' }}</p>
        </section>

        <section class="metrics-card" aria-label="当前帧识别概况"><div class="panel-heading"><h2>识别概况</h2><span>{{ hasResult ? '当前完成帧' : '尚无结果' }}</span></div>
          <div class="metrics-grid"><div><span>人员预测</span><strong>{{ hasResult ? job.counts.person : '—' }}<small>个</small></strong></div><div><span>汽车预测</span><strong>{{ hasResult ? job.counts.car : '—' }}<small>个</small></strong></div>
            <div><span>当前处理耗时</span><strong>{{ hasResult ? job.processingMs : '—' }}<small>ms</small></strong></div><div><span>平均完成频率</span><strong>{{ hasResult ? job.completedHz : '—' }}<small>次/秒</small></strong></div></div>
        </section>
        <details class="model-info"><summary><span>模型参数与能力说明</span><el-icon><ArrowDown /></el-icon></summary>
          <dl><div><dt>权重</dt><dd>best.pt · YOLOv8n</dd></div><div><dt>类别</dt><dd>person / car</dd></div>
            <div><dt>推理输入</dt><dd>640 · 整图</dd></div><div><dt>阈值</dt><dd>置信度0.25 / NMS IoU 0.7</dd></div>
            <div><dt>运行设备</dt><dd>CPU</dd></div></dl>
          <p>固定使用已核验的原版权重，按原版直接检测脚本接入；当前运行库与原训练环境不完全相同，不承诺逐像素复现。</p>
          <p>图片上限1600万像素。视频临时副本处理后删除；浏览器不保证预览所有编码，模型识别以服务解码为准。</p>
        </details>
        <div class="boundary-note"><el-icon :size="17"><InfoFilled /></el-icon><p>仅检测人、汽车，不自动识别轨道或判定违规。数量是当前帧预测，置信度不等于准确率。</p></div>
      </aside>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { Monitor, Upload, ArrowDown, ArrowRight, VideoPlay, InfoFilled } from '@element-plus/icons-vue';

// Local-only service. No footage is sent to a cloud service or business database.
const API = 'http://127.0.0.1:5002/original';
const modes = [{ value: 'image', label: '图片' }, { value: 'video', label: '本地视频' }, { value: 'usb', label: '本机摄像头' }, { value: 'rtsp', label: '网络摄像头' }];
const mode = ref('video'), file = ref(null), deviceIndex = ref(0), cameraId = ref(null);
const cameras = ref([]), loadingCameras = ref(false), cameraError = ref('');
const connected = ref(false), starting = ref(false), controlling = ref(false), error = ref('');
const job = ref(null), frameUrl = ref('');
const fileInput = ref(null), previewVideo = ref(null), previewUrl = ref(''), previewUnavailable = ref(false);
let token = '', timer = null, disposed = false, generation = 0;
const requests = new Set();
const active = computed(() => job.value && ['loading', 'running', 'paused', 'stopping'].includes(job.value.state));
const hasInput = computed(() => ['image', 'video'].includes(mode.value) ? Boolean(file.value) : mode.value === 'usb' ? Number.isInteger(deviceIndex.value) : Boolean(cameraId.value));
const hasResult = computed(() => Boolean(job.value?.frameIndex));
const statusText = computed(() => starting.value ? '正在提交' : ({ loading: '模型加载 / 输入读取中', running: '识别中', paused: '已暂停', finished: '识别完成', stopped: '已停止', failed: '识别失败' }[job.value?.state] || (hasInput.value ? '待开始' : '未选择输入')));
const frameDescription = computed(() => !hasResult.value ? (file.value ? '原始素材 · 尚无检测结果' : '等待选择输入') : `${job.value.width} × ${job.value.height} · 第 ${job.value.frameIndex} 帧${job.value.mediaSeconds == null ? '' : ` · 视频 ${job.value.mediaSeconds.toFixed(2)} 秒`}`);
const formatSize = size => size < 1024 * 1024 ? `${(size / 1024).toFixed(1)} KB` : `${(size / 1024 / 1024).toFixed(1)} MB`;
function openFile() { fileInput.value?.click(); }
function clearResult() { generation++; clearTimeout(timer); job.value = null; frameUrl.value = ''; error.value = ''; }
function releasePreview() { previewVideo.value?.pause(); if (previewUrl.value) URL.revokeObjectURL(previewUrl.value); previewUrl.value = ''; previewUnavailable.value = false; }

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
  error.value = '';
  try { const data = await api('/config'); if (disposed) return; token = data.token; connected.value = true; }
  catch (_) { if (!disposed) { connected.value = false; error.value = '请运行 scan/Detection/启动原版识别.cmd，或重新运行系统启动脚本，然后点击“重新连接”。'; } }
}
function selectMode(value) {
  if (value === mode.value || active.value || starting.value) return;
  releasePreview(); clearResult(); mode.value = value; file.value = null;
  if (value === 'rtsp') loadCameras();
}
function selectFile(event) {
  releasePreview(); clearResult(); file.value = event.target.files[0] || null;
  if (!file.value) return;
  if (file.value.size > (mode.value === 'image' ? 16 : 512) * 1024 * 1024) {
    error.value = '文件超过允许大小，请缩小图片或截取较短视频。'; file.value = null; event.target.value = ''; return;
  }
  previewUrl.value = URL.createObjectURL(file.value);
}
async function loadCameras() {
  loadingCameras.value = true; cameraError.value = '';
  try { const data = await api('/cameras'); if (!disposed) cameras.value = data.data; }
  catch (e) { if (!disposed) cameraError.value = e.message; }
  finally { loadingCameras.value = false; }
}
async function start() {
  error.value = '';
  if (['image', 'video'].includes(mode.value) && !file.value) { error.value = '请先选择文件。'; return; }
  if (mode.value === 'rtsp' && !cameraId.value) { error.value = '请先选择网络摄像头。'; return; }
  if (file.value && file.value.size > (mode.value === 'image' ? 16 : 512) * 1024 * 1024) { error.value = '文件超过允许大小，请缩小图片或截取较短视频。'; return; }
  starting.value = true;
  previewVideo.value?.pause(); frameUrl.value = ''; job.value = null;
  const mine = ++generation;
  clearTimeout(timer);
  try {
    let options;
    if (['image', 'video'].includes(mode.value)) {
      const form = new FormData(); form.append('mode', mode.value); form.append('file', file.value);
      options = { method: 'POST', body: form };
    } else options = { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ mode: mode.value, deviceIndex: deviceIndex.value, cameraId: cameraId.value }) };
    const result = await api('/jobs', options);
    if (disposed || mine !== generation) return;
    frameUrl.value = ''; job.value = result.data; poll(mine);
  } catch (e) { if (!disposed) error.value = e.message || '连接失败，请确认识别服务已启动。'; }
  finally { starting.value = false; }
}
async function poll(mine) {
  if (disposed || mine !== generation || !job.value) return;
  try {
    const result = await api(`/jobs/${job.value.id}`);
    if (disposed || mine !== generation) return;
    const previous = job.value.frameIndex; job.value = result.data;
    if (job.value.frameIndex && (previous !== job.value.frameIndex || !frameUrl.value)) frameUrl.value = `${API}/jobs/${job.value.id}/frame?v=${job.value.frameIndex}`;
    if (job.value.error) error.value = job.value.error;
    if (active.value) timer = setTimeout(() => poll(mine), 650);
  } catch (e) { if (!disposed) { error.value = `${e.message}。请先停止任务后重试；摄像头任务失联120秒后自动释放。`; timer = setTimeout(() => poll(mine), 3000); } }
}
async function control(action) {
  if (!job.value || controlling.value) return;
  controlling.value = true; error.value = '';
  try {
    await api(`/jobs/${job.value.id}/${action}`, { method: 'POST' });
    clearTimeout(timer); timer = setTimeout(() => poll(generation), 100);
  } catch (e) { error.value = e.message; }
  finally { controlling.value = false; }
}
function leave() {
  if (job.value && active.value) fetch(`${API}/jobs/${job.value.id}/stop`, {
    method: 'POST', headers: { 'X-Original-Token': token }, keepalive: true }).catch(() => {});
}
onMounted(() => { connect(); window.addEventListener('pagehide', leave); });
onUnmounted(() => {
  leave(); releasePreview(); disposed = true; generation++; clearTimeout(timer);
  requests.forEach(controller => controller.abort()); requests.clear();
  window.removeEventListener('pagehide', leave);
});
</script>

<style scoped>
.original-page { flex: 1 1 0; width: 100%; height: 100%; min-width: 0; min-height: 0; overflow-y: auto; padding: 20px 24px; box-sizing: border-box; background: #f3f6fa; color: #19324d; scrollbar-gutter: stable; }
.page-heading, .heading-title, .heading-actions { display: flex; align-items: center; gap: 14px; }
.page-heading { justify-content: space-between; margin-bottom: 20px; min-height: 54px; }
.heading-title { min-width: 0; } .heading-icon { width: 44px; height: 44px; display: grid; place-items: center; color: #226cc4; border: 1px solid #d5e2f3; background: #eaf2fc; border-radius: 10px; flex-shrink: 0; }
h1 { margin: 0 0 6px; font-size: 21px; letter-spacing: .3px; } h1 > span { font-size: 11px; letter-spacing: 0; font-weight: 500; color: #526579; margin-left: 12px; }
h2 { font-size: 14px; margin: 0; } .page-heading p { margin: 0; color: #526579; font-size: 12px; line-height: 1.6; }
.heading-actions { flex-shrink: 0; gap: 16px; }
.connection-state { display: flex; align-items: center; gap: 7px; font-size: 12px; color: #315a4a; }
.connection-state i { width: 7px; height: 7px; border-radius: 50%; background: #209566; box-shadow: 0 0 0 3px #e4f3ec; }
.connection-state.offline { color: #a02a20; } .connection-state.offline i { background: #bf4337; box-shadow: 0 0 0 3px #fbece9; }
.recognition-layout { display: grid; width: 100%; min-width: 0; grid-template-columns: minmax(0, 1fr) 370px; gap: 20px; align-items: start; }
.viewer-card, .settings-card, .metrics-card, .model-info { background: #fff; border: 1px solid #dce5f0; border-radius: 10px; min-width: 0; }
.viewer-card { overflow: hidden; }
.viewer-heading, .playback-controls, .section-heading { display: flex; gap: 12px; justify-content: space-between; align-items: center; padding: 15px 18px; }
.viewer-title { display: flex; align-items: center; gap: 10px; min-width: 0; } .viewer-title strong { font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.section-number { color: #497296; background: #edf3f9; border: 1px solid #dfe8f2; border-radius: 4px; font-size: 10px; padding: 3px 5px; font-weight: 500; margin-right: 8px; }
.viewer-title .section-number { margin-right: 0; }
.task-status { font-size: 11px; color: #526579; padding: 4px 8px; background: #f1f4f8; border-radius: 4px; flex-shrink: 0; }
.task-status.running { background: #e9f2ff; color: #1d64bc; } .task-status.failed { color: #a02a20; background: #fcefeb; }
.playback-controls { min-height: 55px; box-sizing: border-box; } .playback-controls > span, .section-heading > span { font-size: 12px; color: #526579; }
.picture-stage { position: relative; height: clamp(320px, 48vh, 560px); display: grid; place-items: center; background: #f7f9fc; border-top: 1px solid #e7edf4; border-bottom: 1px solid #e7edf4; }
.picture-stage.has-media { background: #162534; }
.picture-stage > img, .picture-stage > video { display: block; width: 100%; height: 100%; max-height: clamp(320px, 48vh, 560px); object-fit: contain; min-height: 0; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 13px; padding: 24px; text-align: center; color: #213f5b; }
.empty-icon { display: grid; place-items: center; width: 72px; height: 72px; margin-bottom: 4px; background: #edf3fa; border: 1px solid #dce7f3; border-radius: 18px; color: #507ba4; }
.empty-state > strong { font-size: 18px; font-weight: 600; } .empty-state > span:not(.empty-icon) { font-size: 12px; color: #526579; max-width: 460px; line-height: 1.8; }
.empty-steps { display: flex; gap: 24px; margin-top: 16px; font-size: 11px; color: #60778e; }
.preview-badge, .loading-badge { position: absolute; top: 14px; left: 14px; border-radius: 5px; padding: 7px 10px; font-size: 11px; background: #142536e6; color: #fff; pointer-events: none; }
.loading-badge { top: auto; bottom: 16px; background: #fff; color: #1a5ca8; border: 1px solid #cbdcf0; }
.progress-track { height: 3px; background: #e7eef7; } .progress-track div { height: 100%; background: #2275df; }
.viewer-note { margin: 0; padding: 0 18px 12px; color: #526579; font-size: 11px; line-height: 1.7; }
.results-section { border-top: 1px solid #e2e9f2; }
.section-heading { list-style: none; cursor: pointer; } summary::-webkit-details-marker { display: none; }
.section-heading h2 { display: flex; align-items: center; } .section-heading > span { display: flex; align-items: center; gap: 12px; }
details[open] > summary .el-icon { transform: rotate(180deg); }
.results-empty { font-size: 12px; color: #60748a; padding: 4px 18px 22px; margin: 0; }
.side-column { display: flex; flex-direction: column; gap: 16px; min-width: 0; }
.settings-card, .metrics-card { padding: 20px; }
.panel-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; } .panel-heading > span { font-size: 10px; color: #60748a; }
.mode-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 18px 0 20px; }
.mode-buttons button { padding: 10px 5px; border: 1px solid #d5dfec; border-radius: 6px; background: #fff; color: #344d67; cursor: pointer; transition: background .15s; font-size: 12px; }
.mode-buttons button:hover, .mode-buttons button.selected { background: #edf4ff; border-color: #357ed1; color: #1762b8; }
.mode-buttons button.selected { font-weight: 600; }
.mode-buttons button:disabled, .file-picker:disabled { cursor: not-allowed; opacity: .6; }
button:focus-visible, input:focus-visible, summary:focus-visible { outline: 2px solid #246ed1; outline-offset: 3px; }
.source-input { display: flex; flex-direction: column; gap: 10px; }
.source-input label { font-size: 12px; font-weight: 600; }
.source-input p, .model-info p, .boundary-note p { color: #526579; font-size: 11px; line-height: 1.8; margin: 0; }
.file-input { position: absolute; width: 1px; height: 1px; clip-path: inset(50%); overflow: hidden; white-space: nowrap; }
.file-picker { display: flex; align-items: center; gap: 10px; width: 100%; padding: 15px 12px; text-align: left; cursor: pointer; background: #f8fafd; border: 1px dashed #b6cbe3; border-radius: 7px; color: #3d6c9e; }
.file-picker:hover:not(:disabled) { border-color: #2878cf; background: #f0f6ff; }
.file-icon { flex-shrink: 0; } .file-description { display: flex; flex-direction: column; gap: 6px; min-width: 0; flex: 1; }
.file-description strong { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #253f59; font-size: 12px; font-weight: 500; } .file-description small { font-size: 10px; color: #60748a; }
.start-row { display: flex; gap: 8px; margin-top: 20px; } .start-row > .el-button:first-child { flex: 1; height: 40px; }
.original-page :deep(.primary-start.el-button:not(.is-disabled)) { color: white; background: #1d6ed0; border-color: #1d6ed0; font-weight: 600; }
.original-page :deep(.primary-start.el-button:not(.is-disabled):hover) { background: #195eb3; border-color: #195eb3; }
.original-page :deep(.primary-start.is-disabled) { background: #e3eaf3; border-color: #d9e2ee; color: #60748a; }
.primary-start .el-icon { margin-right: 6px; }
.action-hint { color: #60748a; font-size: 11px; line-height: 1.7; margin: 9px 0 0; }
.metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 12px; margin-top: 20px; }
.metrics-grid > div { display: flex; flex-direction: column; gap: 9px; } .metrics-grid > div > span { color: #526579; font-size: 11px; }
.metrics-grid strong { font-size: 23px; font-weight: 600; font-variant-numeric: tabular-nums; line-height: 1.1; } .metrics-grid small { margin-left: 6px; color: #60748a; font-size: 10px; font-weight: 400; }
.model-info { padding: 0 18px; } .model-info > summary { padding: 15px 0; display: flex; align-items: center; justify-content: space-between; font-size: 12px; list-style: none; cursor: pointer; }
.model-info p { margin: 0 0 12px; }
dl { font-size: 11px; } dl div { display: flex; justify-content: space-between; gap: 10px; margin: 12px 0; } dt { color: #526579; } dd { margin: 0; text-align: right; }
.boundary-note { display: flex; gap: 9px; padding: 0 2px; color: #527596; } .boundary-note .el-icon { flex-shrink: 0; margin-top: 3px; }
.error-box { background: #fff3f1; border: 1px solid #f1c7bf; color: #a02a20; padding: 12px; font-size: 12px; line-height: 1.7; border-radius: 6px; }
.error-text { color: #a02a20 !important; }
@media (max-width: 1280px) { .recognition-layout { grid-template-columns: minmax(0, 1fr) 330px; gap: 16px; } .original-page { padding: 16px; } h1 > span { display: none; } .heading-actions { gap: 10px; } }
@media (max-width: 1000px) { .recognition-layout { grid-template-columns: minmax(0, 1fr) 300px; } .heading-icon { display: none; } .connection-state { max-width: 140px; line-height: 1.5; } .settings-card, .metrics-card { padding: 15px; } }
</style>
