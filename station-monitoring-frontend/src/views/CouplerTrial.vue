<template>
  <section class="trial-panel" aria-label="现场试用记录">
    <details>
      <summary>现场试用记录</summary>
      <p>仅录入本次真实执行的检查。未执行的项目保留「未执行」。</p>
      <label>试用地点、机位或设备编号<input v-model.trim="site" maxlength="160" /></label>
      <p>记录人 {{ reviewer || '未登录' }} · 当前素材 {{ source?.name || '未选择' }}</p>
      <div v-for="row in checklist" :key="row.id" class="trial-row">
        <label>{{ row.title }}
          <select v-model="row.status">
            <option value="pending">未执行</option>
            <option value="passed">通过</option>
            <option value="failed">不通过</option>
            <option value="blocked">缺少条件</option>
          </select>
        </label>
        <p>{{ row.method }}</p>
        <label v-if="row.status !== 'pending'">记录内容
          <textarea v-model.trim="row.observation" rows="2" maxlength="1000" :placeholder="row.status === 'blocked' ? '写明所缺条件' : '记录素材时间点、实际结果及证据位置'" />
        </label>
      </div>
      <button type="button" :disabled="!canExport" @click="exportTrial">导出本次试用记录</button>
      <p v-if="!canExport">填写试用地点和记录人，并为所有已选择结果的项目填写说明后可导出。</p>
    </details>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue';
import { downloadJson } from '../utils/couplerArchive';
import { sourceIdentity } from '../utils/couplerSync';

const props = defineProps({ source: Object, reviewer: String });
const site = ref('');
const checklist = ref([
  { id: 'connection', title: '服务断线与恢复', method: '在测试环境确认断线提示和恢复后的重新识别结果。' },
  { id: 'visibility', title: '夜间、逆光和遮挡', method: '检查人工能辨认的目标与模型检出的差异，记录对应片段。' },
  { id: 'classification', title: '误报和漏检', method: '按人工确认的样本分别记录误报、漏检和证据不足。' },
  { id: 'ranging', title: '测距误差与失效', method: '引用同机位实测对照档案，检查错分辨率和超出量程时的行为。' },
  { id: 'synchronization', title: '多源同步和缺失数据', method: '用未参与校正的共同事件核对时间差，记录无数据时的提示。' },
  { id: 'endurance', title: '长时间运行', method: '记录测试时长、处理速度、内存和异常次数。' },
  { id: 'review', title: '岗位复核和归档', method: '由负责岗位完成证据核查、追加版本和源视频回看。' },
].map(item => ({ ...item, status: 'pending', observation: '' })));

const canExport = computed(() => site.value && props.reviewer &&
  checklist.value.every(row => row.status === 'pending' || row.observation.trim()));

function exportTrial() {
  if (!canExport.value) return;
  downloadJson({
    format: 'rail-coupler-field-trial-v1', exportedAt: new Date().toISOString(),
    site: site.value, recorder: props.reviewer, source: sourceIdentity(props.source),
    checks: checklist.value.map(({ id, title, status, observation }) => ({
      id, title, status, observation: status === 'pending' ? '' : observation.trim(),
    })),
  }, '作业感知现场试用记录.json');
}
</script>

<style scoped>
.trial-panel { min-width: 0; }
summary { color: #e7f0f6; font-weight: 600; cursor: pointer; }
label { display: grid; gap: 4px; margin-block: 6px; }
p, label { font-size: 12px; line-height: 1.6; color: #a7bbc8; }
.trial-row { padding: 5px 0; border-top: 1px solid #28445c; }
input, select, textarea, button { min-width: 0; padding: 5px 8px; border: 1px solid #45667c; background: #12344f; color: #e3eff7; font: inherit; font-size: 12px; }
button:disabled { opacity: .5; }
</style>
