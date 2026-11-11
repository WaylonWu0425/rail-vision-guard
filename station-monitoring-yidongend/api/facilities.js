import request from '@/utils/request';

//获取已购买设备
export async function getBoughtFacilities() {
    return request({
        url: '/clients/bought',
        method: 'GET',
    });
}

// 获取可购买设备列表
export async function getBuyFacilities() {
    return request({
        url: '/clients/buy',
        method: 'GET',
    });
}

// 移除设备
export async function deleteFacilities(data) {
    return request({
        url: '/clients?id=' + data,
        method: 'DELETE',
    });
}

//购买设备
export async function buyFacilities(data) {
    return request({
        url: '/clients/buy_facility',
        method: 'POST',
        data: data
    });
}

//维修设备
export async function repairFacilities(data) {
    return request({
        url: '/clients/repair',
        method: 'POST',
        data: data
    })
}

//获取数据
export async function getSensorsData(clientId) {
    return request({
        url: '/sensors',
        method: 'GET',
        data: {
            clientId
        }
    });
}
