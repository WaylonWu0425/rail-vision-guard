<template>
  <fieldset>
    <legend>{{ title }}</legend>
    <div class="actions">
      <label class="picker">选择{{ title }}文件
        <input type="file" :accept="accept" @change="pick" />
      </label>
      <button v-if="track.file" type="button" @click="$emit('remove')">移除{{ title }}</button>
    </div>
    <p class="filename">{{ track.file?.name || '未导入' }}</p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="!track.file && hint">{{ hint }}</p>
    <template v-if="track.file">
      <slot />
      <p v-if="range">源记录范围 {{ range[0].toFixed(3) }}–{{ range[1].toFixed(3) }} s</p>
      <label>采集位置<input v-model.trim="track.position" maxlength="120" placeholder="设备编号、安装位置及方向" /></label>
      <label>同步依据<input v-model.trim="track.reference" maxlength="240" placeholder="例如视频和记录共同出现的采集标记" /></label>
      <label v-if="acceleration">加速度口径
        <select v-model="track.kind">
          <option value="unknown">未注明</option>
          <option value="linear">线性加速度</option>
          <option value="includes_gravity">含重力</option>
        </select>
      </label>
      <div class="anchors">
        <label>同步点 1 · 视频秒<input v-model.number="track.first.video" type="number" min="0" step="any" /></label>
        <label>同步点 1 · 源记录秒<input v-model.number="track.first.source" type="number" min="0" step="any" /></label>
        <label class="check"><input v-model="track.useSecond" type="checkbox" />用第二个同步点校正时钟漂移</label>
        <template v-if="track.useSecond">
          <label>同步点 2 · 视频秒<input v-model.number="track.second.video" type="number" min="0" step="any" /></label>
          <label>同步点 2 · 源记录秒<input v-model.number="track.second.source" type="number" min="0" step="any" /></label>
        </template>
      </div>
      <label class="check"><input v-model="track.sameOperation" type="checkbox" />已核对该记录和视频来自同一次作业</label>
      <p v-if="alignment?.error" class="error">{{ alignment.error }}</p>
      <p v-else-if="alignment">已配置{{ alignment.method === 'two_anchors' ? '双点对齐，证据限于两同步点之间' : '单点对齐，时钟漂移未校正' }}。</p>
    </template>
  </fieldset>
</template>

<script setup>
defineProps({
  title: String, accept: String, hint: String, track: Object,
  error: String, range: Array, alignment: Object, acceleration: Boolean,
});
const emit = defineEmits(['select', 'remove']);
function pick(event) {
  const file = event.target.files?.[0];
  event.target.value = '';
  if (file) emit('select', file);
}
</script>

<style scoped>
fieldset { min-width: 0; margin: 0; padding: 10px; border: 1px solid #28445c; }
legend { padding: 0 4px; font-weight: 600; color: #e7f0f6; }
p, label { font-size: 12px; color: #a7bbc8; }
label { display: grid; gap: 4px; margin-block: 7px; }
label.check, .actions { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
.picker { position: relative; cursor: pointer; margin: 0; }
.picker input { position: absolute; opacity: 0; width: 1px; height: 1px; }
.picker:focus-within { outline: 2px solid #9cddf2; outline-offset: 2px; }
button, input:not([type=checkbox]):not([type=file]), select, .picker { min-width: 0; padding: 5px 8px; border: 1px solid #45667c; background: #12344f; color: #e3eff7; font: inherit; font-size: 12px; }
.anchors { display: grid; grid-template-columns: 1fr 1fr; gap: 0 8px; }
.anchors .check { grid-column: 1 / -1; }
.filename { overflow-wrap: anywhere; }
.error { color: #ffc791; }
</style>
