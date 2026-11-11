<template>
  <div class="list">
    <div class="search">
      <div class="search-box">
        <el-input
            v-model="cameraSearchKeyword"
            style="width: 240px"
            placeholder="请输入"
            :suffix-icon="Search"
        />
        <div class="search-btn">
          <el-button round @click="search">搜索</el-button>
        </div>
        <div class="clear-btn">
          <el-button round @click="clear">清除</el-button>
        </div>
      </div>
      <div class="add">
        <el-button round @click="addFormVisible = true">新增</el-button>
      </div>
    </div>
    <div class="camera-list">
      <el-table :data="CameraData" style="width: 100%; height: 540px;">
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
            <el-tag :type="row.status === '0' ? 'success' : 'danger'">
              {{ row.status === '0' ? '在线' : '掉线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="ip" min-width="10%" align="center"/>
        <el-table-column prop="type" label="类型" min-width="10%" align="center">
          <template #default="{ row }">
            <el-tag :type="row.type === 0 ? 'primary' : 'warning'">
              {{ row.type === 0 ? '球机型' : '枪机型' }}
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
        <el-form :model="form">
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
import {ref, reactive, onMounted, onUnmounted} from 'vue'
import {Search} from '@element-plus/icons-vue'
import {ElMessage} from 'element-plus'
import {getAllCameras, insertCamera, updateCameraById, deleteCameraById, searchCamera} from "@/http/api/camera.js"
import {getCurrentInstance} from 'vue';

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
const getCameraData = async () => {
  try {
    const response = await getAllCameras();
    CameraData.splice(0, CameraData.length, ...response.data);

  } catch (error) {
    console.error('获取摄像头列表失败:', error);
  }
}
//搜索
const cameraSearchKeyword = ref("")
const search = async () => {
  try {
    const response = await searchCamera(cameraSearchKeyword.value);
    CameraData.splice(0, CameraData.length, ...response.data);
  } catch (error) {
    console.error("搜索失败：", error);
  }
}
//清除搜索
const clear = () => {
  cameraSearchKeyword.value = '';
  getCameraData();
}

//使用websocket实时获取摄像头的状态
let ws = null;

//连接 WebSocket
const connectWebSocket = () => {
  if (ws) {
    ws.close();
  }

  //  WebSocket 服务器地址
  ws = new WebSocket("ws://localhost:8081/ws/cameraStatus");

  ws.onopen = () => {
    console.log("WebSocket 连接成功");
  };

  ws.onmessage = (event) => {
    try {
      const cameraStatusUpdate = JSON.parse(event.data);
      updateCameraStatus(cameraStatusUpdate);
    } catch (error) {
      console.error("WebSocket 数据解析失败:", error);
    }
  };

  ws.onclose = () => {
    console.log("WebSocket 连接已关闭");
  };

  ws.onerror = (error) => {
    console.error("WebSocket 错误:", error);
  };
};

// 更新摄像头状态
const updateCameraStatus = (cameraList) => {
  cameraList.forEach(updatedCamera => {
    const index = CameraData.findIndex(c => c.id === updatedCamera.id);
    if (index !== -1) {
      CameraData[index].status = updatedCamera.status;
    }
  });
};


onMounted(() => {
  getCameraData();
  connectWebSocket();
})

onUnmounted(() => {
  if (ws) {       //组件卸载时，关闭ws
    ws.close();
  }
});


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