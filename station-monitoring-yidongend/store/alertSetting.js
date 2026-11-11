import {
	defineStore
} from 'pinia';
import {
	computed,
	ref
} from 'vue';
import { getalert } from '../api/alert';
export const useAlertSettingStore = defineStore('alertSetting', () => {
	

	let fetchedData = ref([])
	function computedTitle(title) {
	  switch (title) {
	    case 'breath':
	      return '呼吸'
	    case 'temp':
	      return '温度'
	    case 'yanwu':
	      return '烟雾'
	    case 'humidity':
	      return '湿度'
	    case 'heart':
	      return '心跳'
	    case 'distance':
	      return '距离'
	    case 'guang1':
	      return '光照'
	    case 'move':
	      return '移动'
	    case 'shengyin':
	      return '声音'
	    default:
	      return title
	  }
	}
	let settingsLabel = {
	  "breath": ["呼吸频率过快", "呼吸频率过慢", "次/分"],
	  "yanwu": ["烟雾浓度过高", "烟雾浓度过低", "ppm"],
	  "shengyin": ["声音过大", "声音过小", "dB"],
	  "move": ["移动距离过大", "移动距离过小", "m"],
	  "guang1": ["光照过强", "光照过弱", "lux"],
	  "distance": ["距离过近", "距离过远", "m"],
	  "humidity": ["湿度过高", "湿度过低", "%"],
	  "heart": ["心跳过快", "心跳过慢", "次/分"],
	  "temp": ["温度过高", "温度过低", "℃"],
	}
	function computedAlarmData(item) {
	  return {
		label: computedTitle(item.type),
		type: item.type,
		value: {
		  enabled: item.enable,
		  settings: [{
			label: settingsLabel[item.type][1],
			value: item.minValue,
			unit: settingsLabel[item.type][2]
		  }, {
			label: settingsLabel[item.type][0],
			value: item.maxValue,
			unit: settingsLabel[item.type][2]
		  }, {
			label: "20s内异常数",
			value: item.alarmThreshold,
			unit: '次'
		  }],
		  warningPeriod: item.warningPeriod,
		}
	  }
	}

	// 获取报警配置
	let fetchData = async (data)=>{
		try{
			let res = await getalert(data)
			fetchedData.value = res.data
		}catch(err){
			uni.showToast({
				title:'获取报警配置失败',
				icon:'error'
			})
			console.error(err)
		}
	}
	
	let alarmData = computed(()=>{
		return fetchedData.value.map(computedAlarmData)
	})
	return {
		alarmData,
		fetchData
	};
}, {
	unistorage: true
});