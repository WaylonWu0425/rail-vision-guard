import * as echarts from 'echarts'
const axis = {
  axisLine: { lineStyle: { color: '#527fa3' } },
  axisLabel: { color: '#a8c9e4' },
  splitLine: { lineStyle: { color: '#254968' } },
}
echarts.registerTheme('rail-workspace', {
  color: ['#70d7ff','#83baa4','#d9b77f','#ad939c','#899eae'],
  backgroundColor: 'transparent',
  textStyle: { color: '#edf7ff' },
  title: { textStyle: { color:'#edf7ff' }, subtextStyle:{color:'#a8c9e4'} },
  legend: { textStyle:{color:'#cfe5f5'} },
  tooltip: { backgroundColor:'#0b2a49',borderColor:'#527fa3',textStyle:{color:'#edf7ff'} },
  categoryAxis: axis,
  valueAxis: axis,
})
