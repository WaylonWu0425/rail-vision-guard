<template>
    <div ref="reviewPanel" class="alarm-record">
    <header class="ops-page-header"><div><span class="ops-eyebrow">ALARM ARCHIVE / 历史追溯</span><h1>告警历史</h1><p>检索已记录的事件和设备告警，追溯处置过程。</p></div></header>
        <el-tabs v-model="activeTab" type="border-card" class="form">
            <el-tab-pane label="危险警告记录" name="danger">
                <div class="filter">
                    <div style="font-size: 14px;font-weight: 600;margin: 0.4% 0 0 0;width: 4%;">筛选:</div>
                    <div class="filter-form">
                        <el-form :inline="true" :model="searchData" class="demo-form-inline">
                            <el-form-item label="摄像头" :label-width="formLabelWidth">
                                <el-select-v2
                                    v-model="searchData.cameraName"
                                    filterable
                                    :options="CameraList"
                                    placeholder="请输入"
                                    style="width: 100%"
                                />
                            </el-form-item>
                            <el-form-item label="时间" :label-width="formLabelWidth">
                                <el-select v-model="searchData.day" placeholder="请选择时间" style="width: 240px">
                                    <el-option
                                        v-for="item in dayOptions"
                                        :key="item.value"
                                        :label="item.label"
                                        :value="item.value"
                                    />
                                </el-select>
                            </el-form-item>
                            <el-form-item label="类型" :label-width="formLabelWidth">
                                <el-select v-model="searchData.type" placeholder="请选择类型" style="width: 240px">
                                    <el-option
                                        v-for="item in typeOptions"
                                        :key="item.value"
                                        :label="item.label"
                                        :value="item.value"
                                    />
                                </el-select>
                            </el-form-item>
                            <el-form-item>
                                <el-button type="primary" @click="searchAllAlarmData()" round>搜索</el-button>
                            </el-form-item>
                            <el-form-item>
                                <el-button type="primary" @click="clearBtn()" round>清除</el-button>
                            </el-form-item>
                        </el-form>
                    </div>
                </div>
                <div class="alarm-table">
                    <el-table :data="alarmData" :row-class-name="row => archiveRowClass(row, 'danger')" style="width: 100%;" height="500" max-height="500">
                        <el-table-column fixed prop="id" label="序号" min-width="8%" align="center">
                            <template #default="{ $index }">
                            {{ $index + 1 }}
                            </template>
                        </el-table-column>
                        <el-table-column fixed prop="cameraName" label="摄像头" min-width="10%" align="center" :formatter="row => cameraNameForEvent(row, CameraList)" />
                        <el-table-column prop="content" label="内容" min-width="15%" align="center"/>
                        <el-table-column prop="dealUserName" label="处理人" min-width="15%" align="center"/>
                        <el-table-column label="类型" min-width="10%" align="center">
                            <template #default="{ row }">
                                <el-tag :type="row.type == 1 ? 'primary' : row.type == 2 ? 'error' : 'info'">
                                    <span>{{ row.type == 1 ? '人员进入' : row.type == 2 ? '车辆进入' : row.type }}</span>
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="风险" min-width="10%" align="center"><template #default="{ row }"><EventPriority :level="row.level" /></template></el-table-column>
                        <el-table-column prop="createTime" label="报警时间" min-width="15%" align="center" :formatter="formatTime"/>
                        <el-table-column prop="dealTime" label="处理时间" min-width="15%" align="center" :formatter="formatTime"/>
                        <el-table-column prop="dealFlag" label="状态" min-width="10%" align="center">
                            <template #default="{ row }">
                                <RailSignal class="rail-table-signal" :state="alarmRailState(row.dealFlag)" />
                            </template>
                        </el-table-column>
                    </el-table>
                </div>
            </el-tab-pane>
            <el-tab-pane label="摄像头警告记录" name="camera">
                <div class="filter">
                    <div style="font-size: 14px;font-weight: 600;margin: 0.4% 0 0 0;width: 4%;">筛选:</div>
                    <div class="filter-form">
                        <el-form :inline="true" :model="searchData" class="demo-form-inline">
                            <el-form-item label="摄像头" :label-width="formLabelWidth">
                                <el-select-v2
                                    v-model="searchData.cameraName"
                                    filterable
                                    :options="CameraList"
                                    placeholder="请输入"
                                    style="width: 100%"
                                />
                            </el-form-item>
                            <el-form-item label="时间" :label-width="formLabelWidth">
                                <el-select v-model="searchData.day" placeholder="请选择时间" style="width: 240px">
                                    <el-option
                                        v-for="item in dayOptions"
                                        :key="item.value"
                                        :label="item.label"
                                        :value="item.value"
                                    />
                                </el-select>
                            </el-form-item>
                            <el-form-item>
                                <el-button type="primary" @click="searchBtn()" round>搜索</el-button>
                            </el-form-item>
                            <el-form-item>
                                <el-button type="primary" @click="clearBtn()" round>清除</el-button>
                            </el-form-item>
                        </el-form>
                    </div>
                </div>
                <el-table :data="cameraAlarmData" :row-class-name="row => archiveRowClass(row, 'camera')" style="width: 100%">
                    <el-table-column fixed prop="id" label="序号" min-width="10%" align="center">
                        <template #default="{ $index }">
                        {{ $index + 1 }}
                        </template>
                    </el-table-column>
                    <el-table-column fixed prop="cameraName" label="摄像头" min-width="10%" align="center" :formatter="row => cameraNameForEvent(row, CameraList)" />
                    <el-table-column prop="productNumber" label="产品编号" min-width="10%" align="center"/>
                    <el-table-column prop="port" label="端口" min-width="10%" align="center"/>
                    <el-table-column prop="ip" label="IP" min-width="10%" align="center"/>
                    <el-table-column prop="username" label="处理人" min-width="10%" align="center">
                        <template #default="{ row }">
                            <el-tag>
                                {{ row.username == null ? '无' : row.username }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="createTime" label="发生时间" min-width="10%" align="center" :formatter="formatTime"/>
                    <el-table-column prop="dealTime" label="处理时间" min-width="10%" align="center" :formatter="formatTime"/>
                    <el-table-column prop="dealFlag" label="状态" min-width="10%" align="center">
                        <template #default="{ row }">
                            <RailSignal class="rail-table-signal" :state="alarmRailState(row.dealFlag)" />
                        </template>
                    </el-table-column>
                </el-table>
            </el-tab-pane>
        </el-tabs>
    </div>
</template>

<script setup>
import EventPriority from '@/components/EventPriority.vue'
import { reactive, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import RailSignal from '@/components/RailSignal.vue'
import { alarmRailState, cameraNameForEvent } from '@/utils/railPresentation'
import { getAllCameraAlarm, search } from'@/http/api/camerAlarm.js'
import { getCurrentInstance } from 'vue';
import { getAllCameras } from '@/http/api/camera'
import { getAllAlarmInfo, searchAlarmInfo } from '@/http/api/alarm.js'
import { ElMessage } from 'element-plus'

// 获取全局 `formatDate` 方法
const { appContext } = getCurrentInstance();
const formatDate = appContext.config.globalProperties.$formatDate;

// 定义格式化方法
const formatTime = (row, column, cellValue) => {
  if (!cellValue) return '无时间';
  return formatDate(cellValue, 'YYYY-MM-DD HH:mm:ss'); // 这里可以自定义格式
};

//获取摄像头警告
const cameraAlarmData = reactive([])

const getAllCameraAlarmData = async()=> {
    try {
        const response = await getAllCameraAlarm();
        cameraAlarmData.splice(0, cameraAlarmData.length, ...response.data);
    }catch{
        console.error("获取摄像头警告失败");
    }
}
//获取摄像头列表
const CameraList = reactive([])
const getCameraList = async()=> {    
    try {
        const response = await getAllCameras();
        // 将数据转换为 { label, value } 格式
        CameraList.splice(0, CameraList.length, ...response.data.map(camera => ({
            id: camera.id,
            name: camera.name,
            label: camera.name,
            value: camera.name,  
        })));
    }catch(error) {
        console.error('获取摄像头列表失败:',error);
    }
}
//搜索
const dayOptions = [
    { value: 0, label: '全部'},
    { value: 1, label: '今天' },
    { value: 3, label: '近三天' },
    { value: 7, label: '近七天' },
    { value: 15, label: '近半月' }
]
const typeOptions = [
    { value: 0, label: '全部'},
    { value: 1, label: '人员进入' },
    { value: 2, label: '车辆进入' },
]
const searchData = reactive({
    cameraName: '',
    day: '',
    type: ''
})

const searchBtn = async() => {
    try {
        const response = await search(searchData.cameraName, searchData.day, '1');    //传入1代表针对所有的摄像头警告进行搜索
        cameraAlarmData.splice(0, cameraAlarmData.length, ...response.data.data);
    }catch(error) {
        console.error('搜索失败', error);
    }
}
//清除
const clearBtn = () => {
    getAllCameraAlarmData();
    searchData.cameraName = '';
    searchData.day = '';
    searchData.type = '';
}
//获取所有的危险警告
const alarmData = reactive([])
const getAllAlarmData = async() => {
    try {
        const response = await getAllAlarmInfo();
        if (response.data.success) {
            alarmData.splice(0, alarmData.length, ...response.data.data);
        }else {
            ElMessage({
                message: '获取所有危险警告失败',
                type: 'error',
                plain: true,
            });
        }
    }catch(error) {
        console.error('获取所有危险警告失败', error);
    }
}
//搜索全部危险警告
const searchAllAlarmData = async() => {
    try {
        const response = await searchAlarmInfo(searchData.cameraName, searchData.day,searchData.type, '1');    //传入1代表针对所有的摄像头警告进行搜索
        alarmData.splice(0, alarmData.length, ...response.data.data);
    }catch(error) {
        console.error('搜索失败', error);
    }
}

const route = useRoute();
const reviewPanel = ref(null);
const activeTab = ref('danger');
watch(() => route.query.kind, kind => {
  activeTab.value = kind === 'camera' ? 'camera' : 'danger';
}, { immediate: true });
function archiveRowClass({ row }, kind) {
  const expectedKind = route.query.kind === 'camera' ? 'camera' : 'danger';
  return typeof route.query.event === 'string' && kind === expectedKind && String(row.id) === route.query.event
    ? 'rail-linked-row' : '';
}

watch(() => [route.query.event, activeTab.value, alarmData.length, cameraAlarmData.length], () => {
  if (!route.query.event) return;
  const row = reviewPanel.value?.querySelector('.el-tab-pane:not([style*="display: none"]) tr.rail-linked-row');
  row?.scrollIntoView({ block: 'nearest', inline: 'nearest' });
}, { flush: 'post' });

onMounted(() => {
    getAllCameraAlarmData();
    getCameraList();
    getAllAlarmData();
})

</script>


<style scoped>
.alarm-record {
    width: 98%;
    height: 97%;
    margin: 1%;
    background-color: #fff;
}
.form {
    width: 100%;
    height: 100%;
}
.demo-form-inline .el-input {
  --el-input-width: 180px;
}

.demo-form-inline .el-select {
  --el-select-width: 180px;
}
.filter {
    display: flex;
    flex-wrap: nowrap;
    width: 100%;
}
.filter-form {
    width: 92%;
}

.ops-page-header { flex:0 0 auto;min-height:80px;margin-bottom:12px;padding:6px 6px 14px;border-bottom:1px solid #cfdeeb; }
.ops-eyebrow { color:#157da6;font-size:11px;letter-spacing:1.4px;font-weight:700; }
.ops-page-header h1 { margin:4px 0 2px;color:#153b5b;font-size:24px;line-height:1.2; }
.ops-page-header p { margin:0;color:#6e879a;font-size:12px; }

.alarm-record { width:100%;height:100%;margin:0;padding:16px;display:flex;flex-direction:column;min-height:0;background:#f2f7fb; }
.form { flex:1;min-height:0;height:auto;border:0;border-top:2px solid #58b5d2;border-radius:8px;box-shadow:0 8px 30px rgba(21,63,99,.05); }
.form :deep(.el-tabs__content) { height:calc(100% - 56px);overflow:auto; }
.filter { padding:12px;gap:10px;flex-wrap:wrap; }
.filter-form { flex:1;min-width:0; }
</style>