<template>
  <view>
    <view class="header">
      <view class="left">
        <image :src='`../../static/${sensor.type}.png`' mode="heightFix"></image>
        <text>{{ sensor.title }}</text>
      </view>
      <view class="right">
        <text>{{ sensor.unit }}</text>
      </view>
    </view>
    <uv-grid :border="false">
      <uv-grid-item v-for="(dataItem, index) in sensor.data" :key="index">
        <text class="grid-title">{{ dataItem.title }}</text>
        <text class="grid-value">{{ dataItem.value }}</text>
      </uv-grid-item>
    </uv-grid>
    <uv-divider :hairline="false"></uv-divider>
	<view class="subsection">
		<uv-subsection :list="list" :current="current" @change="change"></uv-subsection>
	</view>
	<chartHeartPreview v-if="current===0" :type="sensor.type" :data="twentySecondsData"></chartHeartPreview>
	<chartHeartPreview v-if="current===1" :type="sensor.type" :data="oneDayData"></chartHeartPreview>
	<histogram v-if="current===2" :type="sensor.type" :data="oneWeekData"></histogram>
  </view>
</template>

<script setup>
import { computed, defineProps,ref } from 'vue';
//分段器
	let list=ref(['近20s','天','周'])
	let current = ref(0)
	//选择处理
	function change(index){
		current.value = index
	}
// 定义传入的props
const props = defineProps({
  sensor: {
    type: Object,
    required: true
  }
});

	
let twentySecondsData = computed(()=>{
	return props.sensor.detailedData.twentySecondsData
})
let oneDayData = computed(()=>{
	return props.sensor.detailedData.oneDayData
})
let oneWeekData = computed(()=>{
	return props.sensor.detailedData.oneWeekData
})
</script>

<style scoped>
.header {
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
}
.left {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  font-weight: 800;
}
image {
    height: 24px;
    margin-right: 2px;
}
.right {
  font-size: 12px;
  color: #999;
}
.grid-title {
  font-size: 14px;
  color: #666;
}
.grid-value {
  font-size: 24px;
  color: #333;
  margin-top: 5px;
}
</style>
