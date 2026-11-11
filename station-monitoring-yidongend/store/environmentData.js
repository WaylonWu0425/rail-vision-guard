import {defineStore} from 'pinia'
import {computed, ref} from 'vue'

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

function computedM(item) {
    let data = item.detailedData.twentySecondsData.map(item => item.value)
    let max = Math.max(...data)
    let min = Math.min(...data)
    let title = computedTitle(item.title)
    return {
        title: title,
        type: item.title,
        unit: item.unit,
        value: item.value,
        detailedData: {
            oneDayData: item.detailedData.oneDayData.map(computedOneDayData),
            oneWeekData: item.detailedData.oneWeekData.map(computedOneWeekData),
            twentySecondsData: item.detailedData.twentySecondsData.map(computedTwentySecondsData)
        },
        data: [{
            title: '最大' + title,
            value: max.toFixed()
        },
            {
                title: '最小' + title,
                value: min.toFixed()
            },
            {
                title: title,
                value: item.value.toFixed()
            }
        ]
    }
}

function computedOneDayData(item, index) {
    let date = Array.from({length: 24}, (_, index) => `${index}`);
    return {
        Time: date[index],
        Value: item.toFixed(),
    }
}

function computedOneWeekData(item, index) {
    let date = ['一', '二', '三', '四', '五', '六', '日']
    return {
        Time: '星期' + date[index],
        Value: item.toFixed(),
    }
}

function computedTwentySecondsData(item, index) {
    return {
        Time: index + 1,
        Value: item.value.toFixed(),
    }
}

// 设置环境数据
const environmentStore = {
    fetchedData: {
        //  呼吸
        "breath": {
            "detailedData": {
                "oneDayData": [16, 16, 15, 15, 15, 16, 16, 17, 18, 19, 20, 20, 19, 18, 17, 17, 16, 16, 16, 15, 15, 15, 16, 16],
                "oneWeekData": [16, 17, 18, 16, 17, 15, 16],
                "twentySecondsData": [
                    {"title": "temp", "value": 16.1},
                    {"title": "temp", "value": 15.9},
                    {"title": "temp", "value": 16.0},
                    {"title": "temp", "value": 16.2},
                    {"title": "temp", "value": 15.8},
                    {"title": "temp", "value": 16.1},
                    {"title": "temp", "value": 16.3},
                    {"title": "temp", "value": 16.0},
                    {"title": "temp", "value": 15.9},
                    {"title": "temp", "value": 16.1},
                    {"title": "temp", "value": 16.2},
                    {"title": "temp", "value": 15.8},
                    {"title": "temp", "value": 16.0},
                    {"title": "temp", "value": 16.1},
                    {"title": "temp", "value": 16.3},
                    {"title": "temp", "value": 16.0},
                    {"title": "temp", "value": 15.9},
                    {"title": "temp", "value": 16.1},
                    {"title": "temp", "value": 16.2},
                    {"title": "breath", "value": 16.1}
                ]
            },
            "title": "breath",
            "unit": "次/分",
            "value": 16.1
        },
        "temp": {
            "detailedData": {
                "oneDayData": [36.2, 36.1, 36.0, 35.9, 35.8, 35.9, 36.0, 36.2, 36.5, 36.8, 37.0, 37.1, 37.2, 37.1, 37.0, 36.9, 36.8, 36.7, 36.6, 36.5, 36.4, 36.3, 36.2, 36.1],
                "oneWeekData": [36.5, 36.6, 36.7, 36.5, 36.8, 36.4, 36.3],
                "twentySecondsData": [
                    {"title": "temp", "value": 36.8},
                    {"title": "temp", "value": 36.7},
                    {"title": "temp", "value": 36.9},
                    {"title": "temp", "value": 36.8},
                    {"title": "temp", "value": 36.7},
                    {"title": "temp", "value": 36.8},
                    {"title": "temp", "value": 36.9},
                    {"title": "temp", "value": 36.8},
                    {"title": "temp", "value": 36.7},
                    {"title": "temp", "value": 36.8},
                    {"title": "temp", "value": 36.9},
                    {"title": "temp", "value": 36.8},
                    {"title": "temp", "value": 36.7},
                    {"title": "temp", "value": 36.8},
                    {"title": "temp", "value": 36.9},
                    {"title": "temp", "value": 36.8},
                    {"title": "temp", "value": 36.7},
                    {"title": "temp", "value": 36.8},
                    {"title": "temp", "value": 36.9},
                    {"title": "temp", "value": 36.8}
                ]
            },
            "title": "temp",
            "unit": "℃",
            "value": 36.8
        },
        // 烟雾
        "yanwu": {
            "detailedData": {
                "oneDayData": [0, 0, 0, 0, 0, 0, 0.1, 0.1, 0.1, 0.2, 0.3, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1, 0, 0, 0, 0, 0, 0, 0],
                "oneWeekData": [0.1, 0.2, 0.1, 0.3, 0.1, 0.1, 0.1],
                "twentySecondsData": [
                    {"title": "temp", "value": 0},
                    {"title": "temp", "value": 0},
                    {"title": "temp", "value": 0},
                    {"title": "temp", "value": 0.1},
                    {"title": "temp", "value": 0},
                    {"title": "temp", "value": 0},
                    {"title": "temp", "value": 0.1},
                    {"title": "temp", "value": 0},
                    {"title": "temp", "value": 0},
                    {"title": "temp", "value": 0.1},
                    {"title": "temp", "value": 0},
                    {"title": "temp", "value": 0},
                    {"title": "temp", "value": 0.1},
                    {"title": "temp", "value": 0},
                    {"title": "temp", "value": 0},
                    {"title": "temp", "value": 0.1},
                    {"title": "temp", "value": 0},
                    {"title": "temp", "value": 0},
                    {"title": "temp", "value": 0.1},
                    {"title": "yanwu", "value": 0.1}
                ]
            },
            "title": "yanwu",
            "unit": "ppm",
            "value": 0.1
        },
        // 声音
        "shengyin": {
            "detailedData": {
                "oneDayData": [45, 40, 35, 30, 25, 30, 40, 55, 65, 70, 75, 80, 78, 75, 70, 68, 65, 60, 55, 50, 45, 40, 35, 30],
                "oneWeekData": [60, 65, 70, 68, 72, 55, 50],
                "twentySecondsData": [
                    {"title": "temp", "value": 65},
                    {"title": "temp", "value": 63},
                    {"title": "temp", "value": 67},
                    {"title": "temp", "value": 65},
                    {"title": "temp", "value": 64},
                    {"title": "temp", "value": 66},
                    {"title": "temp", "value": 65},
                    {"title": "temp", "value": 67},
                    {"title": "temp", "value": 64},
                    {"title": "temp", "value": 65},
                    {"title": "temp", "value": 66},
                    {"title": "temp", "value": 65},
                    {"title": "temp", "value": 67},
                    {"title": "temp", "value": 64},
                    {"title": "temp", "value": 65},
                    {"title": "temp", "value": 66},
                    {"title": "temp", "value": 65},
                    {"title": "temp", "value": 67},
                    {"title": "temp", "value": 64},
                    {"title": "shengyin", "value": 65}
                ]
            },
            "title": "shengyin",
            "unit": "dB",
            "value": 65
        },
        // 移动
        "move": {
            "detailedData": {
                "oneDayData": [0, 0, 0, 0, 0, 0.2, 0.5, 1.0, 1.5, 1.8, 2.0, 1.9, 1.7, 1.5, 1.3, 1.1, 0.9, 0.7, 0.5, 0.3, 0.2, 0.1, 0, 0],
                "oneWeekData": [1.2, 1.5, 1.3, 1.4, 1.6, 0.8, 0.5],
                "twentySecondsData": [
                    {"title": "temp", "value": 1.5},
                    {"title": "temp", "value": 1.3},
                    {"title": "temp", "value": 1.4},
                    {"title": "temp", "value": 1.6},
                    {"title": "temp", "value": 1.2},
                    {"title": "temp", "value": 1.5},
                    {"title": "temp", "value": 1.3},
                    {"title": "temp", "value": 1.4},
                    {"title": "temp", "value": 1.6},
                    {"title": "temp", "value": 1.2},
                    {"title": "temp", "value": 1.5},
                    {"title": "temp", "value": 1.3},
                    {"title": "temp", "value": 1.4},
                    {"title": "temp", "value": 1.6},
                    {"title": "temp", "value": 1.2},
                    {"title": "temp", "value": 1.5},
                    {"title": "temp", "value": 1.3},
                    {"title": "temp", "value": 1.4},
                    {"title": "temp", "value": 1.6},
                    {"title": "move", "value": 1.5}
                ]
            },
            "title": "move",
            "unit": "m",
            "value": 1.5
        },
        //
        "guang1": {
            "detailedData": {
                "oneDayData": [0, 0, 0, 0, 0, 10, 100, 300, 600, 800, 900, 950, 1000, 980, 850, 700, 500, 300, 100, 50, 10, 0, 0, 0],
                "oneWeekData": [700, 750, 680, 720, 690, 600, 550],
                "twentySecondsData": [
                    {"title": "temp", "value": 750},
                    {"title": "temp", "value": 730},
                    {"title": "temp", "value": 760},
                    {"title": "temp", "value": 740},
                    {"title": "temp", "value": 720},
                    {"title": "temp", "value": 750},
                    {"title": "temp", "value": 730},
                    {"title": "temp", "value": 760},
                    {"title": "temp", "value": 740},
                    {"title": "temp", "value": 720},
                    {"title": "temp", "value": 750},
                    {"title": "temp", "value": 730},
                    {"title": "temp", "value": 760},
                    {"title": "temp", "value": 740},
                    {"title": "temp", "value": 720},
                    {"title": "temp", "value": 750},
                    {"title": "temp", "value": 730},
                    {"title": "temp", "value": 760},
                    {"title": "temp", "value": 740},
                    {"title": "guang1", "value": 750}
                ]
            },
            "title": "guang1",
            "unit": "lux",
            "value": 750
        },
        //  距离
        "distance": {
            "detailedData": {
                "oneDayData": [10, 10, 10, 10, 10, 9, 8, 7, 6, 5, 4, 3, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10],
                "oneWeekData": [5, 4, 6, 5, 3, 7, 8],
                "twentySecondsData": [
                    {"title": "temp", "value": 4.5},
                    {"title": "temp", "value": 4.8},
                    {"title": "temp", "value": 4.3},
                    {"title": "temp", "value": 4.6},
                    {"title": "temp", "value": 4.9},
                    {"title": "temp", "value": 4.4},
                    {"title": "temp", "value": 4.7},
                    {"title": "temp", "value": 4.2},
                    {"title": "temp", "value": 4.5},
                    {"title": "temp", "value": 4.8},
                    {"title": "temp", "value": 4.3},
                    {"title": "temp", "value": 4.6},
                    {"title": "temp", "value": 4.9},
                    {"title": "temp", "value": 4.4},
                    {"title": "temp", "value": 4.7},
                    {"title": "temp", "value": 4.2},
                    {"title": "temp", "value": 4.5},
                    {"title": "temp", "value": 4.8},
                    {"title": "temp", "value": 4.3},
                    {"title": "distance", "value": 4.5}
                ]
            },
            "title": "distance",
            "unit": "m",
            "value": 4.5
        },
        // 湿度
        "humidity": {
            "detailedData": {
                "oneDayData": [70, 75, 80, 85, 90, 85, 80, 75, 70, 65, 60, 55, 50, 55, 60, 65, 70, 75, 80, 85, 90, 85, 80, 75],
                "oneWeekData": [65, 60, 70, 65, 55, 75, 80],
                "twentySecondsData": [
                    {"title": "temp", "value": 62},
                    {"title": "temp", "value": 63},
                    {"title": "temp", "value": 61},
                    {"title": "temp", "value": 64},
                    {"title": "temp", "value": 62},
                    {"title": "temp", "value": 63},
                    {"title": "temp", "value": 61},
                    {"title": "temp", "value": 64},
                    {"title": "temp", "value": 62},
                    {"title": "temp", "value": 63},
                    {"title": "temp", "value": 61},
                    {"title": "temp", "value": 64},
                    {"title": "temp", "value": 62},
                    {"title": "temp", "value": 63},
                    {"title": "temp", "value": 61},
                    {"title": "temp", "value": 64},
                    {"title": "temp", "value": 62},
                    {"title": "temp", "value": 63},
                    {"title": "temp", "value": 61},
                    {"title": "humidity", "value": 62}
                ]
            },
            "title": "humidity",
            "unit": "%",
            "value": 62
        },
        "heart": {
            "detailedData": {
                "oneDayData": [60, 58, 56, 55, 54, 55, 58, 65, 72, 78, 85, 88, 86, 82, 78, 75, 72, 68, 65, 62, 60, 58, 57, 56],
                "oneWeekData": [72, 75, 70, 78, 74, 68, 66],
                "twentySecondsData": [
                    {"title": "temp", "value": 75},
                    {"title": "temp", "value": 73},
                    {"title": "temp", "value": 76},
                    {"title": "temp", "value": 74},
                    {"title": "temp", "value": 72},
                    {"title": "temp", "value": 75},
                    {"title": "temp", "value": 73},
                    {"title": "temp", "value": 76},
                    {"title": "temp", "value": 74},
                    {"title": "temp", "value": 72},
                    {"title": "temp", "value": 75},
                    {"title": "temp", "value": 73},
                    {"title": "temp", "value": 76},
                    {"title": "temp", "value": 74},
                    {"title": "temp", "value": 72},
                    {"title": "temp", "value": 75},
                    {"title": "temp", "value": 73},
                    {"title": "temp", "value": 76},
                    {"title": "temp", "value": 74},
                    {"title": "heart", "value": 75}
                ]
            },
            "title": "heart",
            "unit": "次/分",
            "value": 75
        }
    }
}

export const useEnvironmentStore = defineStore('environment', () => {
    const fetchedData = ref(environmentStore.fetchedData)

    const sensorData = computed(() => {
        return Object.values(fetchedData.value).map(computedM)
    })

    function updateData() {
        Object.values(fetchedData.value).forEach(sensor => {
            let increace = (Math.random() * 2 - 1)
            sensor.value += increace

            sensor.detailedData.twentySecondsData.shift()
            sensor.detailedData.twentySecondsData.push({
                title: sensor.title,
                value: sensor.value + increace
            })
        })
    }

    setInterval(updateData, 1000)

    return {
        sensorData
    }
})