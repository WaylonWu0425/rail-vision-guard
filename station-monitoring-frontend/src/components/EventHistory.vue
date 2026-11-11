<template>
  <details class="event-history">
    <summary>核查记录 <span>{{ validTime(event.dealTime) ? '含处理时间' : '记录不完整' }}</span></summary>
    <ol>
      <li v-if="validTime(event.createTime)"><time>{{ formatTime(event.createTime) }}</time><strong>事件发生</strong></li>
      <li v-if="validTime(event.dealTime)"><time>{{ formatTime(event.dealTime) }}</time><strong>{{ alarmRailState(event.dealFlag) === 'done' ? '处理结果已保存' : '记录处理时间' }}</strong><span>处理人 {{ event.dealUserName || (event.dealUserId != null ? '#' + event.dealUserId : '未记录') }}</span></li>
    </ol>
    <p v-if="!validTime(event.createTime) && !validTime(event.dealTime)" class="context-empty">暂无可展示的核查时间记录。</p>
    <p v-else-if="!validTime(event.dealTime)" class="context-empty">{{ alarmRailState(event.dealFlag) === 'done' ? '当前为已处理，处理时间未记录。' : '暂无带时间的核查动作记录。' }}</p>
    <p class="history-note">当前状态 <RailSignal :state="alarmRailState(event.dealFlag)" /> · 接口未提供完整操作日志</p>
  </details>
</template>
<script setup>
import { alarmRailState } from '@/utils/railPresentation'
import RailSignal from './RailSignal.vue'
defineProps({ event: { type: Object, required: true } })
const validTime = value => value != null && value !== '' && !Number.isNaN(new Date(value).getTime())
const formatTime = value => new Date(value).toLocaleString('zh-CN', { hour12:false })
</script>
