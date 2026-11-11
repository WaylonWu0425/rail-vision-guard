<template>
  <view class="charts-box">
    <qiun-data-charts :key="key" ref="uchart" :animation="false" :ontouch="true" type="mix" :opts="opts" :chartData="chartData" />
  </view>
</template>

<script setup>
import { ref, defineProps, onMounted, computed, watchEffect } from 'vue';
import { useAlertSettingStore } from '@/store/alertSetting.js';
import { useAlertMessageStore } from '../../store/alertMessage';
import { typeContrast, formatDate, addSeconds } from '../../utils/index.js';

const alertMessageStore = useAlertMessageStore();

let key = ref(1);

const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  type: {
    type: String,
    required: true,
    default: ''
  }
});

// 警戒值设置
let alertSettingStore = useAlertSettingStore();
let alertSetting = computed(() => alertSettingStore.alarmData.find((item) => {
  return item.type === '' + props.type;
})?.value);


// 警戒值最大值最小值
let alertMax = computed(() => alertSetting.value?.settings[0]);
let alertMin = computed(() => alertSetting.value?.settings[1]);
// 监测次数
let monitoringFrequency = computed(() => alertSetting.value?.settings[2].value);
// x轴数据
let xData = computed(() => props.data.map(item => item.Time));
// y轴数据
let yData = computed(() => props.data.map(item => item['Value']));

// 最小值最大值
let maxData = computed(() => Math.max(...yData.value));
let minData = computed(() => Math.min(...yData.value));

// 最小值和最大值的位置
let Ymax = computed(() => maxData.value ? yData.value.map(item => item == maxData.value ? item : null) : [null]);
let Xmax = computed(() => minData.value ? yData.value.map(item => item == minData.value ? item : null) : [null]);

// 数据配置
let series = computed(() => ({
  categories: xData.value,
  series: [{
    name: "选中值",
    data: yData.value,
    type: 'line',
    style: 'curve',
  }, {
    name: "最高",
    type: 'point',
    data: Ymax.value,
  }, {
    name: "最低",
    type: 'point',
    data: Xmax.value,
  }]
}));

// 标记线配置
let markLineData = computed(() => [{
  value: alertMax.value.value || null,
  showLabel: alertSetting.value.enabled || false,
  labelText: alertMax.value.label + ':' + alertMax.value.value || null,
  labelOffsetX: 60
}, {
  value: alertMin.value.value || null,
  showLabel: alertSetting.value.enabled || false,
  labelText: alertMin.value.label + ':' + alertMin.value.value || null,
  labelOffsetX: 60
}]);

// 图表配置
const opts = ref({
  enableScroll: false,
  color: ["#33BCBB", "#FB1374", "#FB1374"],
  canvas2d: true,
  legend: {
    show: false,
  },
  xAxis: {
    disableGrid: true,
	fontSize:8
  },
  yAxis: {
    data: [{
      tofix: 1,
    }],
    gridType: "dash",
    disabled: false,
    disableGrid: true,
    showTitle: false,
  },
  tooltip: {
    show: true,
    trigger: "axis"
  },
  extra: {
    markLine: {
      type: 'dash',
      data: markLineData
    }
  },
  enableMarkLine: true,
  dataLabel: false,
  dataPointShape: false,
  update: true,
  animation:false,
  duration:0,
});

// 图表数据
const chartData = ref({});



function updateChartData(newData) {
  // 更新 xData 和 yData
  let newXData,newYData
  newXData = newData.map(item => item.Time);
  newYData = newData.map(item => item['Value']);
  // 重新计算 series
  const newSeries = {
    categories: newXData,
    series: [{
      name: "选中值",
      data: newYData,
      type: 'line',
      style: 'curve',
    }, {
      name: "最高",
      type: 'point',
      data: newYData.map(item => item == Math.max(...newYData) ? item : null),
    }, {
      name: "最低",
      type: 'point',
      data: newYData.map(item => item == Math.min(...newYData) ? item : null),
    }]
  };

  // 深拷贝并整体赋值
  chartData.value = JSON.parse(JSON.stringify(newSeries));
}
updateChartData(props.data)

onMounted(() => {
  watchEffect(() => {
    updateChartData(props.data)
  });
});
</script>

<style scoped>
.charts-box {
  width: 100%;
  height: 200px;
}
</style>
