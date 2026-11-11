<template><span class="event-priority" :data-level="value">风险 · {{ label }}</span></template>
<script setup>
import { computed } from 'vue'
const props = defineProps({ level: { default: null } })
const value = computed(() => props.level != null && props.level !== '' && ['0','1','2'].includes(String(props.level)) ? String(props.level) : 'unknown')
const label = computed(() => ({'0':'轻度','1':'中度','2':'重度'})[value.value] || '未记录')
</script>
<style scoped>
.event-priority { display:inline-flex;align-items:center;gap:4px;padding:2px 5px;border:1px solid var(--instrument-edge-lit);border-radius:3px;color:var(--instrument-text);font-size:11px;line-height:1.3;white-space:nowrap; }
.event-priority[data-level="1"] { color:#edc388;border-color:#816845; }
.event-priority[data-level="2"] { color:#f1a39d;border-color:#92615e; }
.event-priority[data-level="unknown"] { color:#b1c0c8;border-style:dashed; }
</style>
