<template>
  <div class="list">
    <div class="search">
      <div class="search-box">
        <el-form-item label="摄像头" :label-width="formLabelWidth">
          <el-select-v2
              v-model="searchKey.cameraId"
              filterable
              :options="CameraList"
              placeholder="请输入"
              style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="股道" :label-width="formLabelWidth">
          <el-input v-model="searchKey.trackId" style="width: 100%" placeholder="请输入"/>
        </el-form-item>
        <div class="search-btn">
          <el-button round @click="search">搜索</el-button>
        </div>
        <div class="clear-btn">
          <el-button round @click="clear">清除</el-button>
        </div>
      </div>
      <div class="add">
        <el-button round @click="addBtn">新增预置点</el-button>
      </div>
    </div>
    <div class="camera-list">
      <el-table :data="BallmachineData" style="width: 100%; height: 540px;">
        <el-table-column fixed prop="id" label="序号" min-width="5%">
          <template #default="{ $index }">
            {{ $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="cameraName" label="摄像头名称" min-width="8%"/>
        <el-table-column prop="trackId" label="股道id" min-width="8%"/>
        <el-table-column prop="presetPointId" label="预置点id" min-width="8%"/>
        <el-table-column prop="panPosition" label="水平坐标" min-width="10%"/>
        <el-table-column prop="tiltPosition" label="垂直坐标" min-width="10%"/>
        <el-table-column prop="zoom" label="变焦系数" min-width="10%"/>
        <el-table-column prop="smallRange" label="监控最低范围" min-width="10%"/>
        <el-table-column prop="wideRange" label="监控最高范围" min-width="10%"/>
        <el-table-column fixed="right" label="操作" min-width="15%">
          <template #default="{row}">
            <el-button link type="primary" size="middle" @click=deleteData(row.id)>转到预置点</el-button>
            <el-button link type="primary" size="middle" @click=editData(row)>编辑</el-button>
            <el-button link type="primary" size="middle" @click=deleteData(row.id)>删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="addForm">
      <el-dialog v-model="addFormVisible" title="添加预置点" width="500">
        <el-form :model="addForm">
          <el-form-item label="摄像头" :label-width="formLabelWidth">
            <el-select-v2
                v-model="addForm.cameraId"
                filterable
                :options="CameraList"
                placeholder="请输入"
                style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="股道id" :label-width="formLabelWidth">
            <el-input v-model="addForm.trackId" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="水平坐标" :label-width="formLabelWidth">
            <el-input v-model="addForm.panPosition" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="垂直坐标" :label-width="formLabelWidth">
            <el-input v-model="addForm.tiltPosition" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="变焦系数" :label-width="formLabelWidth">
            <el-input v-model="addForm.zoom" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="监控最小范围" :label-width="formLabelWidth">
            <el-input v-model="addForm.smallRange" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="监控最大范围" :label-width="formLabelWidth">
            <el-input v-model="addForm.wideRange" autocomplete="off"/>
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="addFormVisible = false">取消</el-button>
            <el-button type="primary" @click=addPresetPoint()>确认</el-button>
          </div>
        </template>
      </el-dialog>
    </div>
    <div class="editForm">
      <el-dialog v-model="editFormVisible" title="修改预置点" width="500">
        <el-form :model="form">
          <el-form-item label="水平坐标" :label-width="formLabelWidth">
            <el-input v-model="editForm.panPosition" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="垂直坐标" :label-width="formLabelWidth">
            <el-input v-model="editForm.tiltPosition" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="变焦系数" :label-width="formLabelWidth">
            <el-input v-model="editForm.zoom" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="监控最小范围" :label-width="formLabelWidth">
            <el-input v-model="editForm.smallRange" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="监控最大范围" :label-width="formLabelWidth">
            <el-input v-model="editForm.wideRange" autocomplete="off"/>
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="editFormVisible = false">取消</el-button>
            <el-button type="primary" @click=editPresetPoint()>确认</el-button>
          </div>
        </template>
      </el-dialog>
    </div>
    <div class="delete">
      <el-dialog v-model="deleteVisible" width="300" center>
        <span>确认删除？</span>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="deleteVisible = false">取消</el-button>
            <el-button type="primary" @click=deleteBallmachineById()>
              确认
            </el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive, onMounted} from 'vue'
import {ElMessage} from 'element-plus'
import {
  getAllBallmachine,
  insertPresetPoint,
  insertBallmachine,
  updateBallmachine,
  deleteBallmachine,
  searchBallmachine
} from '@/http/api/ballMachine.js'
import {getBallmachineCameras} from '@/http/api/camera.js'

const formLabelWidth = '140px'
//添加摄像头
const addFormVisible = ref(false)
const addForm = reactive({
  cameraId: '',
  trackId: '',
  panPosition: '',
  tiltPosition: '',
  zoom: '',
  smallRange: '',
  wideRange: ''
})

const CameraList = reactive([])
const getCameraList = async () => {
  try {
    const response = await getBallmachineCameras();
    // 将数据转换为 { label, value } 格式
    CameraList.splice(0, CameraList.length, ...response.data.map(camera => ({
      label: camera.name,
      value: camera.id,
    })));
  } catch (error) {
    console.error('获取摄像头列表失败:', error);
  }
}
const addBtn = () => {
  addFormVisible.value = true;
}
const addPresetPoint = async () => {
  const presetPointData = {
    panPosition: addForm.panPosition,
    tiltPosition: addForm.tiltPosition,
    smallRange: addForm.smallRange,
    wideRange: addForm.wideRange,
    zoom: addForm.zoom,
  };
  const addBallMachine = {
    cameraId: addForm.cameraId,
    trackId: addForm.trackId,
    presetPointId: '',
  }
  try {
    const response = await insertPresetPoint(presetPointData);
    addBallMachine.presetPointId = response.data;
    const response2 = await insertBallmachine(addBallMachine);
    ElMessage({
      message: '预置点添加成功',
      type: 'success',
      plain: true,
    })
    addFormVisible.value = false;
    getBallmachineData();
    resetForm();
  } catch (error) {
    ElMessage({
      message: '预置点添加失败，请检查数据',
      type: 'error',
      plain: true,
    })
  }
}
const resetForm = () => {
  addForm.cameraId = '';
  addForm.trackId = '';
  addForm.panPosition = '';
  addForm.tiltPosition = '';
  addForm.zoom = '';
  addForm.smallRange = '',
      addForm.wideRange = ''
};
//编辑预置点
const editFormVisible = ref(false)
const editForm = reactive({
  id: '',
  panPosition: '',
  tiltPosition: '',
  zoom: '',
  smallRange: '',
  wideRange: ''
})
const editForm2 = reactive({
  id: '',
  cameraId: '',
  trackId: '',
  presetPointId: '',
})
const editData = (row) => {
  editFormVisible.value = true
  editForm.id = row.presetPointId;
  editForm.panPosition = row.panPosition;
  editForm.tiltPosition = row.tiltPosition;
  editForm.zoom = row.zoom;
  editForm.smallRange = row.smallRange;
  editForm.wideRange = row.wideRange;

  editForm2.id = row.id;
  editForm2.cameraId = row.cameraId;
  editForm2.trackId = row.trackId;
}
const editPresetPoint = async () => {
  try {
    const response = await insertPresetPoint(editForm);
    editForm2.presetPointId = response.data;
    const res = await updateBallmachine(editForm2);
    getBallmachineData();
    editFormVisible.value = false;
  } catch (error) {
    console.log('预置点修改该失败:', error);
  }
}
//删除预置点
const deleteVisible = ref(false)
const ballmachineId = ref("")
const deleteData = (id) => {
  ballmachineId.value = id
  deleteVisible.value = true;
}
const deleteBallmachineById = async () => {
  try {
    const response = await deleteBallmachine(ballmachineId.value);
    if (response.data.success) {
      ElMessage({
        message: '摄像头信息删除成功',
        type: 'success',
        plain: true,
      })
      deleteVisible.value = false;
      getBallmachineData();
    }
  } catch (error) {
    console.log('摄像头信息删除该失败:', error);
  }
}
//获取预置点信息
const BallmachineData = reactive([])
const getBallmachineData = async () => {
  try {
    const response = await getAllBallmachine();
    BallmachineData.splice(0, BallmachineData.length, ...response.data);

  } catch (error) {
    console.error('获取列表失败:', error);
  }
}
//搜索
const searchKey = reactive({
  cameraId: "",
  trackId: "",
})
const search = async () => {
  try {
    const response = await searchBallmachine(searchKey.cameraId, searchKey.trackId);
    BallmachineData.splice(0, BallmachineData.length, ...response.data);
  } catch (error) {
    console.error("搜索失败：", error);
  }
}
//清除搜索
const clear = () => {
  searchKey.cameraId = '';
  searchKey.trackId = '';
  getBallmachineCameras();
}

onMounted(() => {
  getBallmachineData();
  getCameraList();
})


</script>

<style scoped>
.list {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.search {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 98%;
  height: 12%;
  margin: 1%;
  padding: 0 2% 0 2%;
  background-color: #fff;
}

.search-box {
  display: flex;
}

.search-btn {
  margin-left: 4%;
}

.clear-btn {
  margin-left: 4%;
}

.camera-list {
  height: 86%;
  width: 98%;
  margin: 0 1% 1% 1%;
  background-color: #fff;
}
</style>