<template><span class="rail-signal" :data-state="state"><span>{{ railStatusLabels[state] }}</span></span></template>

<script setup>
import { railStatusLabels } from '@/utils/railPresentation'
defineProps({ state: { type: String, required: true } })
</script>
