<template>
  <section class="rail-review" aria-label="核查步骤">
    <div class="rail-review-heading">
      <RailIcon name="review" />
      <strong>核查线路</strong>
      <span v-if="recordId != null">事件 #{{ recordId }}</span>
    </div>
    <ol class="rail-review-line">
      <li v-for="(label, index) in steps" :key="label" :data-step="index < step ? 'done' : index === step ? 'current' : 'next'" :aria-current="index === step ? 'step' : undefined">
        <span class="rail-review-node" aria-hidden="true">{{ index < step ? '✓' : index + 1 }}</span>
        <span>{{ label }}</span>
        <span class="rail-sr-only">{{ index < step ? '已完成' : index === step ? '当前步骤' : '未开始' }}</span>
      </li>
    </ol>
  </section>
</template>

<script setup>
import RailIcon from './RailIcon.vue'
defineProps({ step: { type: Number, required: true }, recordId: [String, Number] })
const steps = ['选择记录', '确认处置', '保存结果']
</script>
