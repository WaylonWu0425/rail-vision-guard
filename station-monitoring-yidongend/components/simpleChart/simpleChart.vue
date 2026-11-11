<template>
	<view class="charts-box">
		<qiun-data-charts :ontouch="true" :chartData="chartData" type="mix" :opts="opts"  />
	</view>
</template>

<script setup>
	import {
		ref,
		defineProps,
		onMounted,
		computed,
		watchEffect
	} from 'vue';
	const props = defineProps(['data'])
	const opts = ref({
		enableScroll: true,
		"color": ["#33BCBB","#FB1374","#FB1374"],
		"canvas2d": true,
		"legend": {
			"show": false,
		},
		"xAxis": {
			"disableGrid": true,
			itemCount: 7,
		},
		"yAxis": {
			data: [{
				min: 0,
				tofix: 1,
			}],
			"gridType": "dash",
			"disabled": false,
			disableGrid: true,
			showTitle: false,
	
		},
		"tooltip": {
			"show": true,
			"trigger": "axis"
		},
		enableMarkLine: true,
		"dataLabel": false,
		"dataPointShape": false
	});
	let yData = Array.from((props.data.data))
	let Ymax = Array.from(props.data.aboveAbnormalData)
	let Ymin = Array.from(props.data.lowAbnormalData)
	const array = Array.from({ length: 11 }, (_, index) => index);
	console.log(yData,Ymax,Ymin,array);
	// 图表数据
	const chartData = ref({
			"categories":  array,
			"series": [{
				name: "心率",
				data: yData,
				type: 'line',
				style: 'curve',
			},{
				name: "高于正常值",
				type:'point',
				data:Ymax,
			},{
				name: "低于正常值",
				type:'point',
				data:Ymin,
			}],
		})
</script>

<style scoped>
	.charts-box {
		width: 100%;
		height: 200px;
	}
</style>