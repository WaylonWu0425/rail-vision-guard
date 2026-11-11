<template>
  <div id="home" class="rail-workspace" :data-entrance="entrance.phase.value" :style="entrance.variables" @pointerdown.capture="interruptEntrance" @keydown.capture="interruptEntrance" :class="{ 'dashboard-route': route.path === '/', 'operations-route': route.path !== '/' }">
    <header class="overview-shell-header">
      <div class="overview-header-main">
        <button class="overview-brand" @click="refreshHome" aria-label="返回综合态势">
          <img src="../assets/guard-logo.webp" alt="" />
          <span><strong>视界巡警</strong><small>RAIL VISION GUARD</small></span>
        </button>
        <div class="overview-page-title">
          <h1>铁路站场监控总览</h1>
          
        </div>
        <div class="overview-header-meta">
          <span class="overview-environment" :class="{ disconnected: route.path === '/' && cameraConnection !== 'connected' }"><i></i>{{ route.path === '/' && cameraConnection !== 'connected' ? (cameraConnection === 'connecting' ? '正在连接设备状态' : '状态连接异常') : (route.path === '/' ? '设备状态已连接' : '业务工作区') }}</span>
          <time class="overview-clock">{{ dashboardDate }}</time>
          <el-dropdown trigger="click" @command="handleHeaderCommand">
            <button class="overview-user" :title="store.state.user.userInfo.username || '个人中心'"><img v-if="imageUrl" :src="imageUrl" alt="" /><el-icon v-else><User /></el-icon></button>
            <template #dropdown><el-dropdown-menu><el-dropdown-item command="/userProfile">个人中心</el-dropdown-item><el-dropdown-item command="logout">退出登录</el-dropdown-item></el-dropdown-menu></template>
          </el-dropdown>
        </div>
      </div>
      <nav class="overview-shortcuts rail-navigation" aria-label="系统快捷导航">
        <div ref="railNavigation" class="overview-shortcut-links rail-navigation-links">
          <span class="rail-stop" :style="railStopStyle" aria-hidden="true"></span>
          <div v-for="item in navigationItems" :key="item.path" class="rail-nav-item">
            <button type="button" class="rail-nav-link"
              :class="{ active: route.path === item.path || item.children?.some(child => child.path === route.path) }"
              :aria-current="route.path === item.path ? 'page' : undefined"
              @click="item.path === '/' ? refreshHome() : router.push(item.path)">
              <RailIcon :name="item.icon" /><span class="rail-nav-label">{{ item.label }}</span>
            </button>
            <el-dropdown v-if="item.children" trigger="click" :popper-options="railSubmenuOptions" @command="handleHeaderCommand">
              <button type="button" class="rail-nav-expand" :aria-label="item.menuLabel" :title="item.menuLabel">
                <RailIcon name="more" />
              </button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="child in item.children" :key="child.path"
                    :command="child.path" :aria-current="route.path === child.path ? 'page' : undefined">
                    {{ child.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
        <span class="overview-shortcut-hint">站场监控 · 设备与事件</span>
      </nav>
    </header>
    <div class="main-container">
      <!-- 侧边栏 -->
      <!-- 内容区域 -->
      <div class="content">
        <router-view v-slot="{ Component }">
          <component :is="Component" v-if="Component"/>
          <div v-else class="cameraInfo">
            <main class="dashboard" aria-label="铁路站场监控总览">

              <section class="status-rail grouped-readouts" aria-label="设备状态概览">
                <div class="device-readout-group">
                  <div class="status-token total"><span class="status-icon"><RailIcon name="camera" /></span><button @click="setDeviceFilter('all')" :aria-pressed="deviceFilter === 'all'"><span class="status-label">接入设备</span><strong class="live-readout" :key="hasDeviceSnapshot ? cameras.length : 'loading'">{{ hasDeviceSnapshot ? cameras.length : '—' }}</strong><small>路</small></button></div>
                  <div class="readout-breakdown">
                    <button v-for="state in ['online','offline','unknown']" :key="state" @click="setDeviceFilter(state)" :aria-pressed="deviceFilter === state"><RailSignal :state="state" /><strong class="live-readout" :key="hasDeviceSnapshot ? state + ({online:onlineCount,offline:offlineCount,unknown:unknownCount})[state] : 'loading-' + state">{{ hasDeviceSnapshot ? ({online:onlineCount,offline:offlineCount,unknown:unknownCount})[state] : '—' }}</strong></button>
                  </div>
                  <span class="readout-caption">{{ deviceCountCaption }}</span>
                </div>
                <div class="status-token alarms"><span class="status-icon"><RailIcon name="alert" /></span><button @click="setAlarmPeriod('week')"><span class="status-label">近七日摄像头告警</span><strong class="live-readout" :key="statsLoading ? 'loading' : alarmStatsFailed ? 'error' : sevenDayAlarmCount">{{ statsLoading || alarmStatsFailed ? '—' : sevenDayAlarmCount }}</strong><small>{{ statsLoading ? '查询中' : alarmStatsFailed ? '暂不可用' : '条' }}</small></button></div>
              </section>

              <div class="dashboard-grid" :class="{ 'device-collapsed': deviceCollapsed }">
                <section class="dash-module device-module" aria-labelledby="device-heading">
                  <div class="module-head">
                    <div><span class="module-index">01 / DEVICES</span><h2 id="device-heading">站场资源</h2></div>
                    <button class="module-link" @click="router.push('/cameramanagement')">设备管理 <span aria-hidden="true">›</span></button>
                  </div>
                  <div class="device-list-title">设备列表 <span>{{ visibleDevices.length }} 路 <button v-if="deviceFilter !== 'all'" @click="setDeviceFilter('all')">清除筛选</button></span></div>
                  <div v-if="visibleDevices.length" class="device-list">
                    <button v-for="camera in visibleDevices" :key="camera.id" class="device-row"
                      :class="{ selected: highlightedDeviceId === String(camera.id) }" :aria-pressed="highlightedDeviceId === String(camera.id)" @click="selectDevice(camera)">
                      <span class="device-face">
                      <span class="device-row-icon"><RailIcon name="camera" /><RailJunction /></span>
                      <span class="rail-nameplate">
                        <span class="rail-id">#{{ camera.id }}</span>
                        <strong class="rail-object-name">{{ cameraDisplayName(camera) }}</strong>
                        <RailSignal :state="deviceState(camera)" />
                        <span class="rail-object-detail">{{ deviceTypeLabel(camera) }}</span>
                      </span>
                      <span class="device-position">{{ String(camera.id) === configuredCameraId() && !sceneFailed ? '定位' : '未定位' }}</span>
                      </span>
                    </button>
                  </div>
                  <div v-else class="module-empty">{{ cameraLoading ? '正在加载设备' : cameraLoadFailed ? '设备列表暂不可用，请检查服务。' : deviceFilter !== 'all' ? '没有符合筛选条件的设备。' : '暂无接入设备，前往设备管理添加。' }}</div>
                  <p v-if="deviceFeedback" class="spatial-feedback" role="status">{{ deviceFeedback }}</p><button v-if="selectedDeviceId" class="module-link" @click="router.push('/monitoringscreen')">进入实时预览 ›</button><div class="side-section"><details><summary class="side-section-title">检测能力</summary><div class="capability-row"><span>人员 / 车辆目标检测</span><small>模型输出需人工核查</small></div><div class="capability-row"><span>固定机位基线比对</span><small>受控场景原型</small></div></details></div>
                  <div class="side-section"><div class="side-section-title"><RailIcon name="alert" />核查工作台 <small>危险告警记录</small></div><button class="module-link resource-review-link" @click="router.push('/alarm')">打开告警中心 ›</button><div class="review-stats"><div><span>待核查</span><strong class="live-readout" :key="alarmLoading ? 'loading' : pendingAlarmCount">{{ alarmLoading || alarmLoadFailed ? '—' : pendingAlarmCount }}</strong></div><div><span>已处理</span><strong class="live-readout" :key="alarmLoading ? 'loading' : handledAlarmCount">{{ alarmLoading || alarmLoadFailed ? '—' : handledAlarmCount }}</strong></div></div></div>
                </section>

                <section class="dash-module scene-module" aria-labelledby="scene-heading">
                  <div class="scene-module-head"><div class="rail-station-sign"><RailIcon name="track" /><h2 id="scene-heading">站台与股道 <small>三维示意</small></h2></div><span>拖动旋转 · 滚轮缩放</span></div>
                  <button class="device-collapse" @click="deviceCollapsed = !deviceCollapsed" :aria-expanded="!deviceCollapsed">{{ deviceCollapsed ? '展开设备栏' : '折叠设备栏' }}</button>
                  <iframe ref="sceneFrame" @error="sceneFailed = true" title="可交互站场三维示意" :src="'/spatial-scene/index.html?embedded=1&theme=navy&entrance=' + entrance.mode.value" loading="eager"></iframe>
                  <div v-if="sceneFailed" class="scene-context" role="status">三维场景加载失败，请刷新重试。</div><div v-else-if="sceneSelection" class="scene-context" role="status">{{ sceneSelection }}</div><div class="scene-disclaimer">场景和设备位置为设计示意，尚未与真实机位空间标定</div>
                </section>

                <aside class="alarm-column event-inspector" :class="{ 'no-current-event': !selectedAlarm }" aria-label="事件证据与告警">
                <section class="dash-module evidence-module" aria-labelledby="evidence-heading">
                  <div class="module-head"><div><span class="module-index">03 / EVIDENCE</span><h2 id="evidence-heading">事件证据</h2></div></div>
                  <div class="evidence-content">
                  <div v-if="selectedDevice" class="device-context">
                    <strong>{{ cameraDisplayName(selectedDevice) }}</strong>
                    <p>设备 #{{ selectedDevice.id }} · <RailSignal :state="deviceState(selectedDevice)" /> · {{ deviceTypeLabel(selectedDevice) }}</p>
                    <p>{{ deviceFeedback }}</p>
                    <button class="module-link" @click="router.push('/monitoringscreen')">进入实时预览 ›</button>
                  </div>
                  <template v-if="selectedAlarm">
                    <div class="rail-ticket">
                      <div class="rail-ticket-top">
                        <span class="rail-id">事件 {{ selectedAlarm.id != null ? '#' + selectedAlarm.id : '编号未记录' }}</span>
                        <RailSignal :state="alarmRailState(selectedAlarm.dealFlag)" />
                      </div>
                      <EventPriority :level="selectedAlarm.level" />
                      <strong class="rail-ticket-title">{{ selectedAlarm.content || selectedAlarmType }}</strong>

                    </div>

                    <section class="evidence-tray" :aria-label="'事件证据托盘 ' + selectedEventKey">
                    <div class="tray-heading"><RailIcon name="recognition" /><strong>证据托盘</strong><span>{{ selectedAlarmDate ? '摄像头告警' : '危险告警' }} #{{ selectedAlarm.id ?? '未记录' }}</span></div>
                    <figure class="evidence-frame" :class="{ 'has-frame': evidenceUrl && failedEvidenceUrl !== evidenceUrl }">
                      <button v-if="evidenceUrl && failedEvidenceUrl !== evidenceUrl" type="button" aria-label="放大证据帧" :disabled="!evidenceImageReady" @click="evidenceDialog.showModal()">
                        <img :key="selectedEventKey + evidenceUrl + ':' + evidenceAttempt" :src="evidenceUrl" alt="带检测标注的事件存档帧" @load="evidenceImageReady = true" @error="failedEvidenceUrl = evidenceUrl" />
                        <span v-if="evidenceImageReady" class="evidence-badge">存档帧 · 点击放大</span>
                      </button>
                      <div v-if="!evidenceUrl || failedEvidenceUrl === evidenceUrl" class="evidence-message" role="status">
                        <strong>{{ evidenceTitle }}</strong>
                        <p>{{ evidenceReason }}</p>
                        <button v-if="canRetryEvidence" type="button" :disabled="evidenceLoading" @click="retryEvidence">重试</button>
                      </div>
                      <span v-else-if="!evidenceImageReady" class="evidence-badge" role="status">正在加载存档帧</span>
                    </figure>
                    <div class="tray-record"><span>检测记录</span><strong>{{ detectionEvidence ? '已关联' : selectedAlarmDate ? '尚未关联' : evidenceLoading ? '查询中' : detectionEvents === null ? '查询失败' : '暂无匹配' }}</strong><small>{{ detectionEvidence ? '事件编号与当前危险告警匹配 · 置信度 ' + evidenceConfidence : '仅展示当前事件的检测证据' }}</small></div>
                    <div class="tray-record"><span>关联录像</span><strong>{{ recordingLoading ? '查询中' : matchedRecording ? '可查看' : '暂不可用' }}</strong><small role="status">{{ recordingFeedback }}</small><button @click="openRecording" :disabled="recordingLoading">{{ matchedRecording ? '查看录像' : '重新匹配' }}</button></div>
                    </section>
<div class="event-key-fields">                      <dl class="rail-ticket-fields">
                        <div><dt>类型</dt><dd>{{ selectedAlarmType }}</dd></div>
                        <div><dt>发生时间</dt><dd><time>{{ formatAlarmTime(selectedAlarm.createTime) }}</time></dd></div>
                        <div><dt>来源设备</dt><dd>{{ eventCameraName(selectedAlarm) }}</dd></div>
                        <div><dt>当前状态</dt><dd><RailSignal :state="alarmRailState(selectedAlarm.dealFlag)" /></dd></div>
                      </dl></div>
                    <details :key="selectedEventKey" class="event-fields"><summary>展开事件字段</summary><dl>
                      <div><dt>设备编号</dt><dd>{{ currentEventCameraId == null ? '未记录' : '#' + currentEventCameraId }}</dd></div>
                      <div><dt>模型置信度</dt><dd>{{ evidenceConfidence }}</dd></div>
                      <div><dt>原始风险值</dt><dd>{{ selectedAlarm.level ?? '未记录' }}</dd></div>
                      <div><dt>处理时间</dt><dd>{{ selectedAlarm.dealTime ? formatAlarmTime(selectedAlarm.dealTime) : '未记录' }}</dd></div>
                      <div><dt>处理人</dt><dd>{{ selectedAlarm.dealUserName || (selectedAlarm.dealUserId != null ? '#' + selectedAlarm.dealUserId : '未记录') }}</dd></div>
                    </dl></details>
                    <EventHistory :key="selectedEventKey" :event="selectedAlarm" />
                    <p class="spatial-feedback" role="status">{{ spatialFeedback }}</p>

                  </template>
                  <div v-else class="context-empty event-empty" role="status"><RailIcon name="recognition" /><strong>{{ activeAlarmFailed ? '事件查询失败' : selectedDeviceId ? '设备尚无关联事件' : '当前范围暂无事件' }}</strong><p>{{ activeAlarmFailed ? '请检查后端连接后重新加载记录。' : selectedDeviceId ? '已选择设备 #' + selectedDeviceId + '，当前列表中没有带该设备 ID 的事件。' : '选择有记录的日期或设备后，截图、录像与核查记录将在这里关联展示。' }}</p></div>
                  </div>
                  <div v-if="selectedAlarm" class="review-actions"><button @click="openRecording" :disabled="recordingLoading">{{ recordingLoading ? '匹配中…' : '关联录像' }}</button><button @click="router.push('/monitoringscreen')">实时预览</button><button class="evidence-link" :class="{ 'instrument-primary': alarmRailState(selectedAlarm.dealFlag) === 'pending', 'entrance-focus': entrance.attentionReady.value && !entrance.focusConfirmed.value && alarmRailState(selectedAlarm.dealFlag) === 'pending' }" @click="openEventReview"><RailIcon name="review" />{{ Number(selectedAlarm.dealFlag) === 1 ? '查看处理记录' : '进入核查处置' }}</button></div>
                </section>
                <section class="dash-module events-module" aria-labelledby="events-heading">
                  <div class="module-head"><div><span class="module-index">LIVE RECORDS</span><h2 id="events-heading">{{ selectedAlarmDate ? '摄像头告警' : '最新危险告警' }}</h2></div><button class="module-link" @click="router.push('/alarmrecord')">全部记录 ›</button></div>
                  <div class="event-scope"><button :class="{ active: alarmScope === 'all' }" :aria-pressed="alarmScope === 'all'" @click="alarmScope = 'all'">全部记录</button><button :class="{ active: alarmScope === 'pending' }" :aria-pressed="alarmScope === 'pending'" @click="alarmScope = 'pending'">待核查 <b>{{ activeAlarmFailed ? '—' : activePendingCount }}</b></button></div>
                  <div v-if="selectedDeviceId" class="device-event-filter">设备 #{{ selectedDeviceId }} 的关联记录 <button @click="selectedDeviceId = null">显示全部设备</button></div>
                  <div class="events-source"><span>{{ selectedAlarmDate ? (selectedAlarmDate === 'week' ? '最近七日' : selectedAlarmDate) + ' · 摄像头告警' : '按发生时间倒序 · 选择事件核查' }}</span><button v-if="selectedAlarmDate" @click="setAlarmPeriod(null)">清除筛选 ×</button></div>
                  <div v-if="filteredRecentAlarms.length" class="recent-event-list" tabindex="0" role="region" aria-label="可滚动的告警记录">
                    <button v-for="alarm in filteredRecentAlarms" :key="alarm.id" class="recent-event" :class="{ selected: selectedAlarm?.id === alarm.id }" :aria-pressed="selectedAlarm?.id === alarm.id" @click="selectAlarm(alarm)">
                      <RailJunction />
                      <span class="recent-event-copy"><time>{{ formatAlarmTime(alarm.createTime) }}</time><strong :title="alarm.content || undefined">{{ alarm.content || (selectedAlarmDate ? '摄像头告警' : alarmTypeLabel(alarm.type)) }}</strong><small>{{ eventCameraName(alarm) }}</small><EventPriority :level="alarm.level" /><small class="rail-sr-only"></small></span>
                      <RailSignal :state="alarmRailState(alarm.dealFlag)" />
                    </button>
                  </div>
                  <div v-else class="module-empty">{{ (selectedAlarmDate ? statsLoading : alarmLoading) ? '正在加载告警记录' : activeAlarmFailed ? '告警记录暂不可用，请检查服务。' : selectedAlarmDate ? '所选日期暂无告警记录' : '暂无告警记录' }}</div>
                </section>
                </aside>

                <section class="dash-module trend-module" aria-labelledby="trend-heading">
                  <div class="module-head">
                    <div><span class="module-index">02 / EVENT TREND</span><h2 id="trend-heading">近七日告警分析</h2></div>
                    <span class="module-caption">摄像头告警 · {{ getLast7Days()[0].slice(5) }} 至 {{ getLast7Days()[6].slice(5) }}</span>
                  </div>
                  <div class="time-ruler"><label for="alarm-day-ruler">记录范围 <strong>{{ !selectedAlarmDate ? '最新危险告警' : selectedAlarmDate === 'week' ? '近七日摄像头告警' : selectedAlarmDate }}</strong></label><input id="alarm-day-ruler" type="range" min="-2" max="6" step="1" :value="rulerDay" :aria-valuetext="rulerDay === -2 ? '最新危险告警' : rulerDay === -1 ? '近七日摄像头告警' : getLast7Days()[rulerDay]" @input="setAlarmPeriod(Number($event.target.value) === -2 ? null : Number($event.target.value) === -1 ? 'week' : getLast7Days()[Number($event.target.value)])" /><div><span>最新 · 七日</span><span>{{ getLast7Days()[0].slice(5) }} — {{ getLast7Days()[6].slice(5) }}</span></div></div>
                  <div v-if="!statsLoading && !alarmStatsFailed && sevenDayAlarmCount" class="trend-summary">
                    <div><small>七日总数</small><strong>{{ sevenDayAlarmCount }}</strong></div>
                    <div><small>已处理</small><span>{{ sevenDayRows.filter(row => Number(row.dealFlag) === 1).length }}</span></div><div><small>待核查</small><span>{{ sevenDayRows.filter(row => alarmRailState(row.dealFlag) === 'pending').length }}</span></div>
                  </div>
                  <div v-show="!statsLoading && !alarmStatsFailed && showAlarmTrend" ref="pieChart" class="trend-chart" role="img" aria-label="近七日摄像头告警趋势图"></div>
                  <ol v-if="!statsLoading && !alarmStatsFailed && sevenDayAlarmCount && !showAlarmTrend" class="sparse-alarm-list" aria-label="近期摄像头告警">
                    <li v-for="alarm in sparseAlarmRows" :key="alarm.id">
                      <button type="button" @click="setAlarmPeriod(alarmDay(alarm.createTime))">
                        <time>{{ formatAlarmTime(alarm.createTime).slice(5) }}</time>
                        <span>{{ eventCameraName(alarm) }}</span>
                        <RailSignal :state="alarmRailState(alarm.dealFlag)" />
                      </button>
                    </li>
                  </ol>
                  <div v-if="statsLoading || alarmStatsFailed || sevenDayAlarmCount === 0" class="analysis-empty" role="status">
                    <RailIcon name="overview" /><div><strong>{{ statsLoading ? '正在查询近七日记录' : alarmStatsFailed ? '告警统计查询失败' : '近七日无摄像头告警' }}</strong><small>{{ statsLoading ? '正在读取摄像头告警列表' : alarmStatsFailed ? '请检查后端连接后重试' : getLast7Days()[0] + ' 至 ' + getLast7Days()[6] + ' · 00 条' }}</small></div>
                    <button v-if="alarmStatsFailed && !statsLoading" @click="getAlarmStatisticsData">重试查询</button>
                  </div>
                </section>


              </div>
            <dialog ref="evidenceDialog" class="evidence-dialog" aria-label="告警证据帧"><button @click="evidenceDialog.close()">关闭</button><img v-if="evidenceUrl" :src="evidenceUrl" alt="告警存档帧" /></dialog>
            </main>
          </div>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, computed, onMounted, onActivated, onDeactivated, watch, onUnmounted, nextTick, reactive} from 'vue'
import {logout} from '@/http/api/user.js'
import {useRoute, useRouter} from 'vue-router'
import {getAvatar} from '@/http/api/user'
import {getAllCameras} from '@/http/api/camera.js'
import {getRecordingMatch} from '@/http/api/recording.js';
import {getAllCameraAlarm} from '@/http/api/camerAlarm.js'
import {getAllAlarmInfo} from '@/http/api/alarm.js'
import {useStore} from 'vuex';
import * as echarts from 'echarts';
import {preloadCorePages} from '@/utils/preloadCorePages';
import {subscribeCameraStatus} from '@/services/cameraStatus';
import RailIcon from '@/components/RailIcon.vue';
import RailJunction from '@/components/RailJunction.vue';
import RailSignal from '@/components/RailSignal.vue';
import EventPriority from '@/components/EventPriority.vue';
import EventHistory from '@/components/EventHistory.vue';
import { useOverviewEntrance } from '@/utils/useOverviewEntrance';
import { alarmRailState, cameraRailState, cameraDisplayName, cameraNameForEvent } from '@/utils/railPresentation';
import {
  Warning,
  User,
} from '@element-plus/icons-vue'


//登出
const store = useStore();
const router = useRouter();
const route = useRoute();
const entrance = useOverviewEntrance(route);
function syncBusinessTheme() {
  document.body.classList.toggle('rail-business-theme', route.path !== '/');
}
watch(() => route.path, syncBusinessTheme, { immediate: true });
onActivated(syncBusinessTheme);
onDeactivated(() => document.body.classList.remove('rail-business-theme'));
onUnmounted(() => document.body.classList.remove('rail-business-theme'));

function interruptEntrance() {
  entrance.interrupt();
  sceneFrame.value?.contentWindow?.postMessage({channel:'rail-home-v2',action:'interrupt-entrance'}, location.origin);
}
const userRole = computed(() => String(store.getters['user/getUserRole']));
const navigationItems = computed(() => [
  { path: '/', label: '综合态势', icon: 'overview' },
  { path: '/monitoringscreen', label: '实时预览', icon: 'preview' },
  { path: '/originalRecognition', label: '识别验证', icon: 'recognition' },
  { path: '/couplingSensing', label: '作业感知', icon: 'recognition' },
  {
    path: '/alarm', label: '告警中心', icon: 'alert', menuLabel: '告警中心子菜单',
    children: [{ path: '/alarmrecord', label: '告警历史' }],
  },
  { path: '/video', label: '视频回放', icon: 'playback' },
  userRole.value === '1'
    ? { path: '/jobManagement', label: '作业任务', icon: 'review' }
    : { path: '/employeeTask', label: '我的任务', icon: 'review' },
  {
    path: '/cameramanagement', label: '设备管理', icon: 'camera', menuLabel: '设备管理 · 预置点配置',
    children: [
      { path: '/ballMachine', label: '球机预置点' },
      { path: '/gunMachine', label: '枪机预置点' },
      { path: '/stockTrack', label: '股道预置点' },
      { path: '/switch', label: '道岔预置点' },
    ],
  },
  { path: '/dataStatistics', label: '数据统计', icon: 'statistics' },
  { path: '/aiChat', label: 'AI 助手', icon: 'chat' },
  { path: '/userManagement', label: '用户管理', icon: 'users' },
]);
// Keep the arrow as the trigger, but center the popper on the navigation label.
const railSubmenuOptions = {
  modifiers: [
    {
      name: 'anchorRailSubmenuToLabel',
      enabled: true,
      phase: 'beforeRead',
      fn({ state }) {
        const trigger = state.elements.reference;
        const label = trigger.closest('.rail-nav-item')?.querySelector('.rail-nav-label');
        if (!label) return;
        const triggerRect = trigger.getBoundingClientRect();
        const labelRect = label.getBoundingClientRect();
        state.rects.reference.x += labelRect.left - triggerRect.left;
        state.rects.reference.width = labelRect.width;
      },
    },
    { name: 'offset', options: { offset: [0, 7] } },
  ],
};
const railNavigation = ref(null);
const railStopStyle = ref({ visibility: 'hidden' });
function positionRailStop(animate = false) {
  const track = railNavigation.value;
  const active = track?.querySelector('.rail-nav-link.active');
  if (!active) {
    railStopStyle.value = { ...railStopStyle.value, visibility: 'hidden' };
    return;
  }
  const origin = track.getBoundingClientRect();
  const target = active.getBoundingClientRect();
  railStopStyle.value = {
    transform: `translate(${target.left - origin.left + target.width / 2}px, ${target.bottom - origin.top - 6}px)`,
    visibility: 'visible',
    transition: animate ? undefined : 'none',
  };
}
let railObserver;
onMounted(() => {
  railObserver = new ResizeObserver(() => positionRailStop());
  if (railNavigation.value) railObserver.observe(railNavigation.value);
  positionRailStop();
});
watch(() => route.path, () => positionRailStop(true), { flush: 'post' });
onUnmounted(() => railObserver?.disconnect());

const handleHeaderCommand = (command) => command === 'logout' ? logOut() : router.push(command);
const logOut = async () => {
  try {
    await logout(store.state.user.userInfo.id);
  } catch (error) {
    console.warn('退出登录请求失败，已清除本地会话', error);
  } finally {
    localStorage.removeItem('token');
    await store.dispatch('user/logout');
    await router.replace('/login');
  }
}
//头像
const imageUrl = ref('');
const fetchAvatar = async (filename) => {
  if (imageUrl.value) {
    URL.revokeObjectURL(imageUrl.value);
    imageUrl.value = '';
  }
  if (!filename) return;
  try {
    const response = await getAvatar(filename);
    if (response.data instanceof Blob) {
      imageUrl.value = URL.createObjectURL(response.data);
    }
  } catch (error) {
    console.warn('头像加载失败', error);
  }
}
watch(() => store.state.user.userInfo.avatar, fetchAvatar, {immediate: true});

//表格数据
const cameras = reactive([]);
const cameraLoading = ref(true);
const cameraConnection = ref("connecting");
const cameraLoadFailed = ref(false);
const hasDeviceSnapshot = ref(false);
const alarmStatsFailed = ref(true);
const getCameraData = async () => {
  try {
    const response = await getAllCameras();
    if (!Array.isArray(response.data)) throw new Error('设备接口返回格式异常');
    cameras.splice(0, cameras.length, ...response.data);
    cameraLoadFailed.value = false;
    hasDeviceSnapshot.value = true;
  } catch (error) {
    cameraLoadFailed.value = true;
    console.error('获取摄像头列表失败:', error);
  } finally {
    cameraLoading.value = false;
  }
}

const onlineCount = computed(() => cameras.filter(camera => deviceState(camera) === 'online').length);
const offlineCount = computed(() => cameras.filter(camera => deviceState(camera) === 'offline').length);
const unknownCount = computed(() => cameras.length - onlineCount.value - offlineCount.value);
const deviceCountCaption = computed(() => {
  if (cameraLoading.value) return '正在读取';
  if (cameraLoadFailed.value && !hasDeviceSnapshot.value) return '数据不可用';
  if (cameraLoadFailed.value || cameraConnection.value !== 'connected') return '最近快照';
  return unknownCount.value ? `${unknownCount.value} 路状态未知` : '路设备';
});
let dashboardTimer = null;
let dashboardStarting = false;


//统计图
const pieChart = ref();
let pieInstance = null;

// 添加警报数据存储
const cameraAlarms = ref([]);
const statsLoading = ref(true);

const allAlarms = ref([]);
const selectedAlarm = ref(null);
const detectionBaseUrl = process.env.VUE_APP_DETECTION_BASE_URL || '/detection';
const detectionEvents = ref(null);
const evidenceLoading = ref(false);
const failedEvidenceUrl = ref('');
const evidenceImageReady = ref(false);
const evidenceAttempt = ref(0);
const detectionEvidence = computed(() => selectedAlarm.value && !selectedAlarmDate.value && detectionEvents.value?.find(
  event => event.alarmId != null && selectedAlarm.value.id != null && String(event.alarmId) === String(selectedAlarm.value.id)
));
const evidenceUrl = computed(() => {
  const filename = detectionEvidence.value?.snapshotFile;
  return filename ? `${detectionBaseUrl}/evidence/${encodeURIComponent(filename)}` : '';
});
const evidenceConfidence = computed(() => {
  const value = detectionEvidence.value?.confidence;
  return value != null && Number.isFinite(Number(value)) ? `${(Number(value) * 100).toFixed(1)}%` : '未记录';
});
const evidenceReason = computed(() => {
  if (selectedAlarmDate.value) return '摄像头告警没有关联的检测存档帧。';
  if (evidenceUrl.value && failedEvidenceUrl.value === evidenceUrl.value) return '记录关联了存档帧，但图片无法加载。可到告警中心核查原始记录。';
  if (evidenceLoading.value && detectionEvents.value === null) return '正在查询检测证据。';
  if (detectionEvents.value === null) return '检测证据接口暂不可用，无法核实是否有存档帧。';
  if (!detectionEvidence.value) return '近期检测记录中没有与此告警编号匹配的证据。';
  return '已关联检测记录，但该记录未保存事件帧。';
});
watch(evidenceUrl, () => {
  failedEvidenceUrl.value = '';
  evidenceImageReady.value = false;
});
const canRetryEvidence = computed(() => !selectedAlarmDate.value &&
  (Boolean(failedEvidenceUrl.value) || detectionEvents.value === null));
function retryEvidence() {
  if (failedEvidenceUrl.value) {
    evidenceImageReady.value = false;
    failedEvidenceUrl.value = '';
    evidenceAttempt.value++;
  } else if (!evidenceLoading.value) {
    void getDetectionEvidence();
  }
}

const getDetectionEvidence = async () => {
  if (evidenceLoading.value) return;
  evidenceLoading.value = true;
  try {
    const response = await fetch(`${detectionBaseUrl}/events?limit=200`, { cache: 'no-store' });
    const result = await response.json();
    detectionEvents.value = response.ok && result.success && Array.isArray(result.data) ? result.data : null;
  } catch {
    detectionEvents.value = null;
  } finally {
    evidenceLoading.value = false;
  }
};
const sceneFrame = ref(null);
const evidenceDialog = ref(null);
const deviceCollapsed = ref(false);
const deviceFilter = ref('all');
const selectedDeviceId = ref(null);
const deviceFeedback = ref('');
const selectedDevice = computed(() => cameras.find(camera => String(camera.id) === selectedDeviceId.value));
const sceneSelection = ref('');
const sceneFailed = ref(false);
const recordingFeedback = ref('');
const recordingLoading = ref(false);
let recordingRequest = 0;

function configuredCameraId() {
  const value = process.env.VUE_APP_STATION_CAM_01_ID;
  return /^[1-9][0-9]*$/.test(value || '') ? value : null;
}
function deviceTypeLabel(camera) {
  return ({ '0': '球机', '1': '枪机' })[String(camera.type)] || '类型未记录';
}
const deviceState = camera => cameraRailState(camera.status);
const eventCameraName = alarm => cameraNameForEvent(alarm, cameras);
const sceneDeviceId = ref(null);
const highlightedDeviceId = computed(() => selectedDeviceId.value || (currentEventCameraId.value != null ? String(currentEventCameraId.value) : sceneDeviceId.value));
const visibleDevices = computed(() => cameras.filter(camera =>
  deviceFilter.value === 'all' || deviceState(camera) === deviceFilter.value
));
function setDeviceFilter(filter) {
  deviceFilter.value = filter;
  deviceCollapsed.value = false;
}
function syncSceneDevice() {
  const camera = cameras.find(item => String(item.id) === configuredCameraId());
  sceneFrame.value?.contentWindow?.postMessage({
    channel: 'rail-home-v2',
    action: 'device-state',
    marker: 'CAM-01',
    id: camera ? String(camera.id) : '',
    name: camera ? cameraDisplayName(camera) : '',
    detail: camera ? deviceTypeLabel(camera) : '',
    state: camera ? deviceState(camera) : 'unknown',
  }, location.origin);
}
watch(() => cameras.map(camera => [camera.id, camera.name, camera.status, camera.type]), syncSceneDevice);
function focusDevice(id, move = true) {
  const mapped = !sceneFailed.value && id != null && String(id) === configuredCameraId() &&
    cameras.some(camera => String(camera.id) === String(id));
  sceneDeviceId.value = mapped ? String(id) : null;
  sceneSelection.value = '';
  sceneFrame.value?.contentWindow?.postMessage(
    { channel: 'rail-home-v2', action: mapped ? (move ? 'focus' : 'highlight-only') : 'clear-highlight', marker: 'CAM-01' }, location.origin
  );
  return mapped;
}
function selectDevice(camera) {
  selectedDeviceId.value = String(camera.id);
  alarmScope.value = 'all';
  selectedAlarm.value = filteredRecentAlarms.value[0] || null;
  deviceFeedback.value = focusDevice(camera.id) ? '已请求定位关联机位' : '该设备尚未配置站场机位，空间定位不可用。';
}
function receiveSceneSelection(event) {
  if (event.origin !== location.origin || event.source !== sceneFrame.value?.contentWindow ||
      event.data?.channel !== 'rail-scene-v2') return;
  const { action, marker } = event.data;
  if (action === 'takeover') entrance.interrupt();
  if (action === 'error') {
    sceneFailed.value = true;
  } else if (action === 'ready') {
    sceneFailed.value = false;
    syncSceneDevice();
    if (entrance.interrupted.value) sceneFrame.value?.contentWindow?.postMessage({channel:'rail-home-v2',action:'interrupt-entrance'}, location.origin);
    if (!event.data.restored) focusDevice(currentEventCameraId.value ?? selectedDeviceId.value, false);
  } else if (action === 'reset') {
    sceneDeviceId.value = null;
    selectedDeviceId.value = null;
    deviceFeedback.value = '';
    sceneSelection.value = '';
  } else if (action === 'device' && marker === 'CAM-01') {
    const camera = cameras.find(item => String(item.id) === configuredCameraId());
    selectedDeviceId.value = camera ? String(camera.id) : null;
    sceneDeviceId.value = selectedDeviceId.value;
    if (camera) {
      setDeviceFilter('all');
      deviceFeedback.value = '已选择场景中的关联设备';
    } else {
      deviceFeedback.value = '';
    }
    if (camera) selectDevice(camera);
    sceneSelection.value = camera ? '关联设备 · ' + cameraDisplayName(camera) : '示意机位 · 尚未关联真实设备';
  } else if (action === 'region' && marker === 'platform') {
    sceneDeviceId.value = null;
    selectedDeviceId.value = null;
    deviceFeedback.value = '';
    sceneSelection.value = '站台区域 · 尚无经确认的设备与区域关联';
  }
}
const spatialFeedback = computed(() => {
  const id = currentEventCameraId.value;
  if (id == null) return '定位不可用 · 事件缺少摄像头 ID';
  if (String(id) !== configuredCameraId()) return '定位不可用 · 来源设备未绑定站场机位';
  if (sceneFailed.value) return '定位不可用 · 三维场景加载失败';
  return '已关联模型机位 · 空间位置仍为示意';
});
function selectAlarm(alarm) {
  selectedDeviceId.value = null;
  deviceFeedback.value = '';
  selectedAlarm.value = alarm;
  focusDevice(detectionEvidence.value?.cameraId ?? alarm.cameraId);
}
function openEventReview() {
  const alarm = selectedAlarm.value;
  if (!alarm) return;
  router.push({
    path: Number(alarm.dealFlag) === 1 ? '/alarmrecord' : '/alarm',
    query: {
      kind: selectedAlarmDate.value ? 'camera' : 'danger',
      event: alarm.id == null ? undefined : String(alarm.id),
    },
  });
}
const matchedRecording = ref(null);
async function matchRecording() {
  const request = ++recordingRequest;
  matchedRecording.value = null;
  recordingFeedback.value = '';
  const id = currentEventCameraId.value;
  const time = detectionEvidence.value?.createdAt ?? selectedAlarm.value?.createTime;
  if (!selectedAlarm.value) return;
  if (id == null || !time) {
    recordingFeedback.value = '尚未关联 · 记录缺少摄像头 ID 或事件时间';
    return;
  }
  recordingLoading.value = true;
  try {
    const response = await getRecordingMatch(id, time);
    if (request !== recordingRequest) return;
    const filename = response.data?.data?.filename;
    if (response.data?.success && filename) {
      matchedRecording.value = filename;
      recordingFeedback.value = '同设备、时间覆盖当前事件';
    } else recordingFeedback.value = response.data?.msg || '暂无覆盖该时刻的录像';
  } catch {
    if (request === recordingRequest) recordingFeedback.value = '录像查询失败，请检查服务后重试';
  } finally {
    if (request === recordingRequest) recordingLoading.value = false;
  }
}
async function openRecording() {
  const key = selectedEventKey.value;
  if (!matchedRecording.value) await matchRecording();
  if (key === selectedEventKey.value && matchedRecording.value) {
    router.push({ path: '/video', query: { recording: matchedRecording.value } });
  }
}
let overviewClockTimer;
onMounted(() => {
  window.addEventListener('message', receiveSceneSelection);
  overviewClockTimer = window.setInterval(() => { dashboardDate.value = formatDashboardClock(); }, 1000);
});
onUnmounted(() => window.clearInterval(overviewClockTimer));
onUnmounted(() => window.removeEventListener('message', receiveSceneSelection));

const selectedAlarmDate = ref(null);
const alarmScope = ref('all');


const alarmLoadFailed = ref(false);
const alarmLoading = ref(true);
const sevenDayRows = computed(() => {
  const dates = new Set(getLast7Days());
  return cameraAlarms.value.filter(row => dates.has(alarmDay(row.createTime)));
});
const selectedEventKey = computed(() => selectedAlarm.value ? (selectedAlarmDate.value ? 'camera:' : 'danger:') + String(selectedAlarm.value.id) : '');
const currentEventCameraId = computed(() => detectionEvidence.value?.cameraId ?? selectedAlarm.value?.cameraId ?? null);
watch(selectedEventKey, () => {
  recordingRequest++;
  matchedRecording.value = null;
  recordingFeedback.value = '';
  recordingLoading.value = false;
  evidenceImageReady.value = false;
  failedEvidenceUrl.value = '';
  evidenceDialog.value?.close();
});
const rulerDay = computed(() => !selectedAlarmDate.value ? -2 : selectedAlarmDate.value === 'week' ? -1 : getLast7Days().indexOf(selectedAlarmDate.value));
function eventDeviceId(alarm) {
  return alarm.cameraId ?? (!selectedAlarmDate.value ? detectionEvents.value?.find(event => event.alarmId != null && String(event.alarmId) === String(alarm.id))?.cameraId : null);
}
const activeAlarmRows = computed(() => {
  if (!selectedAlarmDate.value) return allAlarms.value;
  return sevenDayRows.value.filter(row => selectedAlarmDate.value === 'week' || alarmDay(row.createTime) === selectedAlarmDate.value);
});
const activeAlarmFailed = computed(() => selectedAlarmDate.value ? alarmStatsFailed.value : alarmLoadFailed.value);
const activePendingCount = computed(() => activeAlarmRows.value.filter(row => alarmRailState(row.dealFlag) === 'pending').length);
const filteredRecentAlarms = computed(() => activeAlarmRows.value
  .filter(row => !selectedDeviceId.value || String(eventDeviceId(row)) === selectedDeviceId.value)
  .filter(row => alarmScope.value !== 'pending' || alarmRailState(row.dealFlag) === 'pending')
  .sort((a, b) => String(b.createTime || '').localeCompare(String(a.createTime || '')))
  .slice(0, selectedAlarmDate.value ? undefined : 12));
watch(filteredRecentAlarms, items => {
  selectedAlarm.value = items.find(item => String(item.id) === String(selectedAlarm.value?.id)) || items[0] || null;
});
function setAlarmPeriod(period) {
  selectedAlarm.value = null;
  selectedAlarmDate.value = period;
  alarmScope.value = 'all';
}
const pendingAlarmCount = computed(() => allAlarms.value.filter(item => alarmRailState(item.dealFlag) === 'pending').length);
const handledAlarmCount = computed(() => allAlarms.value.filter(item => Number(item.dealFlag) === 1).length);
const dashboardDate = ref(formatDashboardClock());
function formatDashboardClock() {
  return new Date().toLocaleString('zh-CN', { hour12: false });
}
const sevenDayAlarmCount = computed(() => sevenDayRows.value.length);
const showAlarmTrend = computed(() => sevenDayAlarmCount.value >= 5 &&
  new Set(sevenDayRows.value.map(row => alarmDay(row.createTime))).size >= 3);
const sparseAlarmRows = computed(() => [...sevenDayRows.value]
  .sort((a, b) => new Date(b.createTime) - new Date(a.createTime)).slice(0, 3));
watch([showAlarmTrend, alarmStatsFailed], () => pieInstance?.resize(), { flush: 'post' });
const formatAlarmTime = (value) => alarmDay(value)
  ? alarmDay(value) + ' ' + new Date(value).toLocaleTimeString('zh-CN', { hour12: false })
  : '时间未记录';
const selectedAlarmType = computed(() => selectedAlarmDate.value ? '摄像头告警' :
  selectedAlarm.value?.type == null || selectedAlarm.value.type === '' ? '类型未记录' : alarmTypeLabel(selectedAlarm.value.type));
const evidenceTitle = computed(() => evidenceLoading.value ? '正在查询存档帧' :
  failedEvidenceUrl.value ? '存档帧加载失败' : selectedAlarmDate.value ? '尚未关联检测截图' :
  detectionEvents.value === null ? '证据查询失败' : detectionEvidence.value ? '存档帧未保存' : '暂无匹配存档帧');
watch([selectedEventKey, currentEventCameraId, () => selectedAlarm.value?.createTime, () => detectionEvidence.value?.createdAt], () => {
  recordingLoading.value = false;
  void matchRecording();
});
watch([selectedEventKey, currentEventCameraId], () => {
  if (selectedAlarm.value) focusDevice(currentEventCameraId.value, false);
  else if (!selectedDeviceId.value) focusDevice(null, false);
});
const alarmTypeLabel = (type) => ({1:'人员目标检出', 2:'车辆目标检出'})[Number(type)] || '告警记录';
const getRecentAlarms = async () => {
  try {
    const response = await getAllAlarmInfo();
    if (!response.data?.success || !Array.isArray(response.data.data)) throw new Error('告警接口返回格式异常');
    allAlarms.value = response.data.data;
    alarmLoadFailed.value = false;
  } catch (error) {
    alarmLoadFailed.value = true;
    console.warn('首页告警列表获取失败', error);
  } finally {
    alarmLoading.value = false;
  }
};

// 获取最近7天的摄像头警报和危险警报数据
const getAlarmStatisticsData = async () => {
  statsLoading.value = true;
  try {
    // 获取摄像头警报数据
    const cameraAlarmResponse = await getAllCameraAlarm();
    if (!Array.isArray(cameraAlarmResponse.data)) throw new Error('告警统计格式异常');
    cameraAlarms.value = cameraAlarmResponse.data;
    alarmStatsFailed.value = false;

    // 更新图表
    updateCharts();
  } catch (error) {
    alarmStatsFailed.value = true;
    console.error("获取警报统计数据失败:", error);
  } finally {
    statsLoading.value = false;
  }
};

// 获取最近7天的日期数组
function alarmDay(value) {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  return [date.getFullYear(), String(date.getMonth() + 1).padStart(2, '0'),
    String(date.getDate()).padStart(2, '0')].join('-');
}

function getLast7Days() {
  const dates = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const formattedDate = [date.getFullYear(), String(date.getMonth() + 1).padStart(2, '0'), String(date.getDate()).padStart(2, '0')].join('-');
    dates.push(formattedDate);
  }
  return dates;
};

// 根据日期获取警报数量，如果没有则返回0


// 窗口/容器变化时重新调整图表大小
const handleResize = () => {
  if (pieInstance) pieInstance.resize();
};

//销毁图表实例
const disposeCharts = () => {
  if (pieInstance) {
    echarts.dispose(pieInstance);
    pieInstance = null;
  }
};

// 初始化 ECharts
const initCharts = async () => {
  await nextTick(); // 确保 DOM 渲染完成
  if (!pieChart.value) {
    console.error('图表容器未找到');
    return;
  }
  // 销毁旧实例
  disposeCharts();
  // 初始化新实例
  pieInstance = echarts.init(pieChart.value);
  pieInstance.on('click', params => {
    if (!params?.name) return;
    const date = getLast7Days().find(day => day.slice(5) === params.name);
    if (!date) return;
    setAlarmPeriod(selectedAlarmDate.value === date ? null : date);
  });
  // 添加错误处理
  if (!pieInstance) {
    throw new Error('图表初始化失败');
  } else {
    console.log('图表初始化成功!!');
  }
  // 更新图表数据
  updateCharts();
};


let unsubscribeCameraStatus = null;

const subscribeToCameraStatus = () => {
  if (unsubscribeCameraStatus) return;
  unsubscribeCameraStatus = subscribeCameraStatus(({type, updates}) => {
    if (type !== 'update') cameraConnection.value = type;
    if (type === 'update') updateCameraStatus(updates);
    // 建立或恢复连接后先取一份完整快照，避免错过断线期间的状态变更。
    if (type === 'connected') {
      Promise.allSettled([getCameraData()]);
    }
  });
};

// 更新摄像头状态
const updateCameraStatus = (updates) => {
  const items = Array.isArray(updates) ? updates : [updates];
  items.forEach(updatedCamera => {
    if (!updatedCamera || updatedCamera.id == null) return;
    const index = cameras.findIndex(c => Number(c.id) === Number(updatedCamera.id));
    if (index !== -1) cameras[index].status = updatedCamera.status;
  });
};


// 更新图表数据
const updateCharts = () => {
  if (!pieInstance) return;
  const last7Days = getLast7Days();
  const alarmData = last7Days.map(date => sevenDayRows.value.filter(row => alarmDay(row.createTime) === date).length);
  const textColor = '#a8c9e4';
  const lineColor = 'rgba(91, 170, 202, .24)';
  pieInstance.setOption({
    backgroundColor: 'transparent',
    animation: false,
    grid: {left: 18, right: 22, top: 14, bottom: 22, containLabel: true},
    tooltip: {
      trigger: 'axis',
      axisPointer: {type: 'line'},
      backgroundColor: '#092a46',
      borderColor: '#3186a8',
      textStyle: {color: '#effbff'},
      valueFormatter: value => value + ' 条'
    },
    xAxis: {
      type: 'category',
      boundaryGap: true,
      data: last7Days.map(date => date.slice(5)),
      axisLine: {lineStyle: {color: lineColor}},
      axisLabel: {color: textColor, fontSize: 11},
      axisTick: {show: false}
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: {color: textColor, fontSize: 11},
      splitLine: {lineStyle: {color: lineColor, type: 'dashed'}},
      axisLine: {show: false},
      axisTick: {show: false}
    },
    series: [{
      name: '摄像头告警',
      type: 'bar',
      barMaxWidth: 24,
      data: alarmData,
      itemStyle: { color: '#59cbff', borderRadius: [3, 3, 0, 0] },
      emphasis: {focus: 'series'}
    }]
  });
};

onMounted(() => {
  window.addEventListener('resize', handleResize)
  preloadCorePages()
})

const stopDashboard = () => {
  if (dashboardTimer) {
    clearInterval(dashboardTimer);
    dashboardTimer = null;
  }
  if (unsubscribeCameraStatus) {
    unsubscribeCameraStatus();
    unsubscribeCameraStatus = null;
  }
  disposeCharts();
};

const startDashboard = async () => {
  if (route.path !== '/' || dashboardTimer || dashboardStarting) return;
  dashboardStarting = true;
  try {
    await nextTick();
    void getDetectionEvidence();
    await Promise.allSettled([getCameraData(), getAlarmStatisticsData(), getRecentAlarms()]);
    if (route.path !== '/' || !pieChart.value) return;
    await initCharts();
    subscribeToCameraStatus();
    dashboardTimer = setInterval(() => {
      if (!evidenceLoading.value) void getDetectionEvidence();
      Promise.allSettled([getCameraData(), getAlarmStatisticsData(), getRecentAlarms()]);
    }, 30000);
  } finally {
    dashboardStarting = false;
  }
};

watch(() => route.path, path => {
  if (path === '/') startDashboard();
  else stopDashboard();
}, {immediate: true});
onActivated(startDashboard);
onDeactivated(stopDashboard);
onUnmounted(() => {
  stopDashboard();
  window.removeEventListener('resize', handleResize);
  if (imageUrl.value) URL.revokeObjectURL(imageUrl.value);
});

const refreshHome = () => {
  router.push('/');
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

#home {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

nav {
  flex: 0 0 auto;
}

.main-container {
  flex: 1 1 auto;
  min-height: 0;
  overflow: hidden;
  display: flex;
  background-color: #f0f8ff;
}

.content {
  position: relative;
  display: flex;
  flex-grow: 1;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
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
  inset: 0;
  min-width: 0;
  min-height: 0;
  background: #04162d;
}
.dashboard {
  position: relative;
  height: 100%;
  overflow-y: auto;
  padding: 22px 28px 12px;
  color: #edfaff;
  background:
    linear-gradient(rgba(48, 155, 193, .045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(48, 155, 193, .045) 1px, transparent 1px),
    radial-gradient(ellipse at 52% 38%, #0a3455 0%, #051f3c 48%, #04152d 100%);
  background-size: 48px 48px, 48px 48px, auto;
}
.dashboard-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  min-height: 78px;
  padding: 0 0 15px;
  border-bottom: 1px solid rgba(91, 190, 221, .42);
}
.dashboard-eyebrow, .module-index {
  display: block;
  color: #61cce7;
  font: 700 10px/1.3 "Segoe UI", sans-serif;
  letter-spacing: 2px;
}
.dashboard-heading h1 {
  margin: 3px 0 4px;
  color: #f5fdff;
  font-size: clamp(24px, 1.85vw, 34px);
  line-height: 1.24;
  letter-spacing: 1px;
  font-weight: 800;
}
.dashboard-heading p {
  margin: 0;
  color: #91b7c9;
  font-size: 12px;
}
.dashboard-heading-right {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #b4d9e7;
  font-size: 12px;
  white-space: nowrap;
}
.live-dot, .stat-light, .legend-dot {
  display: inline-block;
  flex: none;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #44e0cf;
  box-shadow: 0 0 10px rgba(68,224,207,.72);
}
.heading-separator {
  height: 16px;
  border-left: 1px solid rgba(114,195,220,.35);
  margin: 0 6px;
}
.status-rail {
  display: grid;
  grid-template-columns: repeat(4,minmax(0,1fr));
  gap: 14px;
  margin: 17px 0 19px;
}
.status-token {
  --token: #42d8e9;
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 90px;
  padding: 14px 18px;
  border: 1px solid color-mix(in srgb, var(--token) 62%, transparent);
  clip-path: polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 0 100%);
  background: linear-gradient(180deg, rgba(29,87,121,.72), rgba(7,35,63,.82));
  box-shadow: inset 0 1px rgba(172,239,252,.2);
}
.status-token::before {
  content: "";
  position: absolute;
  top: 0; left: 0; width: 56%; height: 2px;
  background: linear-gradient(90deg,var(--token),transparent);
  box-shadow: 0 0 10px var(--token);
}
.status-token.offline { --token: #ed7972; }
.status-token.alarms { --token: #ffbf56; }
.status-token.total { --token: #63c8f1; }
.status-icon {
  display: grid;
  place-items: center;
  flex: 0 0 46px;
  height: 46px;
  border: 1px solid var(--token);
  border-radius: 50%;
  color: var(--token);
  background: rgba(5,25,47,.7);
  box-shadow: inset 0 0 0 5px rgba(26,114,149,.2), 0 0 14px rgba(0,149,199,.17);
  font-size: 23px;
}
.icon-disc {
  width: 15px; height: 15px; border-radius: 50%;
  background: #42e3cf; box-shadow: 0 0 14px #42e3cf;
}
.status-token>div { display:flex;align-items:baseline;gap:7px;flex-wrap:wrap; }
.status-label { flex-basis:100%; color:#bedde8; font-size:12px; font-weight:600; }
.status-token strong { color:#f4fcff; font: italic 800 29px/1 "Segoe UI",sans-serif; }
.status-token small { color:#87b8c8;font-size:11px; }
.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(300px,.8fr) minmax(500px,1.5fr);
  grid-template-rows: 270px 180px 132px;
  gap: 13px 16px;
}
.dash-module {
  position: relative;
  min-width: 0;
  overflow: hidden;
  padding: 17px 20px;
  background: linear-gradient(160deg,rgba(16,58,91,.63),rgba(4,27,52,.38) 65%);
  border-top: 1px solid rgba(66,192,226,.61);
  border-left: 1px solid rgba(43,147,184,.26);
  border-bottom: 1px solid rgba(43,147,184,.18);
}
.dash-module::before {
  content:"";
  position:absolute;
  top:-1px;left:0;
  width:100px;height:2px;
  background:#56e1f3;
  box-shadow:0 0 11px #2cc9f0;
}
.module-head {
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:12px;
  border-bottom:1px solid rgba(72,157,189,.25);
  padding-bottom:9px;
}
.module-head h2 { margin:3px 0 0; color:#f4fcff;font-size:17px;font-weight:750; }
.module-caption { color:#86b6c8;font-size:11px;white-space:nowrap; }
.module-link {
  border:0;
  background:transparent;
  color:#7ddfed;
  font:600 12px "Microsoft YaHei",sans-serif;
  cursor:pointer;
}
.module-link span { font-size:20px;margin-left:4px; }
.module-link:hover { color:#e6ffff; }
.device-module { grid-row:1 / 4; }
.device-overview {
  display:flex;align-items:center;gap:24px;
  min-height:160px;
  padding:14px 8px 8px;
}
.camera-orbit {
  position:relative;
  display:grid;
  place-items:center;
  flex:0 0 122px;
  width:122px;height:122px;
  border:1px solid #37d7ef;
  border-radius:50%;
  background:radial-gradient(circle at 46% 40%,#1c688f,#092e50 52%,#061d3b 72%);
  box-shadow:0 0 0 7px rgba(24,164,209,.09),inset 0 0 25px rgba(38,196,230,.12);
}
.camera-orbit .orbit { position:absolute;border-radius:50%;pointer-events:none; }
.camera-orbit .outer { inset:7px;border:1px dashed rgba(131,234,246,.57); }
.camera-orbit .inner { inset:17px;border:1px solid rgba(111,215,234,.45); }
.camera-orbit>.el-icon {
  color:#d3f8ff;
  font-size:51px;
  filter:drop-shadow(0 4px 4px #00172d);
}
.device-hero-copy>span { color:#9bc6d6;font-size:12px; }
.device-big-number { display:flex;align-items:baseline;gap:9px; }
.device-big-number strong { color:#effdff;font:italic 800 57px/1.15 "Segoe UI",sans-serif; }
.device-big-number small { color:#b4dce7;font-size:18px; }
.device-hero-copy p { margin:4px 0 0;color:#7fb2c7;font-size:11px; }
.device-mini-stats { display:flex;gap:16px;margin-bottom:15px; }
.device-mini-stats>div {
  flex:1;
  display:flex;align-items:center;gap:8px;
  padding:11px 12px;
  background:rgba(13,63,94,.38);
  border-bottom:1px solid rgba(63,177,211,.3);
  color:#b0d2df;font-size:12px;
}
.device-mini-stats strong { margin-left:auto;color:#ebfbff;font:italic 800 20px "Segoe UI",sans-serif; }
.offline-light { background:#ed7972;box-shadow:0 0 9px rgba(237,121,114,.62); }
.device-list-title { display:flex;justify-content:space-between;color:#dceff6;font-size:12px;font-weight:700;margin-bottom:6px; }
.device-list-title span { color:#7db1c5;font-weight:400; }
.device-list { max-height:250px;overflow:auto;scrollbar-color:#397b9b transparent; }
.device-row {
  display:flex;align-items:center;gap:10px;
  width:100%;min-height:44px;
  padding:5px 6px;
  border:0;border-top:1px solid rgba(59,141,176,.2);
  color:#c9e9f3;background:transparent;
  text-align:left;cursor:pointer;
}
.device-row:hover { background:rgba(26,110,147,.24); }
.device-row-icon { display:grid;place-items:center;width:25px;height:25px;border:1px solid rgba(54,185,222,.45);color:#76ddec; }
.device-row-name { overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px; }
.device-row-status { margin-left:auto;white-space:nowrap;font-size:11px;color:#83bbca; }
.device-row-status::before { content:"";display:inline-block;width:5px;height:5px;border-radius:50%;background:currentColor;margin-right:5px;vertical-align:2px; }
.device-row-status.is-online { color:#54e0c7; }
.device-row-status.is-offline { color:#ee817b; }
.row-chevron { color:#6eaabd;font-size:20px; }
.module-empty { padding:28px 0;color:#89b1c1;font-size:12px; }
.trend-module { grid-column:2;grid-row:1; }
.trend-summary { display:flex;gap:28px;align-items:baseline;padding:9px 0 0; }
.trend-summary>div { display:flex;align-items:baseline;gap:8px; }
.trend-summary small { color:#8db6c8;font-size:11px; }
.trend-summary strong { color:#eaffff;font:italic 800 25px "Segoe UI",sans-serif; }
.trend-summary span { color:#aad8e3;font-size:12px; }
.trend-chart { width:100%;height:150px; }
.trend-foot { display:flex;align-items:center;gap:6px;color:#a9d6e2;font-size:11px; }
.legend-dot { background:#38d7e8;box-shadow:0 0 8px #38d7e8; }
.trend-foot-note { margin-left:auto;color:#6e9db0; }
.workflow-module { grid-column:2;grid-row:2; }
.workflow-steps { display:flex;align-items:center;gap:4px;height:112px; }
.workflow-steps button {
  position:relative;flex:1;min-width:0;height:90px;
  display:grid;grid-template-columns:37px 1fr;grid-template-rows:1fr 1fr;
  align-items:center;column-gap:10px;
  padding:16px 12px;
  border:1px solid rgba(58,163,199,.3);
  background:linear-gradient(145deg,rgba(22,83,117,.48),rgba(6,39,69,.3));
  color:#e4f7fb;text-align:left;cursor:pointer;
}
.workflow-steps button:hover,.workflow-steps button:focus-visible {
  border-color:#57dce9;background:rgba(31,104,137,.62);
  outline:none;
}
.workflow-number { position:absolute;top:4px;right:7px;color:#6aaec7;font:10px "Segoe UI",sans-serif; }
.workflow-icon { grid-row:1 / 3;display:grid;place-items:center;width:36px;height:36px;border:1px solid #2998bb;border-radius:50%;color:#73e2ee;font-size:17px; }
.workflow-steps strong { align-self:end;font-size:12px;white-space:nowrap; }
.workflow-steps small { align-self:start;margin-top:3px;color:#7facbf;font-size:10px;white-space:nowrap; }
.workflow-arrow { color:#57d7e7;font-size:22px; }
.distribution-module { grid-column:2;grid-row:3; }
.distribution-module .module-head { padding-bottom:4px; }
.distribution-module .module-head h2 { font-size:15px; }
.distribution-chart { width:100%;height:82px; }
.dashboard-foot {
  display:flex;justify-content:flex-end;
  padding:10px 0 0;color:#6d9eb4;font-size:11px;
}
#home.dashboard-route .main-container { background:#04162d; }
#home.dashboard-route :deep(.sidebar),
#home.dashboard-route :deep(.sidebar .el-menu) {
  background:#061a33;
  border-right-color:rgba(74,164,197,.25);
}
#home.dashboard-route :deep(.sidebar .el-menu-item),
#home.dashboard-route :deep(.sidebar .el-sub-menu__title) { color:#a7ccdc; }
#home.dashboard-route :deep(.sidebar .el-menu-item:hover),
#home.dashboard-route :deep(.sidebar .el-sub-menu__title:hover) { background:#103b5d;color:#e3faff; }
#home.dashboard-route :deep(.sidebar .el-menu-item.is-active) { color:#57e1ee;background:#0b3455; }
#home.dashboard-route .el-menu--horizontal { border-bottom:1px solid rgba(74,164,197,.25); }
#home.dashboard-route .img-box .title { color:#f0fcff; }
@media (max-width:1100px) {
  .dashboard-grid { grid-template-columns:minmax(270px,.8fr) minmax(440px,1.3fr); }
  .status-token { padding:10px;gap:8px; }
  .status-icon { flex-basis:38px;height:38px;font-size:19px; }
  .workflow-steps button { padding:13px 7px;column-gap:5px; }
  .workflow-steps small { display:none; }
}
@media (max-width:850px) {
  .status-rail { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .dashboard-grid { display:block; }
  .dash-module { margin-bottom:12px;min-height:160px; }
  .device-module { min-height:410px; }
  .trend-module { min-height:280px; }
  .workflow-module { min-height:180px; }
  .dashboard-heading-right { display:none; }
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

/* 首页柔性分区：以局部光带、层次与留白组织内容 */
.dashboard {
  background:
    radial-gradient(ellipse 55% 48% at 39% 43%, rgba(13,83,125,.25), transparent 78%),
    radial-gradient(ellipse 40% 30% at 86% 63%, rgba(8,102,133,.12), transparent 80%),
    linear-gradient(rgba(48,155,193,.026) 1px, transparent 1px),
    linear-gradient(90deg,rgba(48,155,193,.026) 1px, transparent 1px),
    #04162d;
  background-size:auto,auto,52px 52px,52px 52px,auto;
}
.dashboard-heading { border-bottom:0; position:relative; }
.dashboard-heading::after {
  content:"";position:absolute;left:0;right:0;bottom:0;height:1px;
  background:linear-gradient(90deg,rgba(89,213,236,.6),rgba(71,174,207,.12) 58%,transparent);
}
.status-rail { gap:19px;margin:22px 0 28px; }
.status-token {
  clip-path:none;
  min-height:78px;
  padding:10px 14px 12px 4px;
  border:0;
  border-radius:0 18px 4px 0;
  background:
    radial-gradient(ellipse at 9% 50%,color-mix(in srgb,var(--token) 13%,transparent),transparent 68%),
    linear-gradient(90deg,rgba(13,63,96,.34),rgba(8,37,67,.08) 90%,transparent);
  box-shadow:none;
}
.status-token::before {
  top:auto;bottom:0;left:5%;width:88%;height:1px;
  background:linear-gradient(90deg,var(--token),color-mix(in srgb,var(--token) 24%,transparent),transparent);
  box-shadow:0 0 8px color-mix(in srgb,var(--token) 46%,transparent);
  opacity:.62;
}
.status-icon {
  border-color:color-mix(in srgb,var(--token) 68%,transparent);
  background:radial-gradient(circle,rgba(16,87,112,.58),rgba(5,25,47,.38));
  box-shadow:0 0 0 5px color-mix(in srgb,var(--token) 7%,transparent),0 0 17px color-mix(in srgb,var(--token) 16%,transparent);
}
.dashboard-grid { gap:19px 24px; }
.dash-module {
  overflow:visible;
  border:0;
  padding:14px 17px;
  background:radial-gradient(ellipse at 5% 0%,rgba(29,102,145,.2),transparent 70%);
}
.dash-module::before {
  top:0;left:17px;width:110px;height:2px;
  background:linear-gradient(90deg,#5be6f1,rgba(58,187,220,.15));
  box-shadow:0 0 12px rgba(72,220,241,.38);
}
.dash-module::after {
  content:"";position:absolute;pointer-events:none;left:0;right:0;bottom:0;height:1px;
  background:linear-gradient(90deg,rgba(60,171,206,.28),rgba(60,171,206,.09),transparent 80%);
}
.module-head { border-bottom:0;position:relative;padding-bottom:15px; }
.module-head::after {
  content:"";position:absolute;left:0;right:0;bottom:4px;height:1px;
  background:linear-gradient(90deg,rgba(78,187,218,.34),rgba(78,187,218,.1) 72%,transparent);
}
.device-overview { padding-top:6px;min-height:146px; }
.camera-orbit {
  border-color:rgba(58,202,229,.62);
  background:radial-gradient(circle at 43% 36%,#185a7e,#082d4c 64%,rgba(5,26,48,.25) 76%);
  box-shadow:0 0 0 8px rgba(24,164,209,.04),0 0 26px rgba(17,173,216,.12),inset 0 0 23px rgba(38,196,230,.1);
}
.device-mini-stats { gap:3px; }
.device-mini-stats>div {
  background:linear-gradient(90deg,rgba(18,78,112,.25),transparent);
  border:0;
  border-radius:0 8px 0 0;
}
.device-list-title { margin-top:2px; }
.device-row {
  border-top:0;
  border-bottom:1px solid rgba(59,141,176,.14);
  transition:background .16s ease,transform .16s ease;
}
.device-row:hover { transform:translateX(3px); }
.trend-module,.workflow-module,.distribution-module { background:linear-gradient(90deg,rgba(13,64,99,.16),transparent 80%); }
.workflow-steps { gap:6px; }
.workflow-steps button {
  border:0;
  border-bottom:1px solid rgba(62,169,199,.25);
  border-radius:0 12px 0 0;
  background:linear-gradient(110deg,rgba(25,102,138,.27),rgba(7,38,65,.05));
  box-shadow:inset 1px 0 rgba(65,193,223,.2);
  transition:background .18s ease,transform .18s ease;
}
.workflow-steps button:hover,.workflow-steps button:focus-visible {
  border-color:#57dce9;background:linear-gradient(110deg,rgba(30,127,159,.43),rgba(7,38,65,.11));
  transform:translateY(-2px);
}
.workflow-icon {
  border-color:rgba(48,164,201,.62);
  box-shadow:0 0 0 4px rgba(56,170,203,.055);
}
.distribution-module .module-head::after { bottom:2px; }

/* 参考案例的组件结构：轻量信息轨、切角标签与悬浮图表 */
.status-rail { position:relative;gap:6px;margin:20px 0 28px;padding:0 5px; }
.status-rail::before { content:"";position:absolute;left:0;right:0;top:50%;height:1px;background:linear-gradient(90deg,transparent,rgba(62,178,211,.22),transparent); }
.status-token {
  min-height:72px;padding:8px 14px 8px 10px;gap:11px;
  border-radius:0;
  background:linear-gradient(90deg,rgba(7,46,76,.68),rgba(11,49,79,.31) 68%,transparent);
  clip-path:polygon(0 0,calc(100% - 18px) 0,100% 50%,calc(100% - 18px) 100%,0 100%,12px 50%);
}
.status-token:first-child { clip-path:polygon(0 0,calc(100% - 18px) 0,100% 50%,calc(100% - 18px) 100%,0 100%); }
.status-token::before { left:11%;width:72%;bottom:6px;opacity:.45; }
.status-icon { flex-basis:40px;height:40px;font-size:19px; }
.status-token strong { font-size:25px; }
.dash-module { background:none; }
.dash-module::after { opacity:.65; }
.module-head::after { right:16%; }
.device-module { background:radial-gradient(ellipse at 25% 30%,rgba(14,80,120,.16),transparent 69%); }
.trend-module,.workflow-module,.distribution-module { background:none; }
.workflow-steps { position:relative;gap:0; }
.workflow-steps::before { content:"";position:absolute;left:5%;right:5%;top:56px;height:1px;background:linear-gradient(90deg,transparent,rgba(63,198,218,.48),transparent); }
.workflow-steps button {
  z-index:1;height:81px;
  background:linear-gradient(110deg,rgba(16,75,107,.33),rgba(6,37,63,.08) 78%,transparent);
  border-bottom:0;border-radius:0;
  clip-path:polygon(0 0,calc(100% - 14px) 0,100% 50%,calc(100% - 14px) 100%,0 100%,12px 50%);
  box-shadow:none;
}
.workflow-steps button:first-child { clip-path:polygon(0 0,calc(100% - 14px) 0,100% 50%,calc(100% - 14px) 100%,0 100%); }
.workflow-steps button::before { content:"";position:absolute;left:14px;right:22px;top:0;height:1px;background:linear-gradient(90deg,rgba(72,220,235,.75),transparent); }
.workflow-steps button:hover { background:linear-gradient(110deg,rgba(23,119,154,.55),rgba(6,37,63,.15)); }
.workflow-arrow { z-index:2;margin:0 -2px;color:#76e6ed; }
.distribution-module { min-height:158px; }
.distribution-body { display:flex;align-items:center;gap:30px;height:115px; }
.distribution-chart { flex:0 0 164px;width:164px;height:112px; }
.distribution-legend { display:flex;gap:30px;align-items:center;flex:1; }
.distribution-legend>div { display:flex;align-items:center;gap:9px;min-width:100px;color:#a8d0de;font-size:12px;border-bottom:1px solid rgba(66,160,191,.22);padding:8px 0; }
.distribution-legend i { display:inline-block;width:7px;height:7px;border-radius:50%; }
.distribution-legend .legend-online { background:#42dce4;box-shadow:0 0 9px #42dce4; }
.distribution-legend .legend-offline { background:#ec8b78;box-shadow:0 0 9px #ec8b78; }
.distribution-legend strong { margin-left:auto;color:#f2fcff;font:italic 700 21px Segoe UI,sans-serif; }
.dashboard-grid { grid-template-rows:270px 180px 158px; }
@media (max-width:1100px) { .distribution-chart { flex-basis:120px;width:120px; } .distribution-legend { gap:10px; } }

/* 首页专属页眉与快捷导航 */
.overview-shell-header {
  flex:0 0 auto;
  color:#f2fbff;
  background:linear-gradient(180deg,#061a34,#04172e);
  border-bottom:1px solid rgba(61,172,213,.35);
}
.overview-header-main {
  position:relative;
  display:grid;
  grid-template-columns:1fr auto 1fr;
  align-items:center;
  min-height:76px;
  padding:0 28px;
  border-bottom:1px solid rgba(65,157,194,.28);
  background:linear-gradient(90deg,rgba(20,72,114,.18),transparent 30%,rgba(20,72,114,.18));
}
.overview-brand {
  display:flex;align-items:center;gap:10px;justify-self:start;
  padding:0;border:0;background:none;color:#eefaff;cursor:pointer;text-align:left;
}
.overview-brand img { width:50px;height:50px;object-fit:contain; }
.overview-brand span { display:flex;flex-direction:column;gap:2px; }
.overview-brand strong { font-size:22px;font-weight:850;font-style:italic;letter-spacing:1px; }
.overview-brand small { color:#75b4d0;font:600 9px "Segoe UI",sans-serif;letter-spacing:2px; }
.overview-page-title { position:relative;min-width:370px;text-align:center;align-self:stretch;display:flex;flex-direction:column;align-items:center;justify-content:center; }
.overview-page-title::after { content:"";position:absolute;bottom:-1px;left:3%;right:3%;height:4px;background:linear-gradient(90deg,transparent,#23a7d7 22%,#47d5ed 50%,#23a7d7 78%,transparent);filter:drop-shadow(0 0 5px #27aedb); }
.overview-page-title h1 { margin:0;color:#f5fdff;font-size:30px;line-height:1.1;font-weight:850;font-style:italic;letter-spacing:2px;text-shadow:0 0 12px rgba(55,175,221,.3); }
.overview-page-title span { margin-top:6px;color:#6fb9d5;font:700 10px "Segoe UI",sans-serif;letter-spacing:2px; }
.overview-header-meta { display:flex;align-items:center;justify-self:end;gap:15px;color:#a8cede;font-size:11px; }
.overview-environment { padding:6px 9px;border:1px solid rgba(70,156,192,.35); }
.overview-environment i { display:inline-block;width:5px;height:5px;border-radius:50%;background:#4ce5df;margin-right:7px;box-shadow:0 0 7px #4ce5df;vertical-align:2px; }
.overview-header-meta button { width:28px;height:28px;border:1px solid rgba(68,165,204,.55);border-radius:50%;color:#a4dfee;background:#0b3555;cursor:pointer; }
.overview-header-meta .overview-user{display:grid;place-items:center;overflow:hidden}
.overview-user img{width:100%;height:100%;object-fit:cover}
.overview-shortcuts { display:flex;align-items:center;justify-content:space-between;min-height:44px;padding:0 28px;gap:20px; }
.overview-shortcut-links { display:flex;align-items:center;height:100%;gap:6px; }
.overview-shortcut-links :deep(.el-dropdown){display:flex;align-items:center;height:100%}
.overview-shortcut-links button {
  display:flex;align-items:center;justify-content:center;gap:7px;
  min-width:122px;height:30px;padding:0 14px;border:0;
  clip-path:polygon(0 0,calc(100% - 12px) 0,100% 50%,calc(100% - 12px) 100%,0 100%,12px 50%);
  color:#9fc8d8;background:linear-gradient(90deg,rgba(21,73,110,.65),rgba(10,49,80,.35));
  font-size:12px;font-weight:650;cursor:pointer;
}
.overview-shortcut-links button:first-child { clip-path:polygon(0 0,calc(100% - 12px) 0,100% 50%,calc(100% - 12px) 100%,0 100%); }
.overview-shortcut-links button.active,.overview-shortcut-links button:hover { color:#fff;background:linear-gradient(90deg,#0c669c,#07416f);box-shadow:inset 0 -2px #48d4eb; }
.overview-shortcut-hint { white-space:nowrap;color:#5db8d4;font-size:11px; }
.dashboard { padding-top:14px; }
.status-rail { margin-top:8px; }
.dashboard-heading { min-height:56px; }
.dashboard-heading h2 { margin:1px 0 2px;color:#f0faff;font-size:18px;font-weight:750; }
@media (max-width:1100px) {
  .overview-shortcuts { overflow-x:auto; }
  .overview-shortcut-hint { display:none; }
  .overview-shortcut-links button { min-width:105px; }
  .overview-page-title h1 { font-size:25px; }
}

/* 正式首页：连续的站场画布和轻量分区，业务数字均来自接口。 */
.dashboard{padding:10px 22px 18px;background:radial-gradient(ellipse at 49% 41%,#0b3450 0%,#061f39 45%,#031329 100%)}
.status-rail{margin:0 0 13px;gap:10px}
.status-token{min-height:59px;padding:6px 13px;clip-path:none;background:linear-gradient(90deg,rgba(13,70,103,.55),rgba(7,36,65,.12));border:0;border-bottom:1px solid rgba(45,162,202,.26)}
.status-token:first-child{clip-path:none}
.status-icon{flex-basis:36px;height:36px;font-size:16px}
.status-token strong{font-size:23px}
.dashboard-grid{display:grid;grid-template-columns:minmax(248px,22%) minmax(0,1fr) minmax(292px,23%);grid-template-rows:minmax(470px,55vh) 226px 132px 170px;gap:13px 16px;align-items:stretch}
.dash-module{min-width:0;min-height:0;padding:10px 12px;overflow:hidden;background:linear-gradient(110deg,rgba(9,49,78,.55),rgba(7,38,67,.08) 82%)}
.dash-module::before{left:12px;width:45px}
.dash-module::after{opacity:.35}
.device-module{grid-column:1;grid-row:1 / 3;overflow-y:auto}
.side-section{margin-top:16px;padding-top:10px;border-top:1px solid rgba(58,150,183,.24)}
.side-section-title{display:flex;align-items:center;gap:7px;color:#e3f6fd;font-size:14px;font-weight:700;margin-bottom:8px}
.side-section-title .el-icon{color:#54cdec}
.side-section-title small{margin-left:auto;color:#79a6b9;font-size:9px;font-weight:400}
.capability-row{display:flex;flex-direction:column;gap:3px;padding:7px 2px;border-bottom:1px solid rgba(55,128,161,.18);font-size:12px}
.capability-row small{color:#87aabd;font-size:10px}
.review-stats{display:flex;gap:9px}.review-stats>div{flex:1;display:flex;align-items:center;justify-content:space-between;padding:8px;color:#a7c8d8;background:rgba(15,68,98,.38);font-size:11px}.review-stats strong{font:italic 700 20px 'Segoe UI',sans-serif;color:#edc17a}.review-stats>div+div strong{color:#62dbc7}
.scene-module{grid-column:2;grid-row:1;padding:0;position:relative;background:radial-gradient(ellipse at 50% 60%,rgba(18,109,138,.2),transparent 70%);overflow:hidden}
.scene-module::before,.scene-module::after{display:none}
.scene-module-head{position:absolute;z-index:2;left:15px;right:15px;top:11px;display:flex;justify-content:space-between;align-items:flex-start;pointer-events:none;text-shadow:0 2px 8px #001625}
.scene-module-head h2{font-size:19px;margin:4px 0;color:#eafaff}
.scene-module-head h2 small{font-size:11px;font-weight:400;color:#86acc0;margin-left:8px}
.scene-module-head>span{font-size:10px;color:#8cafc1}
.scene-module iframe{position:absolute;inset:0;width:100%;height:100%;border:0;background:transparent}
.scene-disclaimer{position:absolute;left:13px;bottom:7px;z-index:2;pointer-events:none;color:#b8d8e6;background:rgba(2,22,39,.74);font-size:10px;padding:3px 7px}
.events-module{grid-column:3;grid-row:1;display:flex;flex-direction:column}
.events-source{display:flex;justify-content:space-between;gap:8px;font-size:10px;color:#89aabd;padding:1px 0 9px;border-bottom:1px solid rgba(61,152,184,.2)}
.events-source button{padding:0;border:0;background:none;color:#65d8f0;cursor:pointer;white-space:nowrap}
.recent-event-list{flex:1;min-height:0;overflow-y:auto;scrollbar-width:thin;scrollbar-color:#216485 transparent}
.recent-event{width:100%;min-height:70px;display:flex;align-items:center;gap:9px;padding:9px 3px;color:#e6f7ff;border:0;border-bottom:1px solid rgba(68,146,180,.21);background:none;text-align:left;cursor:pointer}
.recent-event:hover,.recent-event.selected{background:linear-gradient(90deg,rgba(17,113,153,.32),transparent 90%)}
.recent-event.selected{box-shadow:inset 2px 0 #22c2e9}
.recent-event-mark{display:grid;place-items:center;width:27px;height:27px;flex:none;color:#65d8f0;border:1px solid rgba(49,155,194,.38);background:rgba(18,91,127,.22)}
.recent-event-copy{min-width:0;flex:1;display:flex;flex-direction:column;gap:2px}
.recent-event-copy time,.recent-event-copy small{font-size:10px;color:#8daec0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.recent-event-copy strong{font-size:12px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.recent-event-state{font-size:10px;color:#f4bd67;white-space:nowrap}
.recent-event-state.done{color:#50d6c2}
.trend-module{grid-column:2;grid-row:2}
.trend-chart{height:115px}
.workflow-module{grid-column:1 / 4;grid-row:3}
.workflow-module .module-head{padding-bottom:6px}
.workflow-steps button{height:62px}
.workflow-steps::before{top:42px}
.evidence-module{grid-column:3;grid-row:2;display:flex;flex-direction:column}
.evidence-module .module-head{padding-bottom:5px;margin-bottom:2px}
.evidence-title{display:flex;justify-content:space-between;gap:8px;font-size:12px}
.evidence-title span{color:#ffc46f;font-size:10px;white-space:nowrap}
.evidence-placeholder{height:71px;display:flex;align-items:center;justify-content:center;gap:7px;margin:7px 0;color:#7398ab;background:linear-gradient(120deg,rgba(12,57,83,.55),rgba(5,29,51,.24));border:1px dashed rgba(60,132,163,.32);font-size:10px}
.evidence-module dl{margin:0;font-size:10px}
.evidence-module dl div{display:flex;justify-content:space-between;gap:8px;margin-bottom:4px}
.evidence-module dt{color:#7ca4b8}.evidence-module dd{margin:0;color:#c0dbe8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.evidence-link{margin-top:auto;border:1px solid rgba(48,160,199,.48);background:rgba(13,100,142,.5);color:#d1f1ff;padding:5px;font-size:11px;cursor:pointer}
.distribution-module{grid-column:1 / 4;grid-row:4;min-height:0}
.dashboard-foot{padding-top:10px}
#home.operations-route>nav{background:#061a33;border-bottom:1px solid rgba(69,163,194,.35)}
#home.operations-route>nav :deep(.el-menu){border-bottom:0!important}
#home.operations-route .img-box .title{color:#eafaff;font-weight:750;letter-spacing:.6px}
#home.operations-route .main-container{background:#eaf2f8}
#home.operations-route :deep(.ops-page-header),
#home.operations-route :deep(.monitor-page-head){padding:12px 20px 14px;margin-bottom:12px;background:linear-gradient(100deg,#092d4d,#0b4567 48%,#092d4d);border-bottom:1px solid #39b4d8;box-shadow:inset 0 1px rgba(126,224,245,.18);color:#e9f9ff}
#home.operations-route :deep(.ops-page-header h1),
#home.operations-route :deep(.monitor-page-head h1){color:#f1fbff}
#home.operations-route :deep(.ops-page-header p),
#home.operations-route :deep(.monitor-page-head p){color:#a4c8d9}
#home.operations-route :deep(.ops-eyebrow),
#home.operations-route :deep(.monitor-page-head span){color:#6dd8ef}
@media(max-width:1250px){.dashboard-grid{grid-template-columns:minmax(220px,24%) minmax(0,1fr) minmax(260px,25%)}.scene-module-head>span{display:none}}
@media(max-width:900px){.dashboard-grid{display:flex;flex-direction:column}.scene-module{height:460px;flex:none}.events-module{height:320px;flex:none}.device-module{max-height:370px}.trend-module{height:250px}.workflow-module{height:150px}.evidence-module{height:220px}.status-rail{grid-template-columns:repeat(2,minmax(0,1fr))}}

/* 连续站场画布：用柔和的光层和短线标记信息区，而非封闭卡片。 */
.dashboard{background:radial-gradient(ellipse 60% 48% at 52% 37%,#0d3a59 0%,#082a48 48%,#04172e 100%)}
.dashboard-grid{column-gap:20px;row-gap:17px}
.dash-module{background:transparent;box-shadow:none}
.dash-module::after{display:none}
.device-module{background:linear-gradient(90deg,rgba(12,55,83,.58),rgba(10,48,78,.25) 78%,transparent)}
.events-module,.evidence-module{background:linear-gradient(270deg,rgba(12,55,83,.56),rgba(10,48,78,.22) 78%,transparent)}
.trend-module,.workflow-module,.distribution-module{background:linear-gradient(180deg,rgba(12,58,89,.22),transparent 82%)}
.module-head{padding-bottom:12px}
.module-head::after{left:0;right:auto;width:84px;height:1px;background:linear-gradient(90deg,#49d3e9,rgba(73,211,233,.08))}
.module-index{letter-spacing:1.6px}
.status-token{background:linear-gradient(90deg,rgba(13,75,108,.5),rgba(6,34,60,.06) 92%);border-bottom-color:rgba(79,187,218,.17)}
.status-token:hover{background:linear-gradient(90deg,rgba(20,97,132,.58),rgba(6,34,60,.1) 92%)}
.recent-event{border-bottom-color:rgba(77,160,190,.15)}
.recent-event.selected{background:linear-gradient(90deg,rgba(20,130,169,.36),rgba(11,73,104,.08) 85%,transparent)}
.evidence-placeholder{border:0;border-bottom:1px solid rgba(72,153,186,.23);background:linear-gradient(90deg,rgba(17,75,104,.25),transparent)}
.scene-module{background:radial-gradient(ellipse at 50% 60%,rgba(18,109,138,.14),transparent 70%)}
.device-module{background:radial-gradient(ellipse 115% 70% at 0% 40%,rgba(16,71,101,.37),transparent 85%)}
.events-module,.evidence-module{background:radial-gradient(ellipse 115% 70% at 100% 35%,rgba(16,71,101,.33),transparent 85%)}
.trend-module,.workflow-module,.distribution-module{background:transparent}
.recent-event-list{mask-image:linear-gradient(180deg,#000 0%,#000 92%,transparent 100%)}
@media (prefers-reduced-motion:reduce){.status-token,.recent-event{transition:none!important}}

/* 值班首页：一屏先看设备，再核查事件与证据。 */
.dashboard{display:flex;flex-direction:column;height:100%;min-height:0;overflow:hidden;padding:10px 22px 8px}
.status-rail{flex:none;margin:0 0 10px;gap:10px;padding:0}
.status-rail::before{display:none}
.status-token{min-height:57px;gap:9px;padding:5px 10px}
.status-icon{flex-basis:34px;height:34px;font-size:16px}
.status-token strong{font-size:22px}
.status-label{font-size:11px}
.dashboard-grid{flex:1;min-height:0;grid-template-columns:minmax(248px,24%) minmax(0,41%) minmax(270px,35%);grid-template-rows:minmax(0,1fr) 102px 76px;gap:9px 15px}
.dash-module{padding:9px 12px;min-height:0;overflow:hidden}
.device-module{grid-column:1;grid-row:1 / 3;overflow-y:auto;scrollbar-width:thin;scrollbar-color:#246783 transparent}
.events-module{grid-column:2;grid-row:1}
.evidence-module{grid-column:3;grid-row:1}
.trend-module{grid-column:2 / 4;grid-row:2;display:flex;flex-direction:column}
.workflow-module{grid-column:1 / 4;grid-row:3}
.module-head{padding-bottom:7px}
.module-head h2{font-size:15px}
.module-index{font-size:9px}
.device-overview{min-height:86px;gap:14px;padding:6px 2px}
.camera-orbit{flex-basis:64px;width:64px;height:64px}
.camera-orbit>.el-icon{font-size:29px}
.camera-orbit .inner{inset:10px}.camera-orbit .outer{inset:4px}
.device-big-number strong{font-size:35px}.device-big-number small{font-size:13px}
.device-mini-stats{margin-bottom:8px}
.device-mini-stats>div{padding:5px 7px;font-size:11px}
.device-mini-stats strong{font-size:16px}
.device-row{min-height:37px}
.side-section{margin-top:9px;padding-top:7px}
.side-section-title{font-size:12px;margin-bottom:5px}
.capability-row{padding:4px 2px;font-size:11px}
.review-stats>div{padding:5px}
.review-stats strong{font-size:17px}
.recent-event{min-height:60px;padding:6px 3px}
.events-source{padding-bottom:5px}
.evidence-module .module-head{margin-bottom:5px}
.evidence-placeholder{height:82px;margin:10px 0}
.trend-module .module-head{padding-bottom:3px}
.trend-module .module-head h2{font-size:14px}
.trend-summary{margin:1px 0}
.trend-summary strong{font-size:17px}
.trend-chart{height:auto;flex:1;min-height:35px}
.trend-foot{font-size:9px}
.workflow-module .module-head{padding-bottom:2px}
.workflow-steps{height:46px}
.workflow-steps::before{top:25px}
.workflow-steps button{height:44px;padding:4px 10px;grid-template-columns:29px 1fr;column-gap:6px}
.workflow-icon{width:27px;height:27px;font-size:13px}
.workflow-number{font-size:9px}
.workflow-steps strong{font-size:11px}
.workflow-steps small{font-size:9px}
.dashboard-foot{flex:none;padding-top:3px;font-size:9px}
@media(max-width:1100px){.dashboard{overflow-y:auto}.dashboard-grid{flex:none;display:flex;flex-direction:column}.device-module,.events-module,.evidence-module,.trend-module,.workflow-module{flex:none;min-height:160px}.device-module{max-height:350px}.events-module{height:280px}.workflow-module{min-height:98px}.status-rail{grid-template-columns:repeat(2,minmax(0,1fr))}}
.dashboard{padding:7px 22px 5px}
.status-rail{margin-bottom:6px}
.status-token{min-height:52px}
.dashboard-grid{grid-template-rows:minmax(0,1fr) 120px 76px;row-gap:6px}
.events-guidance{flex:none;margin:auto 0 0;padding:10px 6px 2px;border-top:1px solid rgba(74,157,185,.2);color:#87afc1;font-size:11px;line-height:1.5}
.trend-module{padding-top:6px;padding-bottom:3px}
.trend-module .module-head{padding-bottom:0}
.trend-module .module-head::after{display:none}
.trend-summary{display:flex;align-items:baseline;gap:18px;min-height:20px;margin:0}
.trend-chart{min-height:62px}
.trend-foot{min-height:12px}
.workflow-module{padding-top:5px;padding-bottom:3px}
.workflow-module .module-head{padding-bottom:0}
.workflow-module .module-head::after{display:none}
.workflow-steps{height:45px}
@media(max-height:760px) and (min-width:1101px){.dashboard-grid{grid-template-rows:minmax(0,1fr) 106px 70px}.trend-chart{min-height:52px}.workflow-steps{height:42px}}
.dashboard-grid{grid-template-rows:minmax(0,1fr) 132px}
.device-module{grid-row:1 / 3}
.trend-module{grid-row:2}
.device-list-title{margin:15px 0 5px}
.device-list{max-height:min(30vh,180px)}
.events-guidance{line-height:1.6}
@media(max-height:760px) and (min-width:1101px){.dashboard-grid{grid-template-rows:minmax(0,1fr) 115px}}

/* 三维场景回到首页中央；真实设备与告警围绕场景形成值班视线。 */
.dashboard-grid{grid-template-columns:minmax(226px,23%) minmax(0,1fr) minmax(282px,27%);grid-template-rows:minmax(0,1fr) 132px;column-gap:10px}
.device-module{grid-column:1;grid-row:1 / 3}
.scene-module{grid-column:2;grid-row:1;min-height:0;padding:0;background:radial-gradient(ellipse at 50% 55%,rgba(18,109,138,.18),transparent 70%)}
.scene-module-head{left:12px;right:12px;top:9px}
.scene-module-head h2{font-size:17px}
.scene-disclaimer{left:8px;bottom:5px;max-width:calc(100% - 16px);font-size:9px}
.events-module{grid-column:3;grid-row:1}
.evidence-module{grid-column:3;grid-row:2;padding-top:5px;padding-bottom:4px}
.evidence-module .module-head{padding-bottom:1px;margin-bottom:1px}
.evidence-module .module-head h2{font-size:13px}
.evidence-title{font-size:10px}
.evidence-placeholder{height:28px;margin:3px 0;font-size:9px}
.evidence-module dl{font-size:9px}
.evidence-module dl div{margin-bottom:1px}
.evidence-link{font-size:9px;padding:3px}
.trend-module{grid-column:2;grid-row:2}
.trend-module .module-head h2{font-size:12px}
.trend-summary{min-height:18px}
.trend-chart{min-height:60px}
.events-guidance{font-size:10px}
@media(max-height:760px) and (min-width:1101px){.dashboard-grid{grid-template-rows:minmax(0,1fr) 115px}.evidence-placeholder{height:22px}}
@media(max-width:1100px){.dashboard-grid{display:flex;flex-direction:column}.scene-module{height:400px;flex:none}.evidence-module{min-height:160px}}
</style>
<style scoped src="../assets/style/home-spatial.css"></style>
