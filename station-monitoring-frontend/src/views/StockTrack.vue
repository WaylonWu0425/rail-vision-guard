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
                <el-input v-model="searchKey.trackId" style="width: 100%" placeholder="请输入" />
              </el-form-item>
              <div class="search-btn">
                  <el-button round @click="search">搜索</el-button>
              </div>
              <div class="clear-btn">
                  <el-button round @click="clear">清除</el-button>
              </div>
          </div>
      </div>
      <div class="camera-list">
          <el-table :data="presetPointData" style="width: 100%; height: 540px;">
              <el-table-column fixed prop="id" label="序号" min-width="5%">
                  <template #default="{ $index }">
                  {{ $index + 1 }}
                  </template>
              </el-table-column>
              <el-table-column prop="trackId" label="轨道ID" min-width="8%" :formatter="formatEmpty"/>
              <el-table-column prop="smallRange" label="监控最低范围" min-width="10%" :formatter="formatEmpty"/>
              <el-table-column prop="wideRange" label="监控最高范围" min-width="10%" :formatter="formatEmpty"/>
              <el-table-column prop="cameraName" label="摄像头名称" min-width="10%" :formatter="formatEmpty"/>
              <el-table-column prop="presetPointId" label="预置点ID" min-width="10%" :formatter="formatEmpty"/>
              <el-table-column prop="panPosition" label="水平座标" min-width="10%" :formatter="formatEmpty"/>
              <el-table-column prop="tiltPosition" label="垂直坐标" min-width="10%" :formatter="formatEmpty"/>
              <el-table-column prop="zoom" label="变焦系数" min-width="10%" :formatter="formatEmpty"/>
          </el-table>
      </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted} from 'vue'
import {ElMessage} from 'element-plus'
import { getAllCameras } from '@/http/api/camera.js'
import { getAllBallmachine, searchBallmachine } from '@/http/api/ballMachine.js'
import { getAllGunmachine, searchGunmachine } from '@/http/api/gunmachine.js'

const formLabelWidth = '140px'

//获取预置点信息
const presetPointData = reactive([])

const getGunmachineData = async()=> {    
  try {
      const getAllBallmachineResp = await getAllBallmachine();
      presetPointData.splice(0, presetPointData.length, ...getAllBallmachineResp.data);
      const getAllGunmachineResp = await getAllGunmachine();
      presetPointData.push(...getAllGunmachineResp.data); 
      
  }catch(error) {
      console.error('获取列表失败:',error);
  }
}

const formatEmpty = (row, column, cellValue)=> {
      return cellValue == null || cellValue === '' ? '无' : cellValue;
    }
//搜索
const CameraList = reactive([])
const getCameraList = async()=> {    
    try {
        const response = await getAllCameras();
        // 将数据转换为 { label, value } 格式
        CameraList.splice(0, CameraList.length, ...response.data.map(camera => ({
            label: camera.name,
            value: camera.id,  
        })));
    }catch(error) {
        console.error('获取摄像头列表失败:',error);
    }
}

const searchKey = reactive({
  cameraId: "",
  trackId:"",
})
const search = async() => {  
  const getAllBallmachineResp = await searchBallmachine(searchKey.cameraId, searchKey.trackId);
  presetPointData.splice(0, presetPointData.length, ...getAllBallmachineResp.data);
  const getAllGunmachineResp = await searchGunmachine(searchKey.cameraId, searchKey.trackId);
  presetPointData.push(...getAllGunmachineResp.data);
}
//清除
const clear = ()=> {
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
.search-btn{
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