<template>
  <section class="review-panel" aria-label="作业人工核查">
    <header><h2>复核记录</h2><span>仅保存在此浏览器</span></header>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="notice" role="status">{{ notice }}</p>
    <p v-if="!owner">登录后可保存本地核查记录。</p>
    <p v-else-if="!source">打开作业素材后可复核画面。</p>
    <button v-if="source && !draft" class="media-action" :class="{ 'media-action--primary': record }" type="button" :disabled="busy || !owner || !canCapture" @click="captureFrame">{{ record ? '复核所选检测记录' : '复核当前画面' }}</button>
    <template v-if="draft">
      <img :src="draft.originalFrame" alt="待核查原始画面" />
      <p>{{ draft.frameRef }}</p>
      <p>{{ draft.prediction ? '已关联模型框图和检测记录' : '人工截图 · 无对应模型记录' }}</p>
      <p>对齐证据：{{ evidenceSummary(draft) }}</p>
      <p v-if="draft.ranging">参考面距离估计 {{ draft.ranging.distanceM.toFixed(3) }} m · {{ draft.ranging.calibrationId }}</p>
      <label>核查结论<select v-model="verdict" :disabled="busy">
        <option value="" disabled>请选择</option>
        <option v-for="(label, value) in verdicts" :key="value" :value="value">{{ label }}</option>
      </select></label>
      <label>复核说明<textarea v-model.trim="note" rows="2" maxlength="1000" :disabled="busy" placeholder="写明看到什么、依据和局限" /></label>
      <div class="actions">
        <button class="media-action media-action--primary" type="button" :disabled="busy || !verdict || !note.trim()" @click="save">保存复核</button>
        <button class="media-action" type="button" :disabled="busy" @click="draft = null">取消复核</button>
      </div>
    </template>
    <details ref="savedDetails">
      <summary ref="savedHeading">已保存记录（{{ cases.length }}）</summary>
      <button type="button" :disabled="busy || !owner" @click="refreshList">刷新归档</button>
      <p v-if="owner && !cases.length">还没有已保存的复核记录。</p>
      <label v-if="cases.length">查阅记录<select v-model="selectedId" :disabled="busy">
        <option value="" disabled>请选择</option>
        <option v-for="item in cases" :key="item.id" :value="item.id">{{ label(item) }}</option>
      </select></label>
      <template v-if="selected">
        <p>{{ selected.evidence.frameRef }}</p>
        <img :src="selected.evidence.originalFrame" alt="归档原始画面" />
        <img v-if="selected.evidence.prediction" :src="selected.evidence.prediction.annotatedFrame" alt="归档模型标注画面" />
        <p>对齐证据：{{ evidenceSummary(selected.evidence) }}</p>
        <p v-if="selected.evidence.ranging">参考面距离估计 {{ selected.evidence.ranging.distanceM.toFixed(3) }} m · {{ selected.evidence.ranging.calibrationId }}</p>
        <div class="actions">
          <button type="button" :disabled="!matchesSource || !canCapture" @click="$emit('seek', selected.evidence.videoSeconds)">跳回对应视频</button>
          <button type="button" @click="downloadJson(selected, '作业核查-' + selected.id + '.json')">导出核查与版本</button>
        </div>
        <p v-if="selected.evidence.videoSeconds != null && !matchesSource">请打开该记录对应的原始录像后回看。</p>
        <ol>
          <li v-for="(review, index) in selected.reviews" :key="index">第 {{ index + 1 }} 版 · {{ verdicts[review.verdict] }} · {{ review.reviewer }} · {{ new Date(review.at).toLocaleString() }}<p>{{ review.note }}</p></li>
        </ol>
        <label>补充结论<select v-model="revisionVerdict" :disabled="busy">
          <option value="" disabled>请选择</option>
          <option v-for="(text, value) in verdicts" :key="value" :value="value">{{ text }}</option>
        </select></label>
        <label>补充说明<textarea v-model.trim="revisionNote" rows="2" maxlength="1000" :disabled="busy" /></label>
        <button type="button" :disabled="busy || !revisionVerdict || !revisionNote.trim()" @click="revise">追加复核版本</button>
      </template>
      <p v-if="cases.length">转交复核时，请将导出记录与原始录像、录音和传感器文件一并提供。</p>
    </details>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { appendReview, archiveCase, downloadJson, listCases } from '../utils/couplerArchive';
import { sourceIdentity } from '../utils/couplerSync';

const props = defineProps({
  owner: String, reviewer: String, source: Object, record: Object,
  canCapture: Boolean, capture: { type: Function, required: true },
});
const emit = defineEmits(['seek', 'draft-change']);
const verdicts = { observed: '已核对画面', suspected: '疑似异常 · 待业务复核', insufficient: '证据不足' };
const cases = ref([]), selectedId = ref(''), draft = ref(null);
const savedDetails = ref(null), savedHeading = ref(null);
const busy = ref(false), error = ref(''), notice = ref('');
const verdict = ref(''), note = ref(''), revisionVerdict = ref(''), revisionNote = ref('');
const selected = computed(() => cases.value.find(item => item.id === selectedId.value));
watch(draft, value => emit('draft-change', Boolean(value)));
function openSavedRecords() {
  if (!savedDetails.value || !savedHeading.value) return;
  savedDetails.value.open = true;
  savedHeading.value.focus({ preventScroll: true });
  savedHeading.value.scrollIntoView({ block: 'nearest' });
}
defineExpose({ openSavedRecords });
const matchesSource = computed(() => {
  const evidence = selected.value?.evidence;
  const source = sourceIdentity(props.source);
  return evidence?.videoSeconds != null && source && Object.keys(source).every(key => source[key] === evidence.source[key]);
});

watch(() => props.owner, async owner => {
  selectedId.value = '';
  cases.value = [];
  draft.value = null;
  if (!owner) return;
  try {
    const saved = await listCases(owner);
    if (props.owner === owner) cases.value = saved;
  } catch (failure) {
    if (props.owner === owner) error.value = failure.message || '读取本地归档失败。';
  }
}, { immediate: true });
watch(selectedId, () => {
  revisionVerdict.value = '';
  revisionNote.value = '';
});

async function run(action) {
  if (busy.value) return;
  busy.value = true;
  error.value = '';
  notice.value = '';
  try { await action(); }
  catch (failure) { error.value = failure.message || '读取或保存本地归档失败。'; }
  finally { busy.value = false; }
}

function refreshList() {
  return run(async () => {
    const owner = props.owner;
    const saved = await listCases(owner);
    if (props.owner === owner) cases.value = saved;
  });
}

function captureFrame() {
  return run(async () => {
    if (!props.canCapture) return;
    const owner = props.owner;
    draft.value = null;
    const evidence = await props.capture();
    if (props.owner !== owner) return;
    if (evidence.originalFrame.length > 24 * 1024 * 1024) throw new Error('单帧证据过大，请选较小的画面。');
    draft.value = evidence;
    verdict.value = '';
    note.value = '';
  });
}

function review(value, text) {
  return { at: new Date().toISOString(), reviewer: props.reviewer, verdict: value, note: text.trim() };
}

function save() {
  return run(async () => {
    const owner = props.owner;
    if (!owner || !draft.value || !verdicts[verdict.value] || !note.value.trim()) return;
    const response = await archiveCase({
      format: 'rail-coupler-case-v1', owner, id: crypto.randomUUID(),
      createdAt: new Date().toISOString(), evidence: draft.value, reviews: [review(verdict.value, note.value)],
    });
    if (props.owner !== owner) return;
    cases.value = [response, ...cases.value];
    selectedId.value = response.id;
    draft.value = null;
    notice.value = '已保存本地核查记录。';
  });
}

function revise() {
  return run(async () => {
    const owner = props.owner;
    const item = selected.value;
    if (!item || !verdicts[revisionVerdict.value] || !revisionNote.value.trim()) return;
    const response = await appendReview(owner, item.id, item.reviews.length, review(revisionVerdict.value, revisionNote.value));
    if (props.owner !== owner) return;
    cases.value = cases.value.map(record => record.id === response.id ? response : record);
    revisionVerdict.value = '';
    revisionNote.value = '';
    notice.value = '已追加复核版本。';
  });
}

function label(item) {
  return `${item.evidence.source.name} · ${verdicts[item.reviews.at(-1).verdict]} · ${new Date(item.createdAt).toLocaleString()}`;
}

function evidenceSummary(evidence) {
  const state = evidence.synchronized;
  const audio = state?.audio.sourceSeconds;
  const acceleration = state?.acceleration.sample;
  return [
    audio == null ? '无对齐录音' : `录音 ${audio.toFixed(3)} s`,
    acceleration ? `三轴 ${[acceleration.x, acceleration.y, acceleration.z].map(n => n.toFixed(2)).join(' / ')} m/s²` : '无对齐加速度样本',
  ].join(' · ');
}
</script>

<style scoped>
.review-panel { display: grid; gap: 8px; min-width: 0; padding: 12px 13px; }
header, .actions { display: flex; align-items: center; justify-content: space-between; gap: 6px; flex-wrap: wrap; }
h2 { margin: 0; font-size: 15px; }
p, span, label, summary, li { overflow-wrap: anywhere; font-size: 12px; line-height: 1.65; color: #a7bbc8; }
p { margin-block: 3px; }
label { display: grid; gap: 4px; margin-block: 6px; }
button:not(.media-action), select, textarea { min-width: 0; padding: 5px 8px; border: 1px solid #45667c; background: #12344f; color: #e3eff7; font: inherit; font-size: 12px; }
button:disabled { opacity: .5; }
summary { cursor: pointer; padding: 4px 0; }
.error { color: #ffc791; }
img { max-width: 100%; max-height: 160px; object-fit: contain; display: block; }
ol { max-height: 170px; overflow: auto; padding-left: 22px; }
</style>
