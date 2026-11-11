<template>
  <div class="list">
    <header class="ops-page-header">
      <div><span class="ops-eyebrow">DEVICE REGISTRY / 接入管理</span><h1>摄像头管理</h1><p>检索、维护和检查摄像头接入信息。</p></div>
      <div class="ops-header-mark"><span>02</span><small>设备管理</small></div>
    </header>
    <div class="search">
      <div class="search-box">
        <el-input
            v-model="cameraSearchKeyword"
            class="camera-search-input"
            placeholder="按名称或编号搜索"
            :suffix-icon="Search"
            clearable
            @keyup.enter="search"
        />
        <div class="search-btn">
          <el-button type="primary" round @click="search">搜索</el-button>
        </div>
        <div class="clear-btn">
          <el-button round @click="clear">清除</el-button>
        </div>
      </div>
      <div class="add">
        <el-button type="primary" plain round @click="addFormVisible = true">新增摄像头</el-button>
      </div>
    </div>
    <div class="camera-list" :aria-busy="loadingCameras">
      <el-table v-loading="loadingCameras" :data="CameraData" style="width: 100%; height: 100%;" empty-text="暂无摄像头数据">
        <el-table-column fixed prop="id" label="序号" min-width="5%">
          <template #default="{ $index }">
            <!-- $index 从 0 开始，因此 +1 使 id 从 1 开始 -->
            {{ $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="8%" align="center"/>
        <el-table-column prop="productNumber" label="产品编号" min-width="8%" align="center"/>
        <el-table-column prop="status" label="状态" min-width="8%" align="center">
          <template #default="{ row }">
            <RailSignal class="rail-table-signal" :state="cameraRailState(row.status)" />
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="ip" min-width="10%" align="center"/>
        <el-table-column prop="type" label="类型" min-width="10%" align="center">
          <template #default="{ row }">
            <el-tag :type="Number(row.type) === 0 ? 'primary' : 'warning'">
              {{ Number(row.type) === 0 ? '球机型' : '固定枪机' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="添加时间" min-width="15%" :formatter="formatTime" align="center"/>
        <el-table-column fixed="right" label="操作" min-width="10%" align="center">
          <template #default="{row}">
            <el-button link type="primary" size="middle" @click=editData(row)>编辑</el-button>
            <el-button link type="primary" size="middle" @click=deleteData(row.id)>删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="addForm">
      <el-dialog v-model="addFormVisible" title="添加摄像头" width="500">
        <el-form :model="addForm">
          <el-form-item label="名称" :label-width="formLabelWidth">
            <el-input v-model="addForm.name" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="IP" :label-width="formLabelWidth">
            <el-input v-model="addForm.ip" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="产品编号" :label-width="formLabelWidth">
            <el-input v-model="addForm.productNumber" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="类型" :label-width="formLabelWidth">
            <el-select v-model="addForm.type" placeholder="请选择" style="width: 100%">
              <el-option
                  v-for="item in options"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="账号" :label-width="formLabelWidth">
            <el-input v-model="addForm.username" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="密码" :label-width="formLabelWidth">
            <el-input v-model="addForm.password" autocomplete="off" show-password="true"/>
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="addFormVisible = false">取消</el-button>
            <el-button type="primary" @click=addCamera()>确认</el-button>
          </div>
        </template>
      </el-dialog>
    </div>
    <div class="editForm">
      <el-dialog v-model="editFormVisible" title="更改摄像头" width="500">
        <el-form :model="editForm">
          <el-form-item label="名称" :label-width="formLabelWidth">
            <el-input v-model="editForm.name" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="IP" :label-width="formLabelWidth">
            <el-input v-model="editForm.ip" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="产品编号" :label-width="formLabelWidth">
            <el-input v-model="editForm.productNumber" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="账号" :label-width="formLabelWidth">
            <el-input v-model="editForm.username" autocomplete="off"/>
          </el-form-item>
          <el-form-item label="密码" :label-width="formLabelWidth">
            <el-input v-model="editForm.password" autocomplete="off" show-password="true"/>
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="editFormVisible = false">取消</el-button>
            <el-button type="primary" @click=editCamera()>确认</el-button>
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
            <el-button type="primary" @click=deleteCamera()>
              确认
            </el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import RailSignal from '@/components/RailSignal.vue'
import { cameraRailState } from '@/utils/railPresentation'
import {ref, reactive, onMounted, onUnmounted} from 'vue'
import {Search} from '@element-plus/icons-vue'
import {ElMessage} from 'element-plus'
import {getAllCameras, insertCamera, updateCameraById, deleteCameraById, searchCamera} from "@/http/api/camera.js"
import {getCurrentInstance} from 'vue';
import {subscribeCameraStatus} from '@/services/cameraStatus';

// 获取全局 `formatDate` 方法
const {appContext} = getCurrentInstance();
const formatDate = appContext.config.globalProperties.$formatDate;

// 定义格式化方法
const formatTime = (row, column, cellValue) => {
  if (!cellValue) return '无时间';
  return formatDate(cellValue, 'YYYY-MM-DD HH:mm:ss'); // 这里可以自定义格式
};

const formLabelWidth = '140px'
//添加摄像头
const addFormVisible = ref(false)
const addForm = reactive({
  name: '',
  ip: '',
  productNumber: '',
  track: '',
  type: '',
  username: '',
  password: '',
})
const addCamera = async () => {
  try {
    const response = await insertCamera(addForm);
    if (response.data.success) {
      ElMessage({
        message: '摄像头添加成功',
        type: 'success',
        plain: true,
      })
      addFormVisible.value = false;
      resetForm();
      getCameraData();
    } else {
      ElMessage({
        message: '摄像头添加失败',
        type: 'error',
        plain: true,
      })
    }
  } catch (error) {
    console.error('添加摄像头失败:', error);
  }
}
const resetForm = () => {
  addForm.name = '';
  addForm.ip = '';
  addForm.productNumber = '';
  addForm.track = '';
  addForm.username = '';
  addForm.password = '';
};
const options = [
  {
    value: 0,
    label: '球机',
  },
  {
    value: 1,
    label: '枪机',
  }
]

//编辑摄像头
const editFormVisible = ref(false)
const editForm = reactive({
  id: '',
  name: '',
  ip: '',
  productNumber: '',
  track: '',
  username: '',
  password: '',
})
const editData = async (row) => {
  editFormVisible.value = true
  editForm.id = row.id;
  editForm.name = row.name;
  editForm.ip = row.ip;
  editForm.productNumber = row.productNumber;
  editForm.track = row.track;
  editForm.username = row.username;
  editForm.password = row.password;
}
const editCamera = async () => {
  console.log(editForm);

  try {
    const response = await updateCameraById(editForm);
    if (response.data.success) {
      ElMessage({
        message: '摄像头信息修改成功',
        type: 'success',
        plain: true,
      })
      editFormVisible.value = false;
      getCameraData();
    }
  } catch (error) {
    console.log('摄像头信息修改该失败:', error);
  }
}
//删除摄像头
const deleteVisible = ref(false)
const cameraId = ref("")
const deleteData = (id) => {
  cameraId.value = id
  deleteVisible.value = true;
}
const deleteCamera = async () => {
  try {
    const response = await deleteCameraById(cameraId.value);
    if (response.data.success) {
      ElMessage({
        message: '摄像头信息删除成功',
        type: 'success',
        plain: true,
      })
      deleteVisible.value = false;
      getCameraData();
    }
  } catch (error) {
    console.log('摄像头信息删除该失败:', error);
  }
}
//获取摄像头
const CameraData = reactive([])
const loadingCameras = ref(false)
const getCameraData = async () => {
  loadingCameras.value = true
  try {
    const response = await getAllCameras();
    CameraData.splice(0, CameraData.length, ...response.data);

  } catch (error) {
    console.error('获取摄像头列表失败:', error);
    ElMessage.error('摄像头列表加载失败，请检查后端服务')
  } finally {
    loadingCameras.value = false
  }
}
//搜索
const cameraSearchKeyword = ref("")
const search = async () => {
  if (!cameraSearchKeyword.value.trim()) {
    getCameraData()
    return
  }
  loadingCameras.value = true
  try {
    const response = await searchCamera(cameraSearchKeyword.value);
    CameraData.splice(0, CameraData.length, ...response.data);
  } catch (error) {
    console.error("搜索失败：", error);
    ElMessage.error('搜索失败，请稍后重试')
  } finally {
    loadingCameras.value = false
  }
}
//清除搜索
const clear = () => {
  cameraSearchKeyword.value = '';
  getCameraData();
}

let unsubscribeCameraStatus = null;

const subscribeToCameraStatus = () => {
  unsubscribeCameraStatus = subscribeCameraStatus(({type, updates}) => {
    if (type === 'update') updateCameraStatus(updates);
    if (type === 'connected') getCameraData();
  });
};

// 更新摄像头状态
const updateCameraStatus = (updates) => {
  const items = Array.isArray(updates) ? updates : [updates];
  items.forEach(updatedCamera => {
    if (!updatedCamera || updatedCamera.id == null) return;
    const index = CameraData.findIndex(c => Number(c.id) === Number(updatedCamera.id));
    if (index !== -1) {
      CameraData[index].status = updatedCamera.status;
    }
  });
};


onMounted(() => {
  getCameraData();
  subscribeToCameraStatus();
})

onUnmounted(() => {
  if (unsubscribeCameraStatus) {
    unsubscribeCameraStatus();
    unsubscribeCameraStatus = null;
  }
});


</script>

<style scoped>
.list {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 0;
  padding: 16px;
  gap: 12px;
  background: #f6f8fb;
}

.search {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  min-height: 64px;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background-color: #fff;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
}

.camera-search-input { width: min(320px, 50vw); }

.camera-list {
  flex: 1 1 auto;
  min-height: 0;
  width: 100%;
  overflow: hidden;
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background-color: #fff;
}

@media (max-width: 720px) {
  .list { padding: 10px; }
  .search { align-items: stretch; flex-direction: column; }
  .search-box { width: 100%; }
  .camera-search-input { width: 100%; }
  .add :deep(.el-button) { width: 100%; }
}

.ops-page-header { flex:0 0 auto;display:flex;justify-content:space-between;align-items:center;min-height:88px;padding:8px 6px 14px;border-bottom:1px solid #cfdeeb; }
.ops-eyebrow { color:#157da6;font-size:11px;letter-spacing:1.5px;font-weight:700; }
.ops-page-header h1 { margin:4px 0 2px;color:#153b5b;font-size:25px;line-height:1.2; }
.ops-page-header p { margin:0;color:#6e879a;font-size:12px; }
.ops-header-mark { display:flex;flex-direction:column;align-items:center;color:#2081ad;opacity:.52; }
.ops-header-mark span { font:italic 800 30px "Segoe UI",sans-serif; }
.ops-header-mark small { font-size:10px; }
.list { background:linear-gradient(140deg,#f1f6fa,#f8fbfd 55%,#edf4fa); }
.search { min-height:70px;border:0;border-left:3px solid #54afcf;border-radius:4px 8px 8px 4px;box-shadow:0 6px 20px rgba(21,63,99,.045); }
.camera-list { padding:0;border:0;border-top:2px solid #58b5d2;border-radius:8px;box-shadow:0 8px 30px rgba(21,63,99,.055); }
.camera-list :deep(.el-table) { --el-table-header-bg-color:#edf5fa;--el-table-row-hover-bg-color:#f0f8fb; }
</style>
