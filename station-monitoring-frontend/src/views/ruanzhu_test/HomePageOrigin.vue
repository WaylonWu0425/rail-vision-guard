<template>
  <div id="home">
    <nav>
      <el-menu
          :default-active="activeIndex"
          class="el-menu-demo"
          mode="horizontal"
          background-color="#fff"
          :ellipsis="false"
          @select="handleSelect"
          router
      >
        <el-menu-item index="/">
          <div class="img-box" @click.stop="refreshHome">
            <div class="img">
              <img
                  style="width: 28px"
                  alt="车站视频管理系统"
                  src="../assets/logo.png"
              />
            </div>
            <!--            <div class="title">车站监控系统</div>-->
            <!--            <div class="title">车站视频管理系统</div>-->
            <!--            <div class="title">车站异物检测系统</div>-->
            <div class="title">视界巡警</div>

          </div>
        </el-menu-item>
        <div class="avatar-box">
          <img v-if="imageUrl" :src="imageUrl" class="avatar"/>
        </div>
        <el-sub-menu index="1">
          <template #title>{{ store.state.user.userInfo.username }}</template>
          <el-menu-item index="/userProfile">个人中心</el-menu-item>
          <el-menu-item index="1-2" @click="logOut()">退出登录</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </nav>
    <div class="main-container">
      <!-- 侧边栏 -->
      <Sidebar></Sidebar>
      <!-- 内容区域 -->
      <div class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade">
            <component :is="Component" v-if="Component"/>
            <div v-else class="cameraInfo">
              <div class="dashboard">
                <!-- 统计信息卡片 -->
                <div class="number">
                  <el-row :gutter="20">
                    <el-col :span="8">
                      <el-card class="stat-card">
                        <div class="stat-content">
                          <span>摄像头总数</span>
                          <el-tag type="info">{{ cameras.length }}</el-tag>
                        </div>
                      </el-card>
                    </el-col>
                    <el-col :span="8">
                      <el-card class="stat-card">
                        <div class="stat-content">
                          <span>在线数量</span>
                          <el-tag type="success">{{ onlineCount }}</el-tag>
                        </div>
                      </el-card>
                    </el-col>
                    <el-col :span="8">
                      <el-card class="stat-card">
                        <div class="stat-content">
                          <span>离线数量</span>
                          <el-tag type="danger">{{ offlineCount }}</el-tag>
                        </div>
                      </el-card>
                    </el-col>
                  </el-row>
                </div>
                <div class="display">
                  <div class="charts">
                    <div ref="barChart" class="chart"></div>
                    <div ref="pieChart" class="chart"></div>
                  </div>

                  <div class="table">
                    <div class="table-content">
                      <el-table :data="displayedData" stripe class="tableInfo">
                        <el-table-column prop="name" label="名称" min-width="20%"/>
                        <el-table-column prop="status" label="状态" min-width="20%">
                          <template #default="{ row }">
                            <el-tag :type="row.status == 0 ? 'success' : 'danger'">
                              {{ row.status == 0 ? '在线' : '掉线' }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="ip" label="ip" min-width="20%"/>
                        <!-- <el-table-column label="位置">
                          <template #default="{ row }">
                            <div>水平: {{ row.ip }}m</div>
                            <div>垂直: {{ row.ip }}m</div>
                            <div>变焦: {{ row.ip }}</div>
                          </template>
                        </el-table-column> -->
                        <el-table-column prop="port" label="端口" min-width="20%"/>
                      </el-table>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onActivated, watch, onUnmounted, nextTick, reactive} from 'vue'
import Sidebar from './Sidebar.vue'
import {logout} from '@/http/api/user.js'
import router from '@/router/index'
import {getAvatar} from '@/http/api/user'
import {getAllCameras, countOnlineCameras, countOfflineCameras, getWarningStatistics} from '@/http/api/camera.js'
import {getCameraAlarmByDay} from '@/http/api/camerAlarm.js'
import {useStore} from 'vuex';
import * as echarts from 'echarts';
import {
  Document,
  Menu as IconMenu,
  Location,
  Setting,
} from '@element-plus/icons-vue'


const isCollapse = ref(true)
//登出
const store = useStore();
const logOut = async () => {
  const response = await logout(store.state.user.userInfo.id);
  if (response) {
    var d = new Date();
    d.setTime(d.getTime() - 1);
    var expireTime = d.toGMTString()
    var expires = ";expires=" + expireTime;
    document.cookie = "url=http://localhost:3001;" + expires + ";path=/"
  }
  router.push('/login');
}
//头像
const imageUrl = ref('');
const fetchAvatar = async () => {
  const response = await getAvatar(store.state.user.userInfo.avatar);
  if (response.data instanceof Blob) {
    imageUrl.value = URL.createObjectURL(response.data)
  } else {
    console.error('API 返回的数据不是 Blob:', response.data);
  }
}
watch(store.state.user.userInfo, () => {
  fetchAvatar()
})

//表格数据
const cameras = reactive([]);
const displayedData = reactive([]) // 初始数据
const getCameraData = async () => {
  try {
    const response = await getAllCameras();
    cameras.splice(0, cameras.length, ...response.data);
    displayedData.splice(0, displayedData.length, ...cameras); // 初始化显示前 5 条数
  } catch (error) {
    console.error('获取摄像头列表失败:', error);
  }
}

// 表格滚动逻辑
const scrollTable = () => {
  if (cameras.length > 1) {
    const firstRow = cameras.shift(); // 移除第一行
    cameras.push(firstRow); // 添加到最后
    displayedData.splice(0, displayedData.length, ...cameras.slice(0, 5)); // 更新显示的数据
  }
};

setInterval(scrollTable, 2000);// 每 2 秒滚动一次

const onlineCount = ref(0)
const offlineCount = ref(0)
const getCountOnlineAndOfflineCameras = async () => {
  const response = await countOnlineCameras();
  const response2 = await countOfflineCameras();
  onlineCount.value = response.data;
  offlineCount.value = response2.data;

  updateCharts();
}
setInterval(getCountOnlineAndOfflineCameras, 5000);// 每 5 秒获取一次摄像头的状态


//统计图
const barChart = ref();
const pieChart = ref();
let barInstance = null;
let pieInstance = null;

// 添加警报数据存储
const cameraAlarms = reactive([]);
const dangerAlarms = reactive([]);

// 获取最近7天的摄像头警报和危险警报数据
const getAlarmStatisticsData = async () => {
  try {
    // 获取摄像头警报数据
    const cameraAlarmResponse = await getCameraAlarmByDay();
    if (cameraAlarmResponse.data) {
      cameraAlarms.splice(0, cameraAlarms.length, ...cameraAlarmResponse.data.data);
    }

    // 获取危险警报数据
    // const dangerAlarmResponse = await getWarningStatistics();
    // if (dangerAlarmResponse.data) {
    //   dangerAlarms.splice(0, dangerAlarms.length, ...dangerAlarmResponse.data);
    // }

    // 更新图表
    updateCharts();
  } catch (error) {
    console.error("获取警报统计数据失败:", error);
  }
};

// 获取最近7天的日期数组
const getLast7Days = () => {
  const dates = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const formattedDate = date.toISOString().slice(0, 10);
    dates.push(formattedDate);
  }
  return dates;
};

// 根据日期获取警报数量，如果没有则返回0
const getAlarmCountByDate = (alarms, date) => {
  const alarm = alarms.find(a => a.alarm_date === date);
  return alarm ? alarm.alarm_count : 0;
};

// 窗口/容器变化时重新调整图表大小
const handleResize = () => {
  if (barInstance) barInstance.resize();
  if (pieInstance) pieInstance.resize();
};

//销毁图表实例
const disposeCharts = () => {
  if (barInstance) {
    echarts.dispose(barInstance);
    barInstance = null;
  }
  if (pieInstance) {
    echarts.dispose(pieInstance);
    pieInstance = null;
  }
};

// 初始化 ECharts
const initCharts = async () => {
  await nextTick(); // 确保 DOM 渲染完成
  if (!barChart.value || !pieChart.value) {
    console.error('图表容器未找到');
    return;
  }
  // 销毁旧实例
  disposeCharts();
  // 初始化新实例
  barInstance = echarts.init(barChart.value);
  pieInstance = echarts.init(pieChart.value);
  // 添加错误处理
  if (!barInstance || !pieInstance) {
    throw new Error('图表初始化失败');
  } else {
    console.log('图表初始化成功!!');
  }
  // 更新图表数据
  updateCharts();
  // 监听窗口变化
  window.addEventListener('resize', handleResize);
};


//使用websocket实时获取摄像头的状态
let ws = null;

//连接 WebSocket
const connectWebSocket = () => {
  if (ws) {
    ws.close();
  }

  // 替换 WebSocket 服务器地址
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
    const index = displayedData.findIndex(c => c.id === updatedCamera.id);
    if (index !== -1) {
      displayedData[index].status = updatedCamera.status;
    }
  });
};


// 更新图表数据
const updateCharts = () => {
  if (!barInstance || !pieInstance) {
    console.error("图表实例未初始化");
    return;
  }

  // 渐变色定义
  const blueGradient = new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    {offset: 0, color: '#83bff6'},
    {offset: 0.5, color: '#188df0'},
    {offset: 1, color: '#188df0'}
  ]);

  const redGradient = new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    {offset: 0, color: '#ff9a9e'},
    {offset: 1, color: '#F56C6C'}
  ]);

  // 柱状图配置
  const barOption = {
    backgroundColor: 'transparent',
    title: {
      text: "摄像头状态统计",
      left: "center",
      textStyle: {
        color: '#3a7bd5',
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      top: '25%',
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: "category",
      data: ["在线", "离线"],
      axisLine: {
        lineStyle: {
          color: '#a7d7f9'
        }
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#3a7bd5'
      }
    },
    yAxis: {
      type: "value",
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: '#e6f2ff',
          type: 'dashed'
        }
      },
      axisLabel: {
        color: '#3a7bd5'
      }
    },
    series: [
      {
        type: "bar",
        data: [
          {
            value: onlineCount.value,
            itemStyle: {
              color: blueGradient
            }
          },
          {
            value: offlineCount.value,
            itemStyle: {
              color: redGradient
            }
          }
        ],
        barWidth: '40%',
        itemStyle: {
          borderRadius: [5, 5, 0, 0]
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0,123,255,0.5)'
          }
        },
        animationDuration: 1500,
        animationEasing: 'elasticOut'
      }
    ],
    // 水波纹动画效果
    graphic: {
      type: 'group',
      children: [
        {
          type: 'image',
          style: {
            image: 'data:image/png;base64,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',
            width: 20,
            height: 20,
            x: '80%',
            y: '10%',
            opacity: 0.6
          }
        }
      ]
    }
  };

  // 获取最近7天的日期数组
  const last7Days = getLast7Days();

  // 计算每天的警报数据
  const cameraAlarmData = last7Days.map(date => getAlarmCountByDate(cameraAlarms, date));
  const dangerAlarmData = last7Days.map(date => getAlarmCountByDate(dangerAlarms, date));

  // 折线图配置 - 修改为显示警报数据
  const pieOption = {
    backgroundColor: 'transparent',
    title: {
      text: "近7天警报趋势",
      left: "center",
      textStyle: {
        color: '#3a7bd5',
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: ['摄像头警报', '危险警报'],
      bottom: 'bottom',
      textStyle: {
        color: '#3a7bd5'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: last7Days,
      axisLine: {
        lineStyle: {
          color: '#a7d7f9'
        }
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#3a7bd5',
        formatter: (value) => {
          // 只显示月-日
          return value.substring(5);
        }
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: '#e6f2ff',
          type: 'dashed'
        }
      },
      axisLabel: {
        color: '#3a7bd5'
      }
    },
    series: [
      {
        name: '摄像头警报',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#188df0',
          borderWidth: 2,
          borderColor: '#fff'
        },
        lineStyle: {
          width: 3,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            {offset: 0, color: '#83bff6'},
            {offset: 1, color: '#188df0'}
          ])
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: 'rgba(24, 141, 240, 0.3)'},
            {offset: 1, color: 'rgba(24, 141, 240, 0.1)'}
          ])
        },
        data: cameraAlarmData,
        animationDuration: 1500,
        animationEasing: 'elasticOut'
      },
      {
        name: '危险警报',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#F56C6C',
          borderWidth: 2,
          borderColor: '#fff'
        },
        lineStyle: {
          width: 3,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            {offset: 0, color: '#ff9a9e'},
            {offset: 1, color: '#F56C6C'}
          ])
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: 'rgba(245, 108, 108, 0.3)'},
            {offset: 1, color: 'rgba(245, 108, 108, 0.1)'}
          ])
        },
        data: dangerAlarmData,
        animationDuration: 1500,
        animationEasing: 'elasticOut'
      }
    ]
  };

  try {
    barInstance.setOption(barOption);
    pieInstance.setOption(pieOption);
  } catch (error) {
    console.error("更新图表失败:", error);
  }
};


onMounted(() => {
  window.addEventListener('resize', handleResize)
  // 只做一次性的监听
})

onActivated(async () => {
  await getCameraData()
  await getCountOnlineAndOfflineCameras()
  await getAlarmStatisticsData()
  await nextTick() // 等待DOM渲染
  initCharts()
  connectWebSocket()
})

const refreshHome = () => {
  if (window.location.pathname === '/' || window.location.hash === '#/') {
    window.location.reload();
  } else {
    window.location.href = '/';
  }
}

</script>

<style scoped>
.el-menu--horizontal > .el-menu-item:nth-child(1) {
  margin-right: auto;
}

.el-menu--horizontal {
  --el-menu-horizontal-height: 6vh;
  box-shadow: 0 2px 10px rgba(0, 123, 255, 0.1);
}

.main-container {
  display: flex;
  background-color: #f0f8ff;
}

.content {
  position: relative;
  display: flex;
  flex-grow: 1;
  min-width: 0;
}

.avatar {
  position: absolute;
  height: 36px;
  width: 36px;
  object-fit: cover;
  border-radius: 50%;
  top: 2px;
  right: 150px;
  border: 2px solid #a7d7f9;
  box-shadow: 0 2px 5px rgba(0, 123, 255, 0.2);
  transition: all 0.3s ease;
}

.avatar:hover {
  transform: scale(1.05);
}

.cameraInfo {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 98%;
  height: 96%;
  background-color: #e6f2ff;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 123, 255, 0.15);
}

.dashboard {
  padding: 20px;
  background: linear-gradient(135deg, #e6f2ff, #d9ebff);
  color: #2c3e50;
  height: 100%;
  width: 100%;
  transition: all 0.3s ease-in-out;
  border-radius: 12px;
}

.number {
  width: 100%;
  height: 15%;
}

.stat-card {
  background: rgba(255, 255, 255, 0.8) !important;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.12);
  transition: all 0.3s ease;
  border: 1px solid #d1e5f8;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 15px rgba(0, 123, 255, 0.2);
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  padding: 15px;
  color: #3a7bd5;
}

.display {
  display: flex;
  flex-direction: row;
  height: 85%;
  gap: 20px;
}

.charts {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-top: 1%;
  height: 100%;
  width: 50%;
  gap: 20px;
}

.chart {
  width: 100%;
  height: 47%;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
  padding: 15px;
  border: 1px solid #d1e5f8;
  transition: all 0.3s ease;
}

.chart:hover {
  box-shadow: 0 6px 15px rgba(0, 123, 255, 0.18);
  transform: translateY(-3px);
}

.table {
  height: 100%;
  width: 50%;
  padding-top: 1%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.table-content {
  overflow: hidden;
  width: 95%;
  height: 99%;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
  background-color: rgba(255, 255, 255, 0.8);
  border: 1px solid #d1e5f8;
  transition: all 0.3s ease;
}

.table-content:hover {
  box-shadow: 0 6px 15px rgba(0, 123, 255, 0.18);
}

.tableInfo {
  width: 100%;
  height: 100%;
  transition: transform 0.5s ease;
}

/* 添加淡入淡出过渡效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 新增按钮样式 */
:deep(.el-button) {
  background-color: #a7d7f9;
  border-color: #a7d7f9;
  color: #2c3e50;
}

:deep(.el-button:hover) {
  background-color: #7fc1f5;
  border-color: #7fc1f5;
}

/* 优化表格样式 */
:deep(.el-table) {
  background-color: transparent;
}

:deep(.el-table th) {
  background-color: #d1e5f8;
  color: #3a7bd5;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: #e6f2ff;
}

:deep(.el-table tr:hover > td) {
  background-color: #d9ebff !important;
}

.img-box {
  display: flex;
}

.img-box .img {
  width: 28px;
  position: relative;
}

.img-box .img img {
  position: absolute;
  top: 24%;
}
</style>