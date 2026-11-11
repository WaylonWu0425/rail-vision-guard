<template>
    <div class="preset">
        <div class="aside">
            <div class="search">
              <el-select
                v-model="input"
                filterable
                placeholder="Select"
                style="width: 98%"
              >
                <el-option
                v-for="item in options"
                :key="item.value"
                :label="item.label"
                :value="item.value"
                />
              </el-select>
            </div>
            <div class="camera-list">
              <div class="camera-name">摄像头1</div>
              <div class="camera-location">摄像头位置</div>
            </div>
            <div class="control-panel">
              <div class="btns">
                <div class="btn1">
                  <el-button type="primary"><</el-button>
                </div>
                <div class="btn1">
                  <el-button type="primary"><</el-button>
                </div>
                <div class="btn1">
                  <el-button type="primary"><</el-button>
                </div>
                <div class="btn1">
                  <el-button type="primary"><</el-button>
                </div>
              </div>
              <div class="operation">
              </div>
            </div>
        </div>
        <div class="main">
            <video controls class="screen"></video>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { Camera, Search } from '@element-plus/icons-vue'
const input = ref('')

const options = [
  {
    value: 'Option1',
    label: 'Option1',
  },
  {
    value: 'Option2',
    label: 'Option2',
  },
  {
    value: 'Option3',
    label: 'Option3',
  },
  {
    value: 'Option4',
    label: 'Option4',
  },
  {
    value: 'Option5',
    label: 'Option5',
  },
]


</script>

<style scoped>
.preset {
    display: flex;
    width: 100%;
    height: 100%;
}
.aside {
    width: 14%;
    height: 100%;
    padding: 1%;
}
.camera-list {
  display: flex;
  flex-direction: column;
  font-size: 12px;
  width: 98%;
  height: 7%;
  margin-top: 2%;
  padding: 3%;
  background-color: #5ea0ff;
  border-radius: 3px;
  color: #fff;
}
.camera-name {
  font-weight: 600;
}

.main {
  position: relative;
    flex: 1;
    height: 100%;
    background-color: rgba(51, 51, 51,0.3);
}
.screen {
  position: absolute;
  top: 50%;
  flex: 1;
  min-width: 0;
  width: 100%;
  transform: translateY(-50%);
}
</style>