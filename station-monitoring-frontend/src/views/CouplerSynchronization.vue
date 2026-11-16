<template>
  <section class="sync-panel" aria-label="多源时间对齐">
    <header><h2>多源时间对齐</h2><span>{{ videoDuration ? videoSeconds.toFixed(3) + ' s' : '等待视频' }}</span></header>
    <p v-if="!videoDuration">打开作业视频后，可导入同一次作业的外部录音和加速度 CSV。</p>
    <template v-else>
      <div v-if="!hideSeek" class="timeline">
        <input aria-label="定位视频时间" type="range" min="0" :max="videoDuration" step="any"
          :value="videoSeconds" :disabled="!canSeek" @change="$emit('seek', Number($event.target.value))" />
        <span>视频 {{ videoDuration.toFixed(2) }} s</span>
      </div>
      <dl>
        <div><dt>外部录音</dt><dd>{{ audioTime == null ? audio.file ? '当前时刻无已对齐录音' : '未导入' : audioTime.toFixed(3) + ' s · 可试听' }}</dd></div>
        <div><dt>三轴加速度</dt><dd>{{ sample ? formatAcceleration(sample) : sensor.file ? '当前时刻无可用样本' : '未导入' }}</dd></div>
      </dl>
      <div class="listen-row" v-if="audioUrl">
        <audio ref="audioElement" :key="audioUrl" :src="audioUrl" controls preload="metadata"
          @loadedmetadata="loadAudioDuration" @error="handleAudioError" />
        <button type="button" :disabled="audioTime == null" @click="listen">试听此时刻的录音</button>
      </div>
      <details>
        <summary>导入记录与设置同步点</summary>
        <CouplerSyncTrack title="录音" accept="audio/*,.wav,.m4a,.mp3,.ogg,.flac" :track="audio"
          :error="audioError" :range="audioRange" :alignment="audioAlignment" @select="selectAudio" @remove="removeAudio" />
        <CouplerSyncTrack title="加速度" accept=".csv,text/csv" :track="sensor" :error="sensorError"
          :range="sensorRange" :alignment="sensorAlignment" acceleration @select="selectSensor" @remove="removeSensor">
          <p v-if="samples.length">{{ samples.length }} 条 · {{ sensorKind }}</p>
        </CouplerSyncTrack>
        <details>
          <summary>CSV 格式与对齐规则</summary>
          <p>首行为 <code>{{ SENSOR_HEADER }}</code>，时间单位秒，三轴单位 m/s²，按时间递增。页面显示与视频时刻相差不超过 0.25 s 的最近样本。</p>
        </details>
      </details>
    </template>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue';
import CouplerSyncTrack from './CouplerSyncTrack.vue';
import { SENSOR_HEADER, accelerationAt, alignedTime, createAlignment, parseAcceleration, sourceIdentity } from '../utils/couplerSync';

const props = defineProps({ videoDuration: Number, videoSeconds: Number, canSeek: Boolean, hideSeek: Boolean });
defineEmits(['seek']);
function emptyTrack() {
  return {
    file: null, position: '', reference: '', kind: 'unknown', sameOperation: false,
    first: { video: null, source: null }, second: { video: null, source: null }, useSecond: false,
  };
}
const audio = ref(emptyTrack()), sensor = ref(emptyTrack());
const audioUrl = ref(''), audioDuration = ref(0), audioElement = ref(null), audioError = ref('');
const samples = ref([]), sensorError = ref('');
let sensorLoad = 0;
const audioRange = computed(() => audioDuration.value > 0 ? [0, audioDuration.value] : null);
const sensorRange = computed(() => samples.value.length ? [samples.value[0].time, samples.value.at(-1).time] : null);
const audioAlignment = computed(() => createAlignment(audio.value, audioRange.value, props.videoDuration));
const sensorAlignment = computed(() => createAlignment(sensor.value, sensorRange.value, props.videoDuration));
const audioTime = computed(() => alignedTime(props.videoSeconds, audioAlignment.value));
const sensorTime = computed(() => alignedTime(props.videoSeconds, sensorAlignment.value));
const sample = computed(() => sensorTime.value == null ? null : accelerationAt(samples.value, sensorTime.value, sensorAlignment.value));
const sensorKind = computed(() => ({
  unknown: '是否含重力未知', linear: '线性加速度', includes_gravity: '含重力',
}[sensor.value.kind]));

function snapshotAt(videoTime) {
  const audioTrack = audioAlignment.value;
  const accelerationTrack = sensorAlignment.value;
  const audioSeconds = alignedTime(videoTime, audioTrack);
  const accelerationSeconds = alignedTime(videoTime, accelerationTrack);
  return {
    audio: {
      source: sourceIdentity(audio.value.file),
      alignment: audioTrack && !audioTrack.error ? audioTrack : null,
      sourceSeconds: audioSeconds,
    },
    acceleration: {
      source: sourceIdentity(sensor.value.file),
      kind: sensor.value.kind,
      alignment: accelerationTrack && !accelerationTrack.error ? accelerationTrack : null,
      sample: accelerationSeconds == null ? null : accelerationAt(samples.value, accelerationSeconds, accelerationTrack),
    },
  };
}

defineExpose({ snapshotAt });

function formatAcceleration(point) {
  const values = [point.x, point.y, point.z].map(n => n.toFixed(2)).join(' / ');
  return `${values} m/s² · 记录 ${point.time.toFixed(3)} s · Δ ${point.videoDelta.toFixed(3)} s`;
}

function removeAudio() {
  audioElement.value?.pause();
  if (audioUrl.value) URL.revokeObjectURL(audioUrl.value);
  audioUrl.value = '';
  audioDuration.value = 0;
  audioError.value = '';
  audio.value = emptyTrack();
}

function selectAudio(file) {
  removeAudio();
  if (file.size === 0 || file.size > 100 * 1024 * 1024) {
    audioError.value = '录音文件为空或超过 100 MB。';
    return;
  }
  audio.value.file = file;
  audioUrl.value = URL.createObjectURL(file);
}

function loadAudioDuration(event) {
  if (event.target !== audioElement.value) return;
  const duration = event.target.duration;
  audioDuration.value = Number.isFinite(duration) && duration > 0 ? duration : 0;
  if (!audioDuration.value) audioError.value = '无法读取有效录音时长。';
}

function handleAudioError(event) {
  if (event.target !== audioElement.value) return;
  audioDuration.value = 0;
  audioError.value = '浏览器无法解码此录音，请尝试 WAV 或 MP3。';
}

async function listen() {
  const element = audioElement.value;
  if (!element || audioTime.value == null) return;
  try {
    element.currentTime = audioTime.value;
    await element.play();
  } catch (error) {
    if (audioElement.value === element && error.name !== 'AbortError') audioError.value = '录音试听失败，请检查文件。';
  }
}

function removeSensor() {
  sensorLoad += 1;
  sensorError.value = '';
  sensor.value = emptyTrack();
  samples.value = [];
}

async function selectSensor(file) {
  removeSensor();
  const generation = sensorLoad;
  if (file.size === 0 || file.size > 16 * 1024 * 1024) {
    sensorError.value = 'CSV 文件为空或超过 16 MB。';
    return;
  }
  try {
    const parsed = parseAcceleration(await file.text());
    if (generation !== sensorLoad) return;
    samples.value = parsed;
    sensor.value.file = file;
  } catch (error) {
    if (generation === sensorLoad) sensorError.value = error.message;
  }
}

onBeforeUnmount(() => {
  removeAudio();
  removeSensor();
});
</script>

<style scoped>
.sync-panel { display: grid; gap: 10px; min-width: 0; }
header, .timeline { display: flex; gap: 8px; align-items: center; justify-content: space-between; }
h2 { margin: 0; font-size: 15px; }
p, span, dt, dd, summary { color: #a7bbc8; font-size: 12px; line-height: 1.6; }
p, dl, dd { margin: 0; }
dl > div { display: flex; justify-content: space-between; gap: 8px; margin-block: 4px; }
dd { text-align: right; }
.timeline input { flex: 1; min-width: 0; }
audio { display: block; width: 100%; margin-block: 6px; }
button { padding: 5px 8px; border: 1px solid #45667c; background: #12344f; color: #e3eff7; font: inherit; font-size: 12px; }
button:disabled { opacity: .5; }
</style>
