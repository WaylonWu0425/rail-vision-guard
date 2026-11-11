import {
    defineStore
} from 'pinia';
import {
    computed,
    ref
} from 'vue';
import {getBoughtFacilities, deleteFacilities, buyFacilities, getBuyFacilities} from '../api/facilities';

export const useFacilitiesStore = defineStore('facilities', () => {
    // 初始值改为空数组，而不是 null
    let bought_facilities = ref([])  // 改为空数组
    let buy_facilities = ref([])      // 改为空数组
    let currentFacility = ref(null)

    // 设置当前设备
    function setCurrentFacility(data) {
        currentFacility.value = data
    }

    // 获取已购买设备列表
    async function fetchFacilities() {
        try {
            let res = await getBoughtFacilities()
            // 使用数组赋值，而不是直接替换
            bought_facilities.value = Array.isArray(res.data) ? res.data : []
            console.log('已购买设备更新:', bought_facilities.value)
        } catch (err) {
            console.error(err);
            bought_facilities.value = []
            uni.showToast({
                icon: "error",
                title: "获取已购买设备列表失败"
            })
        }
    }

    // 获取可购买设备列表
    async function fetchBuyFacilities() {
        try {
            let res = await getBuyFacilities()
            // 使用数组赋值，而不是直接替换
            buy_facilities.value = Array.isArray(res.data) ? res.data : []
            console.log('可购买设备更新:', buy_facilities.value)
            return buy_facilities.value
        } catch (err) {
            console.error(err);
            buy_facilities.value = []
            uni.showToast({
                icon: "error",
                title: "获取可购买设备列表失败"
            })
            return []
        }
    }

    // 移除设备
    async function removeFacility(data) {
        try {
            await deleteFacilities(data)
            uni.showToast({
                icon: 'success',
                title: '移除成功'
            })
            // 删除后重新获取设备列表
            await fetchFacilities()
            await fetchBuyFacilities()
        } catch (err) {
            console.error(err);
            uni.showToast({
                icon: "error",
                title: "网络错误"
            })
        }
    }

    // 购买设备
    async function purchaseFacility(data) {
        try {
            await buyFacilities(data)
            // 购买成功后重新获取设备列表
            await fetchFacilities()
            await fetchBuyFacilities()
        } catch (err) {
            console.error(err);
            uni.showToast({
                icon: "error",
                title: err.message?.data || "购买设备失败"
            })
            throw err
        }
    }

    return {
        setCurrentFacility,
        currentFacility,
        bought_facilities,
        buy_facilities,
        fetchFacilities,
        removeFacility,
        purchaseFacility,
        fetchBuyFacilities,
    }
}, {
    unistorage: true
});