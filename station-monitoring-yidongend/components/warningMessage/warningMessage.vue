<template>
  <view class="warning-message">
    <view class="header">
      <text class="title" :style="{ color: warning.color }">{{ warning.type }}</text>
      <text class="timestamp">{{ warning.timestamp }}</text>
    </view>
    <uv-divider lineColor="#E0E0E0"></uv-divider>
    <view class="content">
      <text class="details">{{ warning.details }}</text>
      <view @click="toggleDetails" class="details-link">
        <text>{{ showDetails ? '隐藏详细数据' : '显示详细数据' }}</text>
      </view>
      <view v-if="showDetails" class="details-content">
        <simpleChart :data="data"></simpleChart> 
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { defineProps,computed } from 'vue';
import UvDivider from "../../uni_modules/uv-divider/components/uv-divider/uv-divider.vue";
import SimpleChart from "../simpleChart/simpleChart.vue";

const props = defineProps({
  warning: {
    type: Object,
    required: true
  },
});

const showDetails = ref(false);
const data = computed(()=>props.warning.abnormalData)
const toggleDetails = () => {
  showDetails.value = !showDetails.value;
};
</script>

<style scoped>
.warning-message {
  padding: 10px;
  margin: 10px 0;
  border-radius: 5px;
  background-color: #f9f9f9;
}
.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}
.title {
  font-weight: bold;
}
.timestamp {
  color: #999;
}
.content {
  font-size: 14px;
}
.details {
  line-height: 1.5;
}
.details-link {
  color: #007bff;
  cursor: pointer;
  margin-top: 10px;
}
.details-content {
  margin-top: 10px;
  background-color: #fff;
}
</style>
