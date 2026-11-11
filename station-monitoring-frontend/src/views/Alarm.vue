<template>
  <div ref="reviewPanel" class="alarm">
    <header class="ops-page-header">
      <div><span class="ops-eyebrow">EVENT REVIEW / 告警核查</span><h1>告警中心</h1><p>按摄像头、时间与事件类型定位记录，完成核查与处置。</p></div>
      <div class="ops-header-mark"><span>01</span><small>事件核查</small></div>
    </header>
    <RailReviewSteps :step="reviewStep" :record-id="reviewId" />
    <p v-if="reviewNotice" class="review-notice" role="status">{{ reviewNotice }}</p>
    <el-tabs v-model="activeTab" type="border-card" class="form">
      <el-tab-pane label="危险警告" name="danger">
        <div class="filter">
          <div style="font-size: 14px;font-weight: 600;margin: 0.4% 0 0 0;width: 4%;">筛选:</div>
          <div class="filter-form">
            <el-form :inline="true" :model="searchData" class="demo-form-inline">
              <el-form-item label="摄像头" :label-width="formLabelWidth">
                <el-select v-model="searchData.cameraName" filterable clearable placeholder="请选择摄像头" style="width: 100%">
                  <el-option v-for="camera in CameraList" :key="camera.value" :label="camera.label" :value="camera.value" />
                </el-select>
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
                <el-button type="primary" @click="searchAlarmInfoBtn()" round>搜索</el-button>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="clearBtn()" round>清除</el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
        <div class="alarm-table">
          <el-table :data="alarmInfo" :row-class-name="row => reviewRowClass(row, 'danger')" style="width: 100%;" height="500" max-height="500">
            <el-table-column fixed prop="id" label="序号" min-width="8%" align="center">
              <template #default="{ $index }">
                {{ $index + 1 }}
              </template>
            </el-table-column>
            <el-table-column fixed prop="cameraName" label="摄像头" min-width="10%" align="center" :formatter="row => cameraNameForEvent(row, CameraList)" />
            <el-table-column prop="content" label="内容" min-width="15%" align="center"/>
            <el-table-column label="类型" min-width="10%" align="center">
              <template #default="{ row }">
                <span class="rail-event-type">{{ row.type == 1 ? '人员目标检出' : row.type == 2 ? '车辆目标检出' : row.type || '类型未记录' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="风险" min-width="10%" align="center"><template #default="{ row }"><EventPriority :level="row.level" /></template></el-table-column>
            <el-table-column prop="createTime" label="报警时间" min-width="15%" align="center" :formatter="formatTime"/>
            <el-table-column fixed="right" label="操作" min-width="10%" align="center">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleClick(row.id)" :disabled="reviewSubmitting">处理</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      <el-tab-pane label="摄像头警告" name="camera">
        <div class="filter">
          <div style="font-size: 14px;font-weight: 600;margin: 0.4% 0 0 0;width: 4%;">筛选:</div>
          <div class="filter-form">
            <el-form :inline="true" :model="searchData" class="demo-form-inline">
              <el-form-item label="摄像头" :label-width="formLabelWidth">
                <el-select v-model="searchData.cameraName" filterable clearable placeholder="请选择摄像头" style="width: 100%">
                  <el-option v-for="camera in CameraList" :key="camera.value" :label="camera.label" :value="camera.value" />
                </el-select>
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
                <el-button type="primary" @click="searchCameraAlarmBtn()" round>搜索</el-button>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="clearBtn()" round>清除</el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
        <el-table :data="cameraAlarmData" :row-class-name="row => reviewRowClass(row, 'camera')" style="width: 100%;" height="500" max-height="500">
          <el-table-column fixed prop="id" label="序号" min-width="8%" align="center">
            <template #default="{ $index }">
              {{ $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="cameraName" label="摄像头" min-width="15%" align="center" :formatter="row => cameraNameForEvent(row, CameraList)" />
          <el-table-column prop="productNumber" label="产品编号" min-width="15%" align="center"/>
          <el-table-column prop="ip" label="IP" min-width="15%" align="center"/>
          <el-table-column prop="port" label="端口号" min-width="15%" align="center"/>
          <el-table-column label="类型" min-width="15%" align="center">
            <template #default>
              <RailSignal class="rail-table-signal" state="offline" />
            </template>
          </el-table-column>
          <el-table-column prop="createTime" label="时间" min-width="15%" align="center" :formatter="formatTime"/>
          <el-table-column fixed="right" label="操作" min-width="15%" align="center">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="dealClick(row.id)" :disabled="reviewSubmitting">
                处理
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import EventPriority from '@/components/EventPriority.vue'
import {reactive, onMounted, ref, computed, watch} from 'vue'
import {useRoute} from 'vue-router'
import RailReviewSteps from '@/components/RailReviewSteps.vue'
import RailSignal from '@/components/RailSignal.vue'
import { cameraNameForEvent } from '@/utils/railPresentation'
import {getUndisposedCameraAlarm, updateCameraAlarmById, search} from '@/http/api/camerAlarm.js'
import {getAllCameras} from '@/http/api/camera';
import {getUndisposedAlarmInfo, searchAlarmInfo, updateAlarmInfoById} from '@/http/api/alarm.js'
import {ElMessage, ElMessageBox} from 'element-plus'
import {getCurrentInstance} from 'vue';

// 获取全局 `formatDate` 方法
const {appContext} = getCurrentInstance();
const formatDate = appContext.config.globalProperties.$formatDate;

// 定义格式化方法
const formatTime = (row, column, cellValue) => {
  if (!cellValue) return '无时间';
  return formatDate(cellValue, 'YYYY-MM-DD HH:mm:ss'); // 这里可以自定义格式
};


//获取摄像头警告
const cameraAlarmData = reactive([])

const getAllCameraAlarmData = async () => {
  try {
    const response = await getUndisposedCameraAlarm();
    cameraAlarmData.splice(0, cameraAlarmData.length, ...response.data);
  } catch {
    console.error("获取摄像头警告失败");
  }
}

//获取摄像头列表
const CameraList = reactive([])
const getCameraList = async () => {
  try {
    const response = await getAllCameras();
    // 将数据转换为 { label, value } 格式
    CameraList.splice(0, CameraList.length, ...response.data.map(camera => ({
      id: camera.id,
      name: camera.name,
      label: camera.name,
      value: camera.name,
    })));
  } catch (error) {
    console.error('获取摄像头列表失败:', error);
  }
}
//搜索
const dayOptions = [
  {value: 0, label: '全部'},
  {value: 1, label: '今天'},
  {value: 3, label: '近三天'},
  {value: 7, label: '近七天'},
  {value: 15, label: '近半月'}
]
const typeOptions = [
  {value: 0, label: '全部'},
  {value: 1, label: '人员进入'},
  {value: 2, label: '车辆进入'},
]

const searchData = reactive({
  cameraName: '',
  day: '',
  type: '',
})

//摄像头警告搜索
const searchCameraAlarmBtn = async () => {
  try {
    const response = await search(searchData.cameraName, searchData.day, searchData.type, '0');    //传入0代表针对未处理的摄像头警告进行搜索

    cameraAlarmData.splice(0, cameraAlarmData.length, ...response.data.data);
  } catch (error) {
    console.error('搜索失败', error);
  }
}


//危险警告搜索
const searchAlarmInfoBtn = async () => {
  try {
    const response = await searchAlarmInfo(searchData.cameraName, searchData.day, searchData.type, '0');    //传入0代表针对未处理的摄像头警告进行搜索
    alarmInfo.splice(0, alarmInfo.length, ...response.data.data);
  } catch (error) {
    console.error('搜索失败', error);
  }
}
//清除
const clearBtn = () => {
  getAllCameraAlarmData();
  getAllAlarmData();
  searchData.cameraName = '';
  searchData.day = '';
  searchData.type = '';
}


//危险警告
const alarmInfo = reactive([])
const getAllAlarmData = async () => {
  try {
    const response = await getUndisposedAlarmInfo();
    alarmInfo.splice(0, alarmInfo.length, ...response.data.data);
  } catch (error) {
    console.error('获取危险警告失败', error);
  }
}

const route = useRoute();
const reviewPanel = ref(null);
const activeTab = ref('danger');
const reviewStep = ref(0);
const reviewId = ref(null);
const reviewKind = ref(null);
const reviewSubmitting = ref(false);
const reviewNotice = ref('');
const linkedKind = computed(() => route.query.kind === 'camera' ? 'camera' : 'danger');
const linkedId = computed(() => typeof route.query.event === 'string' ? route.query.event : null);
watch([linkedId, linkedKind], () => {
  activeTab.value = linkedKind.value;
  reviewId.value = linkedId.value;
  reviewKind.value = linkedId.value ? linkedKind.value : null;
  reviewStep.value = 0;
  reviewNotice.value = '';
}, { immediate: true });

function reviewRowClass({ row }, kind) {
  return reviewId.value != null && reviewKind.value === kind && String(row.id) === String(reviewId.value)
    ? 'rail-linked-row' : '';
}

const handleClick = id => reviewRecord(id, 'danger', updateAlarmInfoById, getAllAlarmData);
const dealClick = id => reviewRecord(id, 'camera', updateCameraAlarmById, getAllCameraAlarmData);

async function reviewRecord(id, kind, update, refresh) {
  if (reviewSubmitting.value) return;
  reviewSubmitting.value = true;
  reviewId.value = id;
  reviewKind.value = kind;
  reviewStep.value = 1;
  reviewNotice.value = '';
  try {
    await ElMessageBox.confirm('确认已经完成处理?', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
    });
  } catch {
    reviewStep.value = 0;
    reviewSubmitting.value = false;
    reviewNotice.value = '已取消本次处置。';
    return;
  }
  reviewStep.value = 2;
  try {
    const response = await update(id);
    if (!response.data.success) throw new Error('处理记录失败');
    reviewStep.value = 3;
    reviewNotice.value = '处理结果已保存。';
    ElMessage.success('处理记录成功');
    await refresh();
  } catch {
    reviewNotice.value = '处理结果未保存，请重新选择该记录后重试。';
    ElMessage.error('处理记录失败');
  } finally {
    reviewSubmitting.value = false;
  }
}

watch(() => [route.query.event, activeTab.value, alarmInfo.length, cameraAlarmData.length], () => {
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
.alarm {
  width: 100%;
  height: 100%;
  min-height: 0;
  padding: 16px;
  background: #f6f8fb;
}

.form {
  width: 100%;
  height: 100%;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.form :deep(.el-tabs__content) { height: calc(100% - 56px); }
.form :deep(.el-tab-pane) { height: 100%; min-height: 0; display: flex; flex-direction: column; }
.form :deep(.el-table) { flex: 1 1 auto; height: auto !important; min-height: 0; }

.demo-form-inline .el-input {
  --el-input-width: 180px;
}

.demo-form-inline .el-select {
  --el-select-width: 180px;
}

.filter {
  display: flex;
  flex: 0 0 auto;
  flex-wrap: wrap;
  gap: 10px;
  align-items: flex-start;
  padding: 12px;
  width: 100%;
}

.filter-form {
  flex: 1;
  min-width: 0;
}

.alarm-table {
  width: 100%;
  min-height: 0;
  flex: 1 1 auto;
}

@media (max-width: 900px) {
  .alarm { padding: 10px; }
  .filter > div:first-child { width: auto !important; margin: 6px 0 0 !important; }
  .filter-form { width: 100%; flex-basis: 100%; }
  .filter-form :deep(.el-form) { display: flex; flex-wrap: wrap; gap: 0 8px; }
  .filter-form :deep(.el-form-item) { margin-right: 0; }
  .filter-form :deep(.el-select),
  .filter-form :deep(.el-input) { width: min(240px, 72vw) !important; }
}

.ops-page-header { flex:0 0 auto;display:flex;justify-content:space-between;align-items:center;min-height:88px;margin-bottom:12px;padding:8px 6px 14px;border-bottom:1px solid #cfdeeb; }
.ops-eyebrow { color:#157da6;font-size:11px;letter-spacing:1.5px;font-weight:700; }
.ops-page-header h1 { margin:4px 0 2px;color:#153b5b;font-size:25px;line-height:1.2; }
.ops-page-header p { margin:0;color:#6e879a;font-size:12px; }
.ops-header-mark { display:flex;flex-direction:column;align-items:center;color:#2081ad;opacity:.52; }
.ops-header-mark span { font:italic 800 30px "Segoe UI",sans-serif; }
.ops-header-mark small { font-size:10px; }
.alarm { display:flex;flex-direction:column;background:linear-gradient(140deg,#f1f6fa,#f7fafc 50%,#edf4fa); }
.form { flex:1;min-height:0;border:0;border-top:2px solid #58b5d2;border-radius:8px;background:#fff;box-shadow:0 8px 30px rgba(21,63,99,.055); }
.form :deep(.el-tabs__header) { margin:0;border:0;background:#f3f8fc; }
.form :deep(.el-tabs__item) { height:47px;font-weight:600; }
.form :deep(.el-tabs__item.is-active) { color:#087da9;background:#fff; }
.filter { border-bottom:1px solid #e5eef4;background:linear-gradient(90deg,#f9fcfe,#fff); }
.filter :deep(.el-form-item) { margin-bottom:6px; }
.alarm-table :deep(.el-table),.form :deep(.el-table) { --el-table-header-bg-color:#edf5fa;--el-table-row-hover-bg-color:#f0f8fb; }

/* 告警核查工作台：筛选、记录、处理保持原位，减弱封闭容器。 */
.alarm{padding:18px 24px;background:radial-gradient(ellipse at 55% 20%,#0b3451,#061e36 56%,#04172d)!important}
.ops-page-header{min-height:78px;margin-bottom:15px;padding:0 2px 13px;background:transparent!important;border:0!important;box-shadow:none!important;position:relative}
.ops-page-header::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:linear-gradient(90deg,#39bddc 0,rgba(57,189,220,.28) 24%,transparent 78%)}
.ops-page-header h1{font-size:28px;letter-spacing:.7px}
.ops-header-mark{opacity:.28}
.form{border:0!important;border-radius:0;background:linear-gradient(180deg,rgba(12,55,84,.38),rgba(7,33,56,.14) 50%,transparent)!important;box-shadow:none!important;overflow:hidden}
.form :deep(.el-tabs__header){background:transparent!important;border-bottom:1px solid rgba(84,170,201,.22)!important;margin:0 0 8px}
.form :deep(.el-tabs__nav){border:0!important}
.form :deep(.el-tabs__item){height:45px;padding:0 25px!important;border:0!important;background:transparent!important;color:#95bacc!important;position:relative;letter-spacing:.5px}
.form :deep(.el-tabs__item.is-active){color:#f1fcff!important;background:linear-gradient(180deg,rgba(24,120,161,.32),rgba(24,120,161,.03))!important}
.form :deep(.el-tabs__item.is-active)::after{content:"";position:absolute;left:16px;right:16px;bottom:0;height:2px;background:linear-gradient(90deg,transparent,#54d6ec,transparent)}
.form :deep(.el-tabs__content){padding:0 8px!important}
.filter{align-items:center;padding:12px 5px 15px!important;background:transparent!important;border-bottom:1px solid rgba(84,170,201,.18)!important}
.filter>div:first-child{width:auto!important;min-width:38px;margin:7px 0 0!important;color:#79c9e0;font-size:12px!important;letter-spacing:1px}
.filter :deep(.el-form-item){margin-bottom:0;margin-right:16px}
.alarm-table :deep(.el-table),.form :deep(.el-table){--el-table-header-bg-color:#0e3854;--el-table-row-hover-bg-color:#12445f;background:transparent!important}
.form :deep(.el-table__header-wrapper){border-top:1px solid rgba(84,170,201,.26)}
.form :deep(.el-table th){height:44px;font-size:12px;letter-spacing:.4px}
.form :deep(.el-table td){height:52px}
.form :deep(.el-table__empty-text){color:#a6c6d6}
.form :deep(.el-table__body-wrapper),.form :deep(.el-scrollbar__view){background:linear-gradient(180deg,rgba(7,33,56,.28),rgba(4,23,45,0) 65%)!important}
.form :deep(.el-table__empty-block){min-height:185px!important}
.form :deep(.el-table__empty-text){display:flex;align-items:center;justify-content:center;min-height:98px;font-size:13px;letter-spacing:.4px}
@media(max-width:900px){.alarm{padding:12px}.filter{align-items:flex-start}.filter>div:first-child{margin:8px 0 0!important}}

.alarm { display: flex; flex-direction: column; box-sizing: border-box; }
.alarm .form { flex: 1 1 auto; min-height: 280px; height: auto; }
.alarm .rail-review, .alarm .review-notice { flex: none; }
.alarm .review-notice { margin: 0 0 8px; color: #c3dadd; font-size: 13px; }
@media (max-width: 700px) {
  .alarm { overflow-y: auto; }
  .alarm .form { min-height: 520px; }
}
.alarm .form :deep(.el-scrollbar__view) { background: #1b272e !important; }
</style>
