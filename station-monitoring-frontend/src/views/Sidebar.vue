<template>
  <div class="sidebar">
    <el-menu
        default-active="2"
        class="el-menu-vertical-demo"
        :collapse="isCollapse"
        :router="true"
    >
      <div class="isCollapseBtn">
        <el-radio-group v-model="isCollapse" class="btns">
          <!-- <div class="btn" :value="false" v-if="isCollapse"><el-icon><DArrowRight /></el-icon></div>
          <div class="btn" :value="true" v-if="!isCollapse"><el-icon><DArrowLeft /></el-icon></div> -->

          <el-radio-button :value="false" v-if="isCollapse">
            <el-icon>
              <DArrowRight/>
            </el-icon>
          </el-radio-button>
          <el-radio-button :value="true" v-if="!isCollapse">
            <el-icon>
              <DArrowLeft/>
            </el-icon>
          </el-radio-button>
        </el-radio-group>
      </div>

      <!--      实时预览-->
      <el-menu-item index="/monitoringscreen">
        <el-icon>
          <View/>
        </el-icon>
        <template #title>实时预览</template>
      </el-menu-item>

      <!--      图像监测-->
<!--      <el-menu-item index="/imageDetection">-->
<!--        <el-icon>-->
<!--          <Monitor/>-->
<!--        </el-icon>-->
<!--        <template #title>图像检测</template>-->
<!--      </el-menu-item>-->

      <!--      视频管理-->
      <el-menu-item index="/video">
        <el-icon>
          <VideoCamera/>
        </el-icon>
        <template #title>视频管理</template>
      </el-menu-item>


      <!--      摄像头管理-->
      <el-menu-item index="/cameramanagement">
        <el-icon>
          <Camera/>
        </el-icon>
        <template #title>摄像头管理</template>
      </el-menu-item>

      <!-- 报警信息-->
<!--      <el-sub-menu index="3">-->
<!--        <template #title>-->
<!--          <el-icon>-->
<!--            <Bell/>-->
<!--          </el-icon>-->
<!--          <span>报警信息</span>-->
<!--        </template>-->
<!--        <el-menu-item-group>-->
<!--          <el-menu-item index="/alarm">查看警报</el-menu-item>-->
<!--          <el-menu-item index="/alarmrecord">历史记录</el-menu-item>-->
<!--        </el-menu-item-group>-->
<!--      </el-sub-menu>-->

      <!--      预置点管理-->
<!--      <el-sub-menu index="5">-->
<!--        <template #title>-->
<!--          <el-icon>-->
<!--            <Operation/>-->
<!--          </el-icon>-->
<!--          <span>预置点管理</span>-->
<!--        </template>-->
<!--        <el-menu-item-group>-->
<!--          <el-menu-item index="/ballMachine">球机预置点</el-menu-item>-->
<!--          <el-menu-item index="/gunMachine">枪机预置点</el-menu-item>-->
<!--          <el-menu-item index="/stockTrack">股道预置点</el-menu-item>-->
<!--          <el-menu-item index="/switch">道岔预置点</el-menu-item>-->
<!--        </el-menu-item-group>-->
<!--      </el-sub-menu>-->

      <!--      数据统计-->
<!--      <el-menu-item index="/DataStatistics">-->
<!--        <el-icon>-->
<!--          <DataLine/>-->
<!--        </el-icon>-->
<!--        <template #title>数据统计</template>-->
<!--      </el-menu-item>-->

      <!--      用户管理-->
      <el-menu-item index="/userManagement">
        <el-icon>
          <User/>
        </el-icon>
        <template #title>用户管理</template>
      </el-menu-item>

      <!--      AI对话-->
      <el-menu-item index="/aiChat">
        <el-icon>
          <ChatDotRound />
        </el-icon>
        <template #title>AI助手</template>
      </el-menu-item>

      <!-- 管理员(role=1)才能看到作业任务 -->
      <el-menu-item v-if="userRole === '1'" index="/jobManagement">
        <el-icon>
          <DocumentRemove/>
        </el-icon>
        <template #title>作业任务</template>
      </el-menu-item>

      <!-- 操作员(role=0)才能看到我的任务 -->
      <el-menu-item v-if="userRole === '0'" index="/employeeTask">
        <el-icon>
          <DocumentRemove/>
        </el-icon>
        <template #title>我的任务</template>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import {ref, computed} from 'vue'
import {useStore} from 'vuex'
import {
  User,
  Menu as IconMenu,
  Operation,
  DataLine,
  View,
  Camera,
  VideoCamera,
  Bell,
  DArrowRight,
  DArrowLeft,
  Warning,
  Monitor,
  DocumentRemove, ChatDotRound
} from '@element-plus/icons-vue'

const store = useStore()
const isCollapse = ref(true)

// 获取用户角色
const userRole = computed(() => store.getters['user/getUserRole'])
</script>

<style scoped>
.el-menu--horizontal > .el-menu-item:nth-child(1) {
  margin-right: auto;
}

.el-menu--horizontal {
  --el-menu-horizontal-height: 50px;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 180px;
  min-height: 94vh;
}

.el-menu-vertical-demo:not(.el-menu--expand) {
  min-height: 94vh;
}

.isCollapseBtn {
  position: relative;
  width: 100%;
  height: 40px;
}

.btns {
  position: absolute;
  top: 0;
  right: 8px;
}
</style>