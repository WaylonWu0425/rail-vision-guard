// src/store/alertMessage.js
import {defineStore} from 'pinia';
import {ref} from 'vue';

export const useAlertMessageStore = defineStore('alertMessage', () => {
    const warnings = ref([
        {
            id: 'alert_001',
            type: '心率异常',
            timestamp: '2026-01-24 08:15:30',
            details: '08:10:00-08:15:30 心率持续偏高，最高达128次/分，超过预设阈值(120次/分)',
            color: '#FF6B6B',
            level: 'urgent',
            status: 'unread',
            abnormalData: {
                data: [72, 75, 82, 95, 108, 118, 128, 124, 112, 98, 85],
                lowAbnormalData: [null, null, null, null, null, null, null, null, null, null, null],
                aboveAbnormalData: [null, null, null, null, 108, 118, 128, 124, 112, null, null]
            }
        },
        {
            id: 'alert_002',
            type: '呼吸频率异常',
            timestamp: '2026-01-24 07:40:15',
            details: '07:35:00-07:40:15 呼吸频率过低，持续低于12次/分，最低达9次/分',
            color: '#FF9F43',
            level: 'warning',
            status: 'read',
            abnormalData: {
                data: [15, 14, 13, 11, 10, 9, 10, 11, 12, 13, 14],
                lowAbnormalData: [null, null, null, 11, 10, 9, 10, 11, 12, null, null],
                aboveAbnormalData: [null, null, null, null, null, null, null, null, null, null, null]
            }
        },
        {
            id: 'alert_003',
            type: '体温异常',
            timestamp: '2026-01-23 22:30:45',
            details: '22:25:00-22:30:45 体温持续升高，最高达37.8°C，超过正常范围',
            color: '#FF6B6B',
            level: 'urgent',
            status: 'unread',
            abnormalData: {
                data: [36.5, 36.6, 36.8, 37.0, 37.2, 37.5, 37.8, 37.7, 37.5, 37.2, 37.0],
                lowAbnormalData: [null, null, null, null, null, null, null, null, null, null, null],
                aboveAbnormalData: [null, null, null, null, 37.2, 37.5, 37.8, 37.7, 37.5, null, null]
            }
        },
        {
            id: 'alert_004',
            type: '血氧饱和度异常',
            timestamp: '2026-01-23 14:20:18',
            details: '14:15:00-14:20:18 血氧饱和度下降，最低降至89%，需要关注',
            color: '#54A0FF',
            level: 'info',
            status: 'resolved',
            abnormalData: {
                data: [95, 94, 93, 92, 91, 89, 90, 91, 92, 93, 94],
                lowAbnormalData: [null, null, null, null, 91, 89, 90, 91, 92, null, null],
                aboveAbnormalData: [null, null, null, null, null, null, null, null, null, null, null]
            }
        }
    ]);

    function addWarning(warning) {
        warnings.value.push(warning);
    }

    function updateWarning(index, updatedWarning) {
        warnings.value[index] = updatedWarning;
    }

    function removeWarning(index) {
        warnings.value.splice(index, 1);
    }

    return {
        warnings,
        addWarning,
        updateWarning,
        removeWarning
    };
});