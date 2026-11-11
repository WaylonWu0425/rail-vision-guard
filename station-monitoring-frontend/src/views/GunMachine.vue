<template>
  <div class="list">
    <header class="ops-page-header"><div><span class="ops-eyebrow">FIXED CAMERA PRESETS / 设备配置</span><h1>枪机预置点</h1><p>查看固定枪机与股道关联的预置点。</p></div></header>
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
      <el-table :data="gunmachineData" style="width: 100%; height: 540px;">
        <el-table-column fixed prop="id" label="序号" min-width="5%">
          <template #default="{ $index }">
            {{ $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="cameraName" label="摄像头名称" min-width="8%"/>
        <el-table-column prop="trackId" label="股道id" min-width="8%"/>
        <el-table-column prop="smallRange" label="监控最低范围" min-width="10%"/>
        <el-table-column prop="wideRange" label="监控最高范围" min-width="10%"/>
        <el-table-column fixed="right" label="操作" min-width="15%">
          <template #default="{row}">
            <el-button link type="primary" size="middle" @click=gotoPreset(row)>转到预置点</el-button>
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
            <el-button type="primary" @click=deleteGunmachineById()>
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
  getAllGunmachine,
  insertGunmachine,
  updateGunmachine,
  deleteById,
  searchGunmachine
} from '@/http/api/gunmachine.js'
import {getGunmachineCameras} from '@/http/api/camera.js'

const formLabelWidth = '140px'
//添加摄像头
const addFormVisible = ref(false)
const addForm = reactive({
  cameraId: '',
  trackId: '',
  smallRange: '',
  wideRange: '',
})

const CameraList = reactive([])
const getCameraList = async () => {
  try {
    const response = await getGunmachineCameras();
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
  try {
    const response = await insertGunmachine(addForm);
    if (response) {
      ElMessage({
        message: '预置点添加成功',
        type: 'success',
        plain: true,
      })
      addFormVisible.value = false;
      getGunmachineData();
      resetForm();
    } else {
      ElMessage({
        message: '预置点添加失败',
        type: 'error',
        plain: true,
      })
    }
  } catch (error) {
    console.error('添加失败:', error);
  }
}
const resetForm = () => {
  addForm.cameraId = '';
  addForm.trackId = '';
  addForm.smallRange = '',
      addForm.wideRange = ''
};
//编辑预置点
const editFormVisible = ref(false)
const editForm = reactive({
  id: '',
  cameraId: '',
  trackId: '',
  smallRange: '',
  wideRange: ''
})
const editData = (row) => {
  editFormVisible.value = true
  editForm.id = row.id;
  editForm.cameraId = row.cameraId;
  editForm.trackId = row.trackId;
  editForm.smallRange = row.smallRange;
  editForm.wideRange = row.wideRange;
}
const editPresetPoint = async () => {
  try {
    const response = await updateGunmachine(editForm);
    console.log(response);

    if (response.data == "ture") {
      ElMessage({
        message: '预置点信息修改成功',
        type: 'success',
        plain: true,
      })
    }
    getGunmachineData();
    editFormVisible.value = false;
  } catch (error) {
    console.log('预置点修改该失败:', error);
  }
}
//转到预置点（云台控制，需要摄像头在线）
const gotoPreset = (row) => {
  ElMessage({
    message: '云台转到预置点需要摄像头在线，当前设备离线，暂无法执行',
    type: 'warning',
    plain: true,
  })
}
//删除预置点
const deleteVisible = ref(false)
const gunmachineId = ref("")
const deleteData = (id) => {
  gunmachineId.value = id
  deleteVisible.value = true;
}
const deleteGunmachineById = async () => {
  try {
    const response = await deleteById(gunmachineId.value);
    if (response.data.success) {
      ElMessage({
        message: '预置点信息删除成功',
        type: 'success',
        plain: true,
      })
      deleteVisible.value = false;
      getGunmachineData();
    }
  } catch (error) {
    console.log('预置点信息删除该失败:', error);
  }
}
//获取预置点信息
const gunmachineData = reactive([])
const getGunmachineData = async () => {
  try {
    const response = await getAllGunmachine();
    gunmachineData.splice(0, gunmachineData.length, ...response.data);

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
    const response = await searchGunmachine(searchKey.cameraId, searchKey.trackId);
    gunmachineData.splice(0, gunmachineData.length, ...response.data);
  } catch (error) {
    console.error("搜索失败：", error);
  }
}
//清除
const clear = () => {
  searchKey.cameraId = '';
  searchKey.trackId = '';
  getGunmachineData();
}

onMounted(() => {
  getGunmachineData();
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

.ops-page-header { flex:0 0 auto;min-height:80px;margin-bottom:10px;padding:6px 6px 14px;border-bottom:1px solid #cfdeeb; }
.ops-eyebrow { color:#157da6;font-size:11px;letter-spacing:1.4px;font-weight:700; }
.ops-page-header h1 { margin:4px 0 2px;color:#153b5b;font-size:24px;line-height:1.2; }
.ops-page-header p { margin:0;color:#6e879a;font-size:12px; }
.list { width:100%;height:100%;min-height:0;display:flex;flex-direction:column;padding:16px;background:linear-gradient(140deg,#f1f6fa,#f8fbfd); }
.search { flex:0 0 auto;width:100%;height:auto;min-height:66px;margin:0 0 12px;padding:12px 16px;border:0;border-left:3px solid #54afcf;border-radius:5px;background:#fff;box-shadow:0 6px 20px rgba(21,63,99,.045); }
.camera-list { flex:1;min-height:0;width:100%;height:auto;margin:0;padding:0;overflow:auto;background:#fff;border:0;border-top:2px solid #58b5d2;border-radius:8px;box-shadow:0 8px 30px rgba(21,63,99,.05); }
.camera-list :deep(.el-table) { --el-table-header-bg-color:#edf5fa;--el-table-row-hover-bg-color:#f0f8fb; }
</style>