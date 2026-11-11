<template>
  <div id="home" class="tech-home">
    <nav class="tech-nav">
      <el-menu
          :default-active="activeIndex"
          class="el-menu-demo tech-menu"
          mode="horizontal"
          background-color="rgba(10, 25, 47, 0.95)"
          :ellipsis="false"
          @select="handleSelect"
          router
      >
        <el-menu-item index="/" class="logo-item">
          <div class="img-box" @click.stop="refreshHome">
            <div class="img">
              <img
                  style="width: 32px"
                  alt="车站视频管理系统"
                  src="../assets/logo.png"
              />
            </div>
            <div class="title tech-title">车站视频管理系统</div>
          </div>
        </el-menu-item>
        <div class="avatar-box">
          <img v-if="imageUrl" :src="imageUrl" class="avatar tech-avatar"/>
        </div>
        <el-sub-menu index="1" class="user-menu">
          <template #title>
            <span class="username">{{ store.state.user.userInfo.username }}</span>
          </template>
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
            <div v-else class="cameraInfo-wrapper">
              <div class="cameraInfo">
                <div class="dashboard">
                  <!-- 统计信息卡片 -->
                  <div class="number">
                    <el-row :gutter="20">
                      <el-col :span="8">
                        <el-card class="stat-card tech-stat-card">
                          <div class="stat-content">
                            <div class="stat-icon">
                              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 2C8.13 2 5 5.13 5 9v4c0 3.87 3.13 7 7 7s7-3.13 7-7V9c0-3.87-3.13-7-7-7z" stroke="#00d4ff" stroke-width="1.5" fill="none"/>
                                <path d="M12 16c-1.66 0-3-1.34-3-3" stroke="#00d4ff" stroke-width="1.5" stroke-linecap="round"/>
                                <circle cx="12" cy="9" r="2" fill="#00d4ff"/>
                              </svg>
                            </div>
                            <div class="stat-info">
                              <span class="stat-label">摄像头总数</span>
                              <span class="stat-value">{{ cameras.length }}</span>
                            </div>
                          </div>
                        </el-card>
                      </el-col>
                      <el-col :span="8">
                        <el-card class="stat-card tech-stat-card">
                          <div class="stat-content">
                            <div class="stat-icon">
                              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <circle cx="12" cy="12" r="9" stroke="#00ff88" stroke-width="1.5" fill="none"/>
                                <path d="M12 8v4l3 3" stroke="#00ff88" stroke-width="1.5" stroke-linecap="round"/>
                                <circle cx="12" cy="12" r="2" fill="#00ff88"/>
                              </svg>
                            </div>
                            <div class="stat-info">
                              <span class="stat-label">在线数量</span>
                              <span class="stat-value">{{ onlineCount }}</span>
                            </div>
                          </div>
                        </el-card>
                      </el-col>
                      <el-col :span="8">
                        <el-card class="stat-card tech-stat-card">
                          <div class="stat-content">
                            <div class="stat-icon">
                              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <circle cx="12" cy="12" r="9" stroke="#ff4757" stroke-width="1.5" fill="none"/>
                                <path d="M9 9L15 15M15 9L9 15" stroke="#ff4757" stroke-width="1.5" stroke-linecap="round"/>
                              </svg>
                            </div>
                            <div class="stat-info">
                              <span class="stat-label">离线数量</span>
                              <span class="stat-value">{{ offlineCount }}</span>
                            </div>
                          </div>
                        </el-card>
                      </el-col>
                    </el-row>
                  </div>
                  <div class="display">
                    <div class="charts">
                      <div ref="barChart" class="chart tech-chart"></div>
                      <div ref="pieChart" class="chart tech-chart"></div>
                    </div>

                    <div class="table">
                      <div class="table-content tech-table-container">
                        <el-table :data="displayedData" stripe class="tableInfo tech-table" :header-cell-style="headerCellStyle">
                          <el-table-column prop="name" label="名称" min-width="20%"/>
                          <el-table-column prop="status" label="状态" min-width="20%">
                            <template #default="{ row }">
                              <div class="status-badge">
                                <span class="status-dot" :class="row.status == 0 ? 'online' : 'offline'"></span>
                                <el-tag :type="row.status == 0 ? 'success' : 'danger'" size="small">
                                  {{ row.status == 0 ? '在线' : '掉线' }}
                                </el-tag>
                              </div>
                            </template>
                          </el-table-column>
                          <el-table-column prop="ip" label="IP地址" min-width="20%"/>
                          <el-table-column prop="port" label="端口" min-width="20%"/>
                        </el-table>
                      </div>
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

  // 渐变色定义 - 科技感配色
  const blueGradient = new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    {offset: 0, color: '#00d4ff'},
    {offset: 0.5, color: '#0099ff'},
    {offset: 1, color: '#0066cc'}
  ]);

  const redGradient = new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    {offset: 0, color: '#ff6b6b'},
    {offset: 1, color: '#ff4757'}
  ]);

  // 柱状图配置
  const barOption = {
    backgroundColor: 'transparent',
    title: {
      text: "摄像头状态统计",
      left: "center",
      textStyle: {
        color: '#00d4ff',
        fontSize: 16,
        fontWeight: '500',
        fontFamily: 'monospace'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      backgroundColor: 'rgba(10, 25, 47, 0.9)',
      borderColor: '#00d4ff',
      borderWidth: 1,
      textStyle: {
        color: '#fff'
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
          color: '#00d4ff'
        }
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#00d4ff',
        fontSize: 12,
        fontWeight: '500'
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
          color: 'rgba(0, 212, 255, 0.2)',
          type: 'dashed'
        }
      },
      axisLabel: {
        color: '#00d4ff'
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
          borderRadius: [8, 8, 0, 0],
          shadowBlur: 10,
          shadowColor: 'rgba(0, 212, 255, 0.5)'
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 20,
            shadowColor: 'rgba(0,212,255,0.8)'
          }
        },
        animationDuration: 1500,
        animationEasing: 'elasticOut'
      }
    ]
  };

  // 获取最近7天的日期数组
  const last7Days = getLast7Days();

  // 计算每天的警报数据
  const cameraAlarmData = last7Days.map(date => getAlarmCountByDate(cameraAlarms, date));
  const dangerAlarmData = last7Days.map(date => getAlarmCountByDate(dangerAlarms, date));

  // 折线图配置 - 科技感风格
  const pieOption = {
    backgroundColor: 'transparent',
    title: {
      text: "近7天警报趋势",
      left: "center",
      textStyle: {
        color: '#00d4ff',
        fontSize: 16,
        fontWeight: '500',
        fontFamily: 'monospace'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#00d4ff'
        }
      },
      backgroundColor: 'rgba(10, 25, 47, 0.9)',
      borderColor: '#00d4ff',
      borderWidth: 1,
      textStyle: {
        color: '#fff'
      }
    },
    legend: {
      data: ['摄像头警报', '危险警报'],
      bottom: 'bottom',
      textStyle: {
        color: '#00d4ff'
      },
      itemWidth: 30,
      itemHeight: 10
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
          color: '#00d4ff'
        }
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#00d4ff',
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
          color: 'rgba(0, 212, 255, 0.2)',
          type: 'dashed'
        }
      },
      axisLabel: {
        color: '#00d4ff'
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
          color: '#00d4ff',
          borderWidth: 2,
          borderColor: '#0a192f'
        },
        lineStyle: {
          width: 3,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            {offset: 0, color: '#00d4ff'},
            {offset: 1, color: '#0099ff'}
          ])
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: 'rgba(0, 212, 255, 0.3)'},
            {offset: 1, color: 'rgba(0, 212, 255, 0.05)'}
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
          color: '#ff4757',
          borderWidth: 2,
          borderColor: '#0a192f'
        },
        lineStyle: {
          width: 3,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            {offset: 0, color: '#ff6b6b'},
            {offset: 1, color: '#ff4757'}
          ])
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: 'rgba(255, 71, 87, 0.3)'},
            {offset: 1, color: 'rgba(255, 71, 87, 0.05)'}
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

// 表格表头样式
const headerCellStyle = {
  background: 'rgba(0, 212, 255, 0.1)',
  color: '#00d4ff',
  borderBottom: '1px solid #00d4ff',
  fontWeight: '500',
  fontSize: '14px'
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
* {
  box-sizing: border-box;
}

.tech-home {
  background: linear-gradient(135deg, #0a192f 0%, #0f2a3f 100%);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.tech-nav {
  flex-shrink: 0;
  position: relative;
  z-index: 100;
}

.el-menu--horizontal > .el-menu-item:nth-child(1) {
  margin-right: auto;
}

.el-menu--horizontal {
  --el-menu-horizontal-height: 60px;
  box-shadow: 0 2px 20px rgba(0, 212, 255, 0.3);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 212, 255, 0.3);
}

.tech-menu {
  --el-menu-bg-color: rgba(10, 25, 47, 0.95) !important;
  --el-menu-text-color: #00d4ff !important;
  --el-menu-active-color: #00d4ff !important;
  --el-menu-hover-bg-color: rgba(0, 212, 255, 0.1) !important;
}

.tech-menu .logo-item {
  background: transparent !important;
  display: flex;
  align-items: center;
  justify-content: center;
}

.img-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  cursor: pointer;
  height: 100%;
  width: 100%;
}

.img-box .img {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.img-box .img img {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 0 5px rgba(0, 212, 255, 0.5));
}

.tech-title {
  font-family: 'Orbitron', monospace;
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  letter-spacing: 2px;
  line-height: 1;
}

.main-container {
  display: flex;
  flex: 1;
  background: linear-gradient(135deg, #0a192f 0%, #0f2a3f 100%);
  overflow: hidden;
  position: relative;
  min-height: 0;
}

.content {
  position: relative;
  display: flex;
  flex-grow: 1;
  min-width: 0;
  overflow: auto;
  padding: 20px;
}

.avatar {
  position: absolute;
  height: 40px;
  width: 40px;
  object-fit: cover;
  border-radius: 50%;
  top: 10px;
  right: 150px;
  border: 2px solid #00d4ff;
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
  transition: all 0.3s ease;
}

.tech-avatar {
  filter: brightness(1.1);
}

.avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.8);
}

.username {
  font-family: monospace;
  font-weight: 500;
  letter-spacing: 1px;
}

.cameraInfo-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cameraInfo {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(10, 25, 47, 0.6), rgba(15, 42, 63, 0.7));
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 212, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.3);
  overflow: auto;
}

.dashboard {
  padding: 20px;
  background: transparent;
  color: #00d4ff;
  height: 100%;
  width: 100%;
  transition: all 0.3s ease-in-out;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.number {
  width: 100%;
  flex-shrink: 0;
}

.stat-card {
  background: rgba(10, 25, 47, 0.6) !important;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.15);
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 212, 255, 0.3);
  backdrop-filter: blur(5px);
}

.tech-stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 212, 255, 0.3);
  border-color: rgba(0, 212, 255, 0.6);
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
}

.stat-icon {
  flex-shrink: 0;
  opacity: 0.9;
}

.stat-info {
  text-align: right;
  flex: 1;
}

.stat-label {
  display: block;
  font-size: 14px;
  color: rgba(0, 212, 255, 0.7);
  margin-bottom: 8px;
  font-family: monospace;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-family: monospace;
}

.display {
  display: flex;
  flex-direction: row;
  flex: 1;
  gap: 20px;
  min-height: 0;
}

.charts {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 50%;
  gap: 20px;
  min-height: 0;
}

.chart {
  width: 100%;
  flex: 1;
  background: rgba(10, 25, 47, 0.6);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);
  padding: 15px;
  border: 1px solid rgba(0, 212, 255, 0.2);
  transition: all 0.3s ease;
  min-height: 200px;
}

.tech-chart:hover {
  box-shadow: 0 6px 25px rgba(0, 212, 255, 0.2);
  transform: translateY(-3px);
  border-color: rgba(0, 212, 255, 0.5);
}

.table {
  width: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 0;
}

.tech-table-container {
  overflow: hidden;
  width: 100%;
  height: 100%;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);
  background-color: rgba(10, 25, 47, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.2);
  backdrop-filter: blur(5px);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.tech-table-container:hover {
  box-shadow: 0 6px 25px rgba(0, 212, 255, 0.2);
  border-color: rgba(0, 212, 255, 0.5);
}

.tableInfo {
  width: 100%;
  height: 100%;
  transition: transform 0.5s ease;
}

.tech-table {
  --el-table-bg-color: transparent !important;
  --el-table-tr-bg-color: transparent !important;
  --el-table-header-bg-color: rgba(0, 212, 255, 0.1) !important;
  --el-table-row-hover-bg-color: rgba(0, 212, 255, 0.1) !important;
  --el-table-border-color: rgba(0, 212, 255, 0.2) !important;
  --el-table-text-color: #00d4ff !important;
}

/* 状态徽章样式 */
.status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-dot.online {
  background: #00ff88;
  box-shadow: 0 0 8px #00ff88;
}

.status-dot.offline {
  background: #ff4757;
  box-shadow: 0 0 8px #ff4757;
}

@keyframes pulse {
  0% {
    opacity: 0.5;
    transform: scale(0.8);
  }
  100% {
    opacity: 1;
    transform: scale(1.2);
  }
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

/* 按钮样式 */
:deep(.el-button) {
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  border: none;
  color: #0a192f;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
}

/* 优化表格样式 */
:deep(.el-table) {
  background-color: transparent;
  color: #00d4ff;
}

:deep(.el-table th) {
  background-color: rgba(0, 212, 255, 0.1);
  color: #00d4ff;
  border-bottom: 1px solid rgba(0, 212, 255, 0.3);
}

:deep(.el-table td) {
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
  color: #b0e0ff;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: rgba(0, 212, 255, 0.05);
}

:deep(.el-table tr:hover > td) {
  background-color: rgba(0, 212, 255, 0.1) !important;
}

/* 标签样式优化 */
:deep(.el-tag--success) {
  background: rgba(0, 255, 136, 0.2);
  border-color: #00ff88;
  color: #00ff88;
}

:deep(.el-tag--danger) {
  background: rgba(255, 71, 87, 0.2);
  border-color: #ff4757;
  color: #ff4757;
}

:deep(.el-tag--info) {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  color: #00d4ff;
}

/* 用户菜单样式 */
:deep(.el-sub-menu__title) {
  color: #00d4ff !important;
}

:deep(.el-sub-menu__title:hover) {
  background-color: rgba(0, 212, 255, 0.1) !important;
}

:deep(.el-menu-item) {
  color: #b0e0ff !important;
}

:deep(.el-menu-item:hover) {
  background-color: rgba(0, 212, 255, 0.1) !important;
  color: #00d4ff !important;
}

/* 滚动条样式 */
.cameraInfo::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.cameraInfo::-webkit-scrollbar-track {
  background: rgba(0, 212, 255, 0.1);
  border-radius: 3px;
}

.cameraInfo::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.5);
  border-radius: 3px;
}

.cameraInfo::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.8);
}
</style>