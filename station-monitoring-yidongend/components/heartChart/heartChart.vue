<template>
	<view>
		<view class="header">
			<view class="left">
				<image src="../../static/心率.png" mode="heightFix"></image>
				<text>心率BPM</text>
			</view>
			<view class="right">
				<text>次/分钟</text>
			</view>
		</view>
		<uv-grid :border="false">
			<uv-grid-item v-for="(item,index) in baseList" :key="index">
				<text class="grid-title">{{item.title}}</text>
				<text class="grid-value">{{item.value}}</text>
			</uv-grid-item>
		</uv-grid>
		<uv-divider :hairline="false"></uv-divider>
		<view class="subsection">
			<uv-subsection :list="list" :current="current" @change="change"></uv-subsection>
		</view>
		<chartHeartPreview v-if="current===0" type="heart" :data="heartRateData"></chartHeartPreview>
		<chartHeartPreview v-if="current===1" type="heart" :data="data"></chartHeartPreview>
		<histogram v-if="current===2" type="heart" :data="heartRateWeekData"></histogram>
	</view>
</template>

<script setup>
	import {
		computed,
		onMounted,
		ref
	} from 'vue';
	//分段器
	let list=ref(['近10分钟','天','周'])
	let current = ref(0)
	//选择处理
	function change(index){
		current.value = index
	}
	//一周的数据
	const heartRateWeekData = [
	  { Time: '5-10', Value: 70 },
	  { Time: '5-11', Value: 72 },
	  { Time: '5-12', Value: 68 },
	  { Time: '5-13', Value: 75 },
	  { Time: '5-14', Value: 78 },
	  { Time: '5-15', Value: 73 },
	  { Time: '5-16', Value: 69 }
	];

	//10分钟数据
	const heartRateData = [
	  { Time: "12:00", Value: 34 },
	  { Time: "12:01", Value: 75 },
	  { Time: "12:02", Value: 80 },
	  { Time: "12:03", Value: 78 },
	  { Time: "12:04", Value: 130 },
	  { Time: "12:05", Value: 74 },
	  { Time: "12:06", Value: 73 },
	  { Time: "12:07", Value: 72 },
	  { Time: "12:08", Value: 70 },
	  { Time: "12:09", Value: 23 },
	  { Time: "12:10", Value: 72 }
	];


	//一天数据处理
	let data = ref([
	    { "Time": 1, "Value": 105 },
	    { "Time": 2, "Value": 78 },
	    { "Time": 3, "Value": 90 },
	    { "Time": 4, "Value": 115 },
	    { "Time": 5, "Value": 107 },
	    { "Time": 6, "Value": 50 },
	    { "Time": 7, "Value": 89 },
	    { "Time": 8, "Value": 67 },
	    { "Time": 9, "Value": 68 },
	    { "Time": 10, "Value": 78 },
	    { "Time": 11, "Value": 73 },
	    { "Time": 12, "Value": 99 },
	    { "Time": 13, "Value": 85 },
	    { "Time": 14, "Value": 72 },
	    { "Time": 15, "Value": 79 },
	    { "Time": 16, "Value": 77 },
	    { "Time": 17, "Value": 100 },
	    { "Time": 18, "Value": 66 },
	    { "Time": 19, "Value": 76 },
	    { "Time": 20, "Value": 53 },
	    { "Time": 21, "Value": 19 },
	    { "Time": 22, "Value": 83 },
	    { "Time": 23, "Value": 87 },
	    { "Time": 24, "Value": 55 }
	]);
	let heartRateValue = computed(()=>Array.from(data.value).map(item=>item['Value']))
	
	
	let maxData = computed(()=>Math.max(...heartRateValue.value))
	let minData = computed(()=>Math.min(...heartRateValue.value))
	let currentData = computed(()=>data.value[data.value.length-1])
	let baseList = ref([{
						value: currentData.value["Value"].toFixed(),
						title: '静息心率'
					}, {
						value: maxData.value.toFixed(),
						title: '最高'
					}, {
						value: minData.value.toFixed(),
						title: '最低'
					}]) 

</script>

<style lang="scss">
  /* 您可以添加自定义的scss样式 */
  .grid-title {
    font-size: 14px;
    color: #666;
	
  }
  .grid-value {
    font-size: 24px;
    color: #333;
    margin-top: 5px;
  }
  .subsection{
	  margin: 10px 0;
  }
  
  .header{
	  margin-bottom: 10px;
	  display: flex;
	  justify-content: space-between;
	  .left{
		  image{
			  height: 24px;
			  margin-right: 2px;
		  }
		  display: flex;
		  justify-content: flex-start;
		  align-items:flex-start;
		  font-weight: 800;
	  }
	  .right{
		  font-size: 12px;
		  color: #999;
	  }
  }
  
  

</style>
