<template>
  <div class="alarm">
    <el-tabs type="border-card" class="form">
      <el-tab-pane label="危险警告">
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
                <el-button type="primary" @click="searchAlarmInfoBtn()" round>搜索</el-button>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="clearBtn()" round>清除</el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
        <div class="alarm-table">
          <el-table :data="alarmInfo" style="width: 100%;" height="500" max-height="500">
            <el-table-column fixed prop="id" label="序号" min-width="8%" align="center">
              <template #default="{ $index }">
                {{ $index + 1 }}
              </template>
            </el-table-column>
            <el-table-column fixed prop="cameraName" label="摄像头" min-width="10%" align="center"/>
            <el-table-column prop="content" label="内容" min-width="15%" align="center"/>
            <el-table-column label="类型" min-width="10%" align="center">
              <template #default="{ row }">
                <el-tag :type="row.type == 1 ? 'primary' : row.type == 2 ? 'error' : 'info'">
                  <span>{{ row.type == 1 ? '人员进入' : row.type == 2 ? '车辆进入' : row.type }}</span>
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="level" label="级别" min-width="10%" align="center"/>
            <el-table-column prop="createTime" label="报警时间" min-width="15%" align="center" :formatter="formatTime"/>
            <el-table-column fixed="right" label="操作" min-width="10%" align="center">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleClick(row.id)">处理</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      <el-tab-pane label="摄像头警告">
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
                <el-button type="primary" @click="searchCameraAlarmBtn()" round>搜索</el-button>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="clearBtn()" round>清除</el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
        <el-table :data="cameraAlarmData" style="width: 100%;" height="500" max-height="500">
          <el-table-column fixed prop="id" label="序号" min-width="8%" align="center">
            <template #default="{ $index }">
              {{ $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="cameraName" label="摄像头" min-width="15%" align="center"/>
          <el-table-column prop="productNumber" label="产品编号" min-width="15%" align="center"/>
          <el-table-column prop="ip" label="IP" min-width="15%" align="center"/>
          <el-table-column prop="port" label="端口号" min-width="15%" align="center"/>
          <el-table-column label="类型" min-width="15%" align="center">
            <template #default>
              <el-tag type="danger">
                <span>掉线</span>
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createTime" label="时间" min-width="15%" align="center" :formatter="formatTime"/>
          <el-table-column fixed="right" label="操作" min-width="15%" align="center">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="dealClick(row.id)">
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
import {reactive, onMounted} from 'vue'
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

//处理摄像头警告
const dealClick = async (id) => {
  try {
    await ElMessageBox.confirm(
        '确认已经完成处理?',
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
        }
    );

    try {
      const response = await updateCameraAlarmById(id);
      if (response.data.success) {
        ElMessage({
          message: '处理记录成功',
          type: 'success',
          plain: true,
        });
        getAllCameraAlarmData();
      } else {
        ElMessage({
          message: '处理记录失败',
          type: 'error',
          plain: true,
        });
      }
    } catch (error) {
      ElMessage({
        message: '网络错误: ' + error.message,
        type: 'error',
        plain: true,
      });
    }
  } catch (error) {
    ElMessage({
      type: 'info',
      message: '已取消处理',
    });
  }

};
//获取摄像头列表
const CameraList = reactive([])
const getCameraList = async () => {
  try {
    const response = await getAllCameras();
    // 将数据转换为 { label, value } 格式
    CameraList.splice(0, CameraList.length, ...response.data.map(camera => ({
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

//危险警告处理
const handleClick = async (id) => {
  try {
    await ElMessageBox.confirm(
        '确认已经完成处理?',
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
        }
    );
    try {
      const response = await updateAlarmInfoById(id);
      if (response.data.success) {
        ElMessage({
          message: '处理记录成功',
          type: 'success',
          plain: true,
        });
      } else {
        ElMessage({
          message: '处理记录失败',
          type: 'error',
          plain: true,
        });
      }
      getAllAlarmData();
    } catch (error) {
      console.error('处理失败', error);
    }
  } catch (error) {
    console.error('处理失败', error);
  }
}


onMounted(() => {
  getAllCameraAlarmData();
  getCameraList();
  getAllAlarmData();
})
</script>

<style scoped>
.alarm {
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

.alarm-table {
  width: 100%;
  height: calc(100% - 60px);
}
</style>