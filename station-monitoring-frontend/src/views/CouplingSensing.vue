<template>
  <main class="coupling-workspace" aria-label="车辆接近与连挂辅助感知">
    <header class="work-head">
      <div><span class="eyebrow">RAILWAY OPERATIONS / 作业感知</span><h1>车辆接近与连挂辅助感知</h1><p>查看现场画面及可追溯的感知证据。检测、测距与接触提示分别标明有效状态。</p></div>
      <span class="scope">本地验证工作区</span>
    </header>
    <div class="work-grid">
      <section class="visual-column">
        <div class="panel-head"><h2>作业画面</h2><span>{{ file ? file.name : '未选择来源' }}</span></div>
        <div class="source-bar">
          <label class="source-button" for="coupling-file">选择现场视频或图片</label>
          <input id="coupling-file" type="file" accept="video/mp4,video/webm,video/ogg,image/jpeg,image/png,image/webp" @change="selectFile" />
          <button v-if="file" type="button" @click="clearFile">清除</button>
          <button v-if="file" type="button" :disabled="predicting || !serviceReady" @click="predictCurrentFrame">{{ predicting ? '识别中…' : '识别当前画面' }}</button>
          <button v-if="analyzedFrame" type="button" @click="analyzedFrame = ''">返回原始画面</button>
          <button v-if="isVideo && duration" type="button" @click="captureFrame">保存当前帧</button>
          <span>{{ converting ? '正在转换为浏览器可播放格式…' : serviceReady ? '本机识别服务可用' : '本机识别服务未连接' }}</span>
        </div>
        <p v-if="inferenceError" class="error-message" role="alert">{{ inferenceError }}</p>
        <div class="media-stage">
          <video v-if="url && isVideo" v-show="!analyzedFrame" ref="video" :src="url" controls playsinline preload="metadata" @timeupdate="updateTime" @loadedmetadata="onVideoLoaded" @error="onVideoError" />
          <img v-if="analyzedFrame" :src="analyzedFrame" alt="本机 NCNN 模型检测画面，包含真实预测框" />
          <img v-else-if="url && !isVideo" :src="url" alt="本地选择的原始现场画面，尚未识别" />
          <div v-if="!url" class="media-empty"><strong>请选择一段现场视频或图片</strong><span>画面会在这里按原始比例显示。仅选择文件不会产生模型预测。</span></div>
          <span v-if="url" class="raw-label">{{ analyzedFrame ? 'NCNN 预测 · 待人工复核' : '原始画面 · 尚未识别此帧' }}</span>
        </div>
        <div class="time-panel"><div class="panel-head"><h2>作业时间轴</h2><span>{{ timeText }}</span></div>
          <div class="time-track" aria-label="播放进度"><span :style="{ width: progress + '%' }"></span></div>
          <p>{{ file ? '可以保存当前原始帧作为人工复核材料；检测、测距及传感器事件接入后才会出现对应标记。' : '选择视频后显示播放位置。' }}</p>
        </div>
      </section>
      <aside class="inspector" aria-label="感知结果与有效性">
        <section class="readout"><div class="panel-head"><h2>当前感知</h2><span class="status">尚未运行</span></div>
          <dl><div><dt>车辆／车钩识别</dt><dd>{{ hasPrediction ? `${detections.length} 个预测目标` : '尚无模型结果' }}</dd></div><div><dt>处理耗时</dt><dd>{{ hasPrediction ? `${processingMs} ms` : '—' }}</dd></div><div><dt>距离估计</dt><dd>不可用</dd></div><div><dt>测距条件</dt><dd>未关联相机标定</dd></div></dl>
          <div v-for="(item, index) in detections" :key="index" class="signal-row"><span>{{ item.label }}</span><strong>{{ (item.confidence * 100).toFixed(1) }}% · {{ item.box.join(', ') }}</strong></div>
        </section>
        <section class="signals"><div class="panel-head"><h2>多源判据</h2><span>仅显示实际接入的数据</span></div>
          <div class="signal-row"><span>视觉检测</span><strong>{{ hasPrediction ? (detections.length ? '有目标预测 · 待复核' : '当前帧未检出目标') : '尚未识别当前帧' }}</strong></div>
          <div class="signal-row"><span>声音事件</span><strong>未采集</strong></div>
          <div class="signal-row"><span>冲击事件</span><strong>未采集</strong></div>
          <div class="signal-row"><span>综合提示</span><strong>证据不足</strong></div>
          <p>老师提供的安卓应用具备视觉、声音与加速度规则判断；网页端尚未取得安卓端输出，不能据此判定连挂完成。</p>
        </section>
        <section class="evidence"><div class="panel-head"><h2>本次作业素材</h2><span>{{ captures.length }} 帧</span></div>
          <p v-if="!captures.length">暂无保存的原始帧。保存画面仅供人工复核，不代表模型检测证据。</p>
          <div v-for="item in captures" :key="item.id" class="capture"><img :src="item.url" alt="从本地视频截取的原始画面"/><div><strong>{{ item.time }}</strong><span>原始帧 · 人工保存</span><a :href="item.url" :download="item.filename">下载图片</a></div></div>
        </section>
        <div class="model-note"><strong>模型接入状态：{{ serviceReady ? 'NCNN 本机推理可用' : '本机服务未启动' }}</strong><p>使用老师提供的 best12_20.param/.bin。单帧预测不能证明连挂完成；需要现场样本复核类别和误检。</p></div>
      </aside>
    </div>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
const file = ref(null), url = ref(''), video = ref(null), seconds = ref(0), duration = ref(0), captures = ref([]);
const serviceReady = ref(false), predicting = ref(false), converting = ref(false), converted = ref(false), inferenceError = ref(''), analyzedFrame = ref('');
const detections = ref([]), hasPrediction = ref(false), processingMs = ref(null);
const API = 'http://127.0.0.1:5003';
const isVideo = computed(() => file.value?.type.startsWith('video/'));
const progress = computed(() => duration.value > 0 ? Math.min(100, seconds.value / duration.value * 100) : 0);
const fmt = value => `${String(Math.floor(value / 60)).padStart(2, '0')}:${String(Math.floor(value % 60)).padStart(2, '0')}`;
const timeText = computed(() => isVideo.value && duration.value ? `${fmt(seconds.value)} / ${fmt(duration.value)}` : '无时间数据');
function clearFile() { if (url.value) URL.revokeObjectURL(url.value); captures.value.forEach(item => URL.revokeObjectURL(item.url)); captures.value = []; file.value = null; url.value = ''; seconds.value = 0; duration.value = 0; converting.value = false; converted.value = false; resetPrediction(); }
function resetPrediction() { analyzedFrame.value = ''; detections.value = []; hasPrediction.value = false; processingMs.value = null; inferenceError.value = ''; }
function selectFile(event) { clearFile(); const selected = event.target.files?.[0]; if (!selected) return; if (!(selected.type.startsWith('video/') || selected.type.startsWith('image/'))) return; file.value = selected; url.value = URL.createObjectURL(selected); event.target.value = ''; }
function updateTime() { seconds.value = video.value?.currentTime || 0; duration.value = Number.isFinite(video.value?.duration) ? video.value.duration : 0; resetPrediction(); }
function onVideoLoaded() { updateTime(); inferenceError.value = ''; }
async function onVideoError() {
  if (!file.value || converting.value) return;
  if (converted.value) { inferenceError.value = '转换完成后仍无法播放，请换用较短的 MP4/H.264 文件。'; return; }
  if (!serviceReady.value) { inferenceError.value = '浏览器无法解码此视频；请先启动本机车钩识别服务，再重新选择视频。'; return; }
  const selectedFile = file.value;
  converting.value = true;
  try {
    const response = await fetch(`${API}/transcode`, { method: 'POST', body: selectedFile, headers: { 'Content-Type': 'application/octet-stream' } });
    if (!response.ok) { const data = await response.json(); throw new Error(data.error || '视频转换失败'); }
    const media = await response.blob();
    if (file.value !== selectedFile) return;
    if (url.value) URL.revokeObjectURL(url.value);
    converted.value = true;
    url.value = URL.createObjectURL(media);
    await new Promise(resolve => setTimeout(resolve, 0));
    video.value?.load();
  } catch (error) { inferenceError.value = error.message || '视频转换失败'; }
  finally { converting.value = false; }
}
async function predictCurrentFrame() {
  if (!file.value || predicting.value) return;
  predicting.value = true; inferenceError.value = '';
  try {
    let blob = file.value;
    if (isVideo.value) {
      const element = video.value;
      if (!element || element.readyState < 2) throw new Error('请先播放到需要识别的画面');
      element.pause();
      const canvas = document.createElement('canvas'); canvas.width = element.videoWidth; canvas.height = element.videoHeight;
      canvas.getContext('2d').drawImage(element, 0, 0);
      blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', .9));
    }
    if (!blob) throw new Error('无法读取当前画面');
    const response = await fetch(`${API}/predict`, { method: 'POST', body: blob, headers: { 'Content-Type': blob.type || 'image/jpeg' } });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || '推理失败');
    detections.value = result.detections; processingMs.value = result.processingMs;
    analyzedFrame.value = result.frame; hasPrediction.value = true;
  } catch (error) { inferenceError.value = error.message || '无法连接本机识别服务'; }
  finally { predicting.value = false; }
}
onMounted(async () => { try { const response = await fetch(`${API}/health`); serviceReady.value = response.ok && (await response.json()).ready; } catch { serviceReady.value = false; } });
function captureFrame() {
  const element = video.value;
  if (!element || element.readyState < 2 || !element.videoWidth) return;
  const canvas = document.createElement('canvas'); canvas.width = element.videoWidth; canvas.height = element.videoHeight;
  canvas.getContext('2d').drawImage(element, 0, 0);
  canvas.toBlob(blob => {
    if (!blob) return;
    const time = fmt(element.currentTime);
    captures.value.unshift({ id: crypto.randomUUID(), url: URL.createObjectURL(blob), time,
      filename: `source-frame-${Math.floor(element.currentTime * 1000)}ms.png` });
  }, 'image/png');
}
onBeforeUnmount(clearFile);
</script>

<style scoped>
.coupling-workspace{height:100%;min-height:0;overflow:auto;background:#071d32;color:#e7f0f6;padding:18px 24px;box-sizing:border-box;font-family:inherit}.work-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;gap:16px}.eyebrow{font-size:11px;letter-spacing:.12em;color:#82bad2}.work-head h1{font-size:23px;margin:5px 0;font-weight:650}.work-head p{font-size:13px;color:#a6bac8;margin:0}.scope{font-size:12px;color:#93afbf;border:1px solid #31516a;padding:7px 10px;white-space:nowrap}.work-grid{display:grid;grid-template-columns:minmax(0,2fr) minmax(320px,1fr);gap:16px;min-height:0}.visual-column,.inspector{min-width:0}.visual-column,.inspector>section,.model-note{background:#0c2a44;border:1px solid #28445c}.visual-column{padding:14px}.inspector{display:flex;flex-direction:column;gap:12px}.inspector>section,.model-note{padding:14px}.panel-head{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin-bottom:12px}.panel-head h2{font-size:15px;margin:0;font-weight:600}.panel-head span{font-size:12px;color:#92b2c5}.source-bar{display:flex;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap}.source-bar input{position:absolute;width:1px;height:1px;opacity:0}.source-button,.source-bar button{cursor:pointer;background:#194769;border:1px solid #45718c;color:#eff8fb;padding:8px 12px;font:inherit;font-size:12px}.source-button:hover,.source-bar button:hover,.source-button:focus-within{background:#246185}.source-bar>span{font-size:12px;color:#8eaebf}.media-stage{position:relative;background:#051320;min-height:320px;aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;overflow:hidden}.media-stage video,.media-stage img{width:100%;height:100%;object-fit:contain;position:absolute}.media-empty{text-align:center;display:flex;flex-direction:column;gap:8px;padding:20px}.media-empty span{color:#95aebf;font-size:12px}.raw-label{position:absolute;left:12px;top:12px;padding:5px 8px;background:#071d32e6;font-size:11px;color:#d8e4e9}.time-panel{margin-top:14px}.time-panel p,.signals p,.evidence p,.model-note p{font-size:12px;line-height:1.7;color:#a7bbc8;margin:10px 0 0}.time-track{height:5px;background:#193952}.time-track span{display:block;height:100%;background:#64a7c8}.readout dl{margin:0}.readout dl>div,.signal-row{display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-bottom:1px solid #25435a;font-size:12px}.readout dl>div:last-child,.signal-row:last-of-type{border:0}.readout dt,.signal-row span{color:#a4bbca}.readout dd{margin:0}.signal-row strong{font-weight:500;color:#d2dce4}.status{color:#dfb775!important}.model-note strong{font-size:12px;color:#d0bd87}@media(max-width:900px){.coupling-workspace{padding:14px}.work-grid{grid-template-columns:1fr}.work-head{align-items:flex-start}.media-stage{min-height:240px}.inspector{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:600px){.inspector{display:flex}.work-head{flex-direction:column}.media-stage{min-height:180px}}
.capture{display:flex;gap:10px;padding:9px 0;border-top:1px solid #25435a}.capture img{width:92px;height:60px;object-fit:contain;background:#071d32}.capture div{display:flex;flex-direction:column;gap:3px;font-size:11px}.capture strong{font-size:12px}.capture span{color:#a7bbc8}.capture a{color:#9cddf2}
.source-bar button:disabled{opacity:.5;cursor:not-allowed}.error-message{font-size:12px;color:#efba86;margin:0 0 10px}
</style>
