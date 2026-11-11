import http from "../index.js"


// 获取设备运行统计数据
export const getDeviceRunningStats = (startTime, endTime) => {
    return http({
        url: '/Statistics/deviceStats',
        method: 'get',
        params: {
            startTime,
            endTime
        }
    })
}

// 获取报警统计数据
export const getAlarmStats = (startTime, endTime) => {
    return http({
        url: '/Statistics/alarmStats',
        method: 'get',
        params: {
            startTime,
            endTime
        }
    })
}

// 获取任务统计数据
export const getTaskStats = (startTime, endTime) => {
    return http({
        url: '/Statistics/taskStats',
        method: 'get',
        params: {
            startTime,
            endTime
        }
    })
}

// 导出统计报表为PDF
export const exportStatisticsPDF = (startTime, endTime, reportType) => {
    return http({
        url: '/Statistics/exportPDF',
        method: 'get',
        params: {
            startTime,
            endTime,
            reportType
        },
        responseType: 'blob' // 指定响应类型为二进制数据
    })
}

// 导出统计报表为Excel
export const exportStatisticsExcel = (startTime, endTime, reportType) => {
    return http({
        url: '/Statistics/exportExcel',
        method: 'get',
        params: {
            startTime,
            endTime,
            reportType
        },
        responseType: 'blob' // 指定响应类型为二进制数据
    })
}

