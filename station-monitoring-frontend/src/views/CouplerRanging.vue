<template>
  <section class="range-panel" aria-label="车钩测距验证">
    <header>
      <h2 v-if="!embedded">车钩距离估算</h2>
      <span>{{ availability }}</span>
    </header>
    <p v-if="!ready">距离估算暂不可用，请联系运维。</p>
    <p v-else-if="!report">请导入当前机位对应的标定档案。</p>
    <p v-else>距离为相机光心到车钩参考面中心的直线距离。</p>
    <details>
      <summary>机位标定与实测</summary>
      <div class="actions">
        <button type="button" @click="download(template, '车钩测距标定模板.json')">下载标定模板</button>
        <button type="button" :disabled="!ready || busy" @click="archiveInput?.click()">导入标定档案</button>
        <input ref="archiveInput" type="file" accept=".json,application/json" hidden @change="importArchive" />
      </div>
      <p v-if="report">{{ report.lens }} · {{ report.installation }} · {{ report.targetId }} · {{ report.targetReference }}</p>
      <p v-if="report">标定来源 {{ report.source }}</p>
    </details>
    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <template v-if="report">
      <p><strong>{{ report.id }} · {{ report.cameraId }}</strong> · {{ report.imageSize.join(' × ') }} px</p>
      <p v-if="report.status === 'passed'">实测覆盖 {{ rangeText }}，平均绝对误差 {{ metres(report.meanAbsoluteErrorM) }}，最大绝对误差 {{ metres(report.maxAbsoluteErrorM) }}。已纳入 {{ report.validCount }} 条有效样本。</p>
      <p v-else>{{ report.reasons.join('。') }}。</p>
      <details v-if="report.samples.length">
        <summary>逐帧实测对照</summary>
        <ul class="sample-list">
          <li v-for="row in report.samples" :key="row.frameRef">
            <strong>{{ row.frameRef }}</strong>
            <span v-if="row.reason">{{ row.reason }}</span>
            <span v-else>实测 {{ metres(row.referenceM) }} · 估算 {{ metres(row.distanceM) }} · 偏差 {{ metres(row.errorM) }}</span>
          </li>
        </ul>
      </details>
      <div class="actions">
        <button type="button" :disabled="!canLoad || busy" @click="capture">取当前原始帧</button>
        <button type="button" @click="download(archive, '车钩测距标定档案.json')">导出档案</button>
        <button type="button" v-if="report.samples.length" @click="download(report, '车钩测距实测对照.json')">导出对照结果</button>
      </div>
    </template>

    <template v-if="frame">
      <p class="frame-ref">{{ frame.frameRef }}</p>
      <p>按左上、右上、右下、左下依次点选四个参考角点。角点应与档案中测量宽高的矩形参考面对应。</p>
      <div class="mark-frame" @click="mark">
        <img :src="frame.src" alt="用于标注参考面角点的原始画面" draggable="false" @load="readFrameSize" />
        <span v-for="(point, index) in corners" :key="index" class="corner"
              :style="{ left: point[0] / frame.imageSize[0] * 100 + '%', top: point[1] / frame.imageSize[1] * 100 + '%' }">{{ index + 1 }}</span>
      </div>
      <p v-if="frame.imageSize && !matchingSize" class="error">当前原帧分辨率与标定档案不一致。</p>
      <div class="actions">
        <button type="button" :disabled="!corners.length || busy" @click="undo">撤销角点</button>
        <span>{{ corners.length }} / 4</span>
      </div>
      <label class="check"><input v-model="sameSetup" :disabled="busy" type="checkbox" />我已核对本帧的相机、镜头、成像设置与参考面均符合档案，四角完整可见。</label>
      <details>
        <summary>录入这一帧的独立实测值</summary>
        <label class="field">实测距离（米）<input v-model.number="referenceM" :disabled="busy" type="number" min="0" step="any" /></label>
        <label class="field">测量工具与基准<input v-model.trim="referenceMethod" :disabled="busy" maxlength="200" placeholder="填写实测工具及测量起止点" /></label>
        <button type="button" :disabled="!canMeasure || !(referenceM > 0) || !referenceMethod" @click="addSample">加入样本并重新对照</button>
      </details>
      <div class="actions" v-if="report.status === 'passed'">
        <button type="button" :disabled="!canMeasure" @click="estimateDistance">估算本帧距离</button>
        <strong v-if="estimate && sameSetup">估算 {{ metres(estimate.distanceM) }}</strong>
      </div>
      <details v-if="estimate && sameSetup"><summary>本帧估算依据</summary><p>档案 {{ estimate.calibrationId }} · 重投影误差 {{ estimate.reprojectionPx.toFixed(2) }} px</p></details>
    </template>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import template from './couplerRangingTemplate.json';

const props = defineProps({
  api: { type: String, required: true },
  ready: Boolean,
  source: { type: Object, default: null },
  canLoad: Boolean,
  embedded: Boolean,
  loadFrame: { type: Function, required: true },
});
const archiveInput = ref(null);
const archive = ref(null), report = ref(null), busy = ref(false), error = ref('');
const frame = ref(null), corners = ref([]), sameSetup = ref(false);
const referenceM = ref(null), referenceMethod = ref(''), estimate = ref(null);
let pending = null;

const availability = computed(() => {
  if (!props.ready) return '服务未就绪';
  if (!report.value) return '缺少标定';
  if (report.value.status === 'pending') return '等待实测对照';
  if (report.value.status === 'failed') return '实测对照未通过';
  return '已通过档案实测对照';
});
const metres = value => value == null ? '—' : value.toFixed(3) + ' m';
const rangeText = computed(() => report.value?.observedRangeM?.map(metres).join(' 至 ') || '—');
const matchingSize = computed(() => frame.value?.imageSize?.every((n, i) => n === report.value?.imageSize[i]));
const canMeasure = computed(() => !busy.value && matchingSize.value && corners.value.length === 4 && sameSetup.value);

function resetFrame() {
  frame.value = null;
  corners.value = [];
  sameSetup.value = false;
  referenceM.value = null;
  referenceMethod.value = '';
  estimate.value = null;
}
watch(() => props.source, () => {
  resetFrame();
  error.value = '';
});
watch(sameSetup, () => { estimate.value = null; });
onBeforeUnmount(() => pending?.abort());

function download(data, filename) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function request(action, payload) {
  const controller = new AbortController();
  pending = controller;
  try {
    const response = await fetch(`${props.api}/ranging/${action}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || '测距服务请求失败');
    return result;
  } finally {
    if (pending === controller) pending = null;
  }
}

async function run(action) {
  if (busy.value) return;
  busy.value = true;
  error.value = '';
  try { await action(); }
  catch (failure) {
    if (failure.name !== 'AbortError') error.value = failure.message || '测距操作失败';
  } finally { busy.value = false; }
}

async function applyArchive(next) {
  const result = await request('compare', { archive: next });
  archive.value = next;
  report.value = result;
  estimate.value = null;
}

function importArchive(event) {
  const selected = event.target.files?.[0];
  event.target.value = '';
  if (!selected) return;
  run(async () => {
    if (selected.size > 128 * 1024) throw new Error('标定档案不能超过 128 KB');
    const text = await selected.text();
    let next;
    try { next = JSON.parse(text.replace(/^\uFEFF/, '')); }
    catch (_) { throw new Error('标定档案不是有效的 JSON 文件'); }
    await applyArchive(next);
    resetFrame();
  });
}

function capture() {
  run(async () => {
    const source = props.source;
    const snapshot = await props.loadFrame();
    if (props.source !== source) return;
    resetFrame();
    frame.value = snapshot;
  });
}

function readFrameSize(event) {
  if (frame.value && event.target.getAttribute('src') === frame.value.src)
    frame.value.imageSize = [event.target.naturalWidth, event.target.naturalHeight];
}

function mark(event) {
  if (busy.value || !matchingSize.value || corners.value.length >= 4 || event.target.tagName !== 'IMG') return;
  const bounds = event.target.getBoundingClientRect();
  const [width, height] = frame.value.imageSize;
  const x = (event.clientX - bounds.left) * width / bounds.width;
  const y = (event.clientY - bounds.top) * height / bounds.height;
  corners.value.push([Math.round(x * 100) / 100, Math.round(y * 100) / 100]);
  estimate.value = null;
}

function undo() {
  corners.value.pop();
  estimate.value = null;
}

function markedFrame() {
  return { imageSize: frame.value.imageSize, corners: corners.value, sameSetup: sameSetup.value };
}

function addSample() {
  run(async () => {
    const sample = {
      ...markedFrame(), frameRef: frame.value.frameRef, kind: 'field_measured',
      referenceMethod: referenceMethod.value, referenceM: referenceM.value,
    };
    const previous = archive.value.samples.filter(row => row.frameRef !== sample.frameRef);
    await applyArchive({ ...archive.value, samples: [...previous, sample] });
  });
}

function estimateDistance() {
  run(async () => {
    estimate.value = null;
    const current = frame.value;
    const value = await request('estimate', { archive: archive.value, frame: markedFrame() });
    if (frame.value === current) estimate.value = value;
  });
}

defineExpose({
  snapshotFor(frameRef) {
    if (frame.value?.frameRef !== frameRef || !sameSetup.value || !estimate.value) return null;
    return { ...estimate.value, corners: corners.value.map(point => [...point]), imageSize: [...frame.value.imageSize] };
  },
});
</script>

<style scoped>
.range-panel { min-width: 0; padding: 14px; border: 1px solid #28445c; background: #0c2a44; }
header, .actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
header { justify-content: space-between; }
h2 { margin: 0; font-size: 15px; }
p, span, label, summary, li { font-size: 12px; line-height: 1.65; color: #a7bbc8; }
.actions { margin-block: 8px; }
button, input:not([type=checkbox]) { padding: 5px 8px; border: 1px solid #45667c; background: #12344f; color: #e3eff7; font: inherit; font-size: 12px; }
button:disabled { opacity: .5; }
.error { color: #ffc791; }
.mark-frame { position: relative; }
.mark-frame img { display: block; width: 100%; cursor: crosshair; }
.corner { position: absolute; translate: -50% -50%; border-radius: 50%; background: #e3ad58; color: #0a2030; width: 18px; text-align: center; pointer-events: none; }
.check, .field { display: flex; align-items: center; gap: 6px; margin-block: 8px; }
.field input { flex: 1; min-width: 0; }
.sample-list { padding-left: 18px; max-height: 180px; overflow: auto; }
.sample-list li span { display: block; }
.frame-ref, .sample-list strong { overflow-wrap: anywhere; }
</style>
