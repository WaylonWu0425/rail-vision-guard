<template>
	<view class="charts-box">
		<qiun-data-charts :ontouch="true" type="mix" :opts="opts" :chartData="chartData" />
	</view>
</template>

<script setup>
	import {
		ref,
		defineProps,
		onMounted,
		computed
	} from 'vue';


	let props = defineProps(['data'])
	//x轴数据
	let xData = computed(() => Array.from(props.data).map(item => {
		return item.Time
	}))
	//y轴数据
	let yData = computed(() => Array.from(props.data).map(item => item['Value']))
	//最小值最大值
	let maxData = computed(() => Math.max(...yData.value))
	let minData = computed(() => Math.min(...yData.value))

	//最小值和最大值的位置
	let Ymax = computed(() => maxData.value ? yData.value.map(item => {
		if (item == maxData.value)
			return item
		return null
	}) : [null])

	let Xmax = computed(() => minData.value ? yData.value.map(item => {
		if (item == minData.value)
			return item
		return null
	}) : [null])

	// 图表配置
	const opts = ref({
		enableScroll: true,
		"color": ["#33BCBB", "#FB1374", "#FB1374"],
		"canvas2d": true,
		"legend": {
			"show": false,
		},

		"xAxis": {
			"disableGrid": true,
			itemCount: 9,
		},
		"yAxis": {
			splitNumber:3,
			showTitle: false,
			data: [{
				min: 0,
				tofix: 1,
			}],
		},
		"tooltip": {
			"show": true,
			"trigger": "axis",
			
		},
		extra: {
			markLine: {
				type: 'dash',
				data: [{
					value: 60,
					showLabel: true,
					labelText: "偏低"
				}, {
					value: 130,
					showLabel: true,
					labelText: "偏高"
				}]
			}
		},
		enableMarkLine: true,
		"dataLabel": true,
		"dataPointShape": false
	});

	const chartData = ref({
		"categories": xData.value,
		"series": [{
			name: "当前值",
			data: yData.value,
			type: 'column',
		}, {
			name: "最高",
			type: 'point',
			data: Ymax.value,
		}, {
			name: "最低",
			type: 'point',
			data: Xmax.value,
		}],
	})

	// 图表数据
</script>

<style scoped>
	.charts-box {
		width: 100%;
		height: 200px;
	}
</style>