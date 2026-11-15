<template>
  <svg class="recognition-frame" :viewBox="viewBox.values" preserveAspectRatio="xMidYMid meet"
    role="img" :aria-label="annotated ? '同帧模型检测标注' : '同帧原始画面'">
    <defs><clipPath :id="clipId"><rect :x="viewBox.x" :y="viewBox.y" :width="viewBox.w" :height="viewBox.h" /></clipPath></defs>
    <g :clip-path="`url(#${clipId})`">
      <image :href="frame.image" :width="frame.width" :height="frame.height" />
      <g v-if="annotated">
        <g v-for="box in boxes" :key="box.index" :class="{ selected: box.index === selected }">
          <rect class="target-box" :class="box.label" :x="box.x" :y="box.y"
            :width="box.width" :height="box.height" />
          <text v-if="selected == null || box.index === selected"
            :x="Math.min(box.x + 3, viewBox.x + viewBox.w - labelSize * 4)"
            :y="box.y >= viewBox.y + labelSize + 4 ? box.y - 4 : box.y + labelSize + 4" :font-size="labelSize">
            {{ box.label === 'person' ? '人员' : '汽车' }} {{ box.index + 1 }}
          </text>
        </g>
      </g>
    </g>
  </svg>
</template>

<script setup>
import { computed, useId } from 'vue';

const props = defineProps({
  frame: { type: Object, required: true },
  annotated: Boolean,
  selected: { type: Number, default: null },
  zoom: { type: Number, default: 1 },
});
const clipId = useId();

const boxes = computed(() => props.frame.detections.map((target, index) => {
  const [x, y, right, bottom] = target.box;
  return { index, label: target.label, x, y, width: right - x, height: bottom - y };
}));
const labelSize = computed(() => Math.max(12, props.frame.width / 75 / props.zoom));
const viewBox = computed(() => {
  const { width, height } = props.frame;
  const w = width / props.zoom;
  const h = height / props.zoom;
  const target = boxes.value.find(box => box.index === props.selected);
  const centerX = target ? target.x + target.width / 2 : width / 2;
  const centerY = target ? target.y + target.height / 2 : height / 2;
  const x = Math.max(0, Math.min(centerX - w / 2, width - w));
  const y = Math.max(0, Math.min(centerY - h / 2, height - h));
  return { x, y, w, h, values: [x, y, w, h].join(' ') };
});
</script>

<style scoped>
.recognition-frame { position: absolute; inset: 0; width: 100%; height: 100%; }
.target-box { fill: none; stroke: #76dcff; stroke-width: 2; vector-effect: non-scaling-stroke; }
.target-box.car { stroke: #f5cc8a; }
.selected .target-box { stroke: #fff; stroke-width: 3; }
text { fill: #fff; stroke: #061522; stroke-width: 3; vector-effect: non-scaling-stroke; paint-order: stroke; font-weight: 650; }
</style>
