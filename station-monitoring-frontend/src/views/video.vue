<template>
  <div class="app-container">
    <!-- 导航栏 -->
    <header class="header">
      <div class="logo-section">
        <i class="fas fa-video"></i>
        <h1>视频回放</h1>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
      <!-- 侧边栏 - 视频列表 -->
      <aside class="sidebar">
        <div class="recordings-browser">
          <div class="sidebar-header">
            <div class="panel-header with-controls">
              <h2>录像文件</h2>
              <div class="controls">
                <button class="btn refresh-btn" @click="getRecordings">
                  <i class="fas fa-sync"></i>
                </button>
                <!-- 视图变化：网格视图和列表视图 -->
                <div class="view-toggle">
                  <button class="btn" :class="{'active': viewMode === 'grid'}" @click="viewMode = 'grid'">
                    <i class="fas fa-th"></i>
                  </button>
                  <button class="btn" :class="{'active': viewMode === 'list'}" @click="viewMode = 'list'">
                    <i class="fas fa-list"></i>
                  </button>
                </div>
              </div>
            </div>

            <div class="filter-bar">
              <div class="search-bar">
                <i class="fas fa-search"></i>
                <!-- 当用户输入时，自动触发filterRecordings方法 -->
                <input type="text" placeholder="搜索录像..." v-model="searchQuery" @input="filterRecordings">
              </div>
            </div>
          </div>

          <div class="sidebar-scroll-container">
            <div v-if="filteredRecordings.length === 0" class="no-recordings">
              <i class="fas fa-film"></i>
              <p>暂无符合条件的录像</p>
            </div>

            <div v-else class="video-list-container">
              <!-- 网格视图 -->
              <div v-if="viewMode === 'grid'" class="video-grid">
                <div
                    v-for="video in filteredRecordings"
                    :key="video.filename"
                    class="video-card"
                    @click="selectVideo(video)"
                    :class="{'selected': selectedVideo && selectedVideo.path === video.path}"
                >
                  <!-- 删除按钮 -->
                  <button class="delete-btn" @click.stop="confirmDelete(video)">
                    <i class="fas fa-trash"></i>
                  </button>
                  <div class="thumbnail">
                    <img :src="getVideoThumbnail(video)" alt="视频缩略图">
                    <span class="duration">{{ video.duration || '00:00:00' }}</span>
                  </div>
                  <div class="video-info">
                    <div class="video-name">{{ formatVideoName(video.filename) }}</div>
                    <div class="video-meta">
                      <span class="video-time">{{ formatTime(video.date) }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 列表视图 -->
              <div v-else class="video-list">
                <div
                    v-for="video in filteredRecordings"
                    :key="video.filename"
                    class="video-item"
                    @click="selectVideo(video)"
                    :class="{'selected': selectedVideo && selectedVideo.path === video.path}"
                >
                  <!-- 删除按钮 -->
                  <button class="delete-btn" @click.stop="confirmDelete(video)">
                    <i class="fas fa-trash"></i>
                  </button>
                  <div class="video-thumbnail">
                    <img :src="getVideoThumbnail(video)" alt="视频缩略图">
                  </div>
                  <div class="video-details">
                    <div class="video-name">{{ formatVideoName(video.filename) }}</div>
                    <div class="video-meta">
                      <span class="video-time"><i class="fas fa-clock"></i> {{ formatTime(video.date) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 主内容区域 - 视频播放 -->
      <section class="content-area" :class="{'full-width': sidebarCollapsed}">
        <div class="playback-view">
          <div v-if="!selectedVideo" class="no-video-selected">
            <i class="fas fa-film"></i>
            <p>请从左侧选择一个录像进行播放</p>
          </div>

          <div v-else class="video-player-container">
            <div class="panel-header with-controls">
              <h2>{{ getPlayerTitle() }}</h2>
              <div class="controls">
                <button class="btn close-btn" @click="closeVideo">
                  <i class="fas fa-times"></i> 关闭
                </button>
              </div>
            </div>

            <div class="video-player">
              <!-- 加载指示器 - 调整为非全屏样式 -->
              <div v-if="videoLoading" class="video-loading">
                <div class="loading-spinner"></div>
                <p>加载视频中...</p>
              </div>

              <!-- Video.js播放器 -->
              <div class="video-wrapper">
                <video
                    ref="videoPlayer"
                    class="video-js vjs-theme-forest"
                    controls
                    preload="auto"
                    v-if="selectedVideo"
                    :src="selectedVideo.path"
                    style="width:100%;height:100%;background:#000;object-fit:contain;"
                >
                  <p>要查看此视频，请启用JavaScript并考虑升级到支持HTML5视频的Web浏览器</p>
                </video>
              </div>
            </div>

            <div class="video-details">
              <div class="detail-item">
                <i class="fas fa-calendar"></i>
                <span>{{ selectedVideo?.date || '未知日期' }}</span>
              </div>
              <div class="detail-item">
                <i class="fas fa-file"></i>
                <span>{{ selectedVideo?.filename || '未知文件名' }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 消息提示 -->
    <div v-if="message" class="message-toast" :class="messageType">
      <i class="fas" :class="getMessageIcon()"></i>
      {{ message }}
    </div>
  </div>
</template>

<script>
// 引入API基础URL - 如果需要的话可以保留
const API_BASE_URL = 'http://localhost:4000/api';

// 声明videojs为全局变量，避免ESLint报错
/* global videojs */
/* global Hls */

export default {
  name: 'App',
  data() {
    return {
      // 视图控制
      viewMode: 'grid', // 'grid', 'list'

      // 侧边栏状态
      sidebarCollapsed: false,

      // 录像列表和过滤
      recordings: [],
      filteredRecordings: [],
      selectedVideo: null,
      searchQuery: '',

      // 消息提示
      message: '',
      messageType: 'info',
      messageTimeout: null,

      // Video.js播放器
      player: null,
      videoLoading: false,
      isSelectingVideo: false,
      hlsInstance: null,

      // 视频源目录 - 实际项目中应由服务器提供访问
      videoDirectory: 'D:/camera_test/hls_output',
      // HTTP服务器URL前缀，用于替换本地路径
      videoServerUrl: 'http://localhost:4000/videos',
    }
  },

  mounted() {
    // 组件加载后立即获取录像列表
    this.getRecordings();

    // 加载字体图标
    this.loadFontAwesome();

    // 加载HLS.js库
    this.loadHlsLibrary();

    // 恢复用户侧边栏偏好
    const savedSidebarState = localStorage.getItem('sidebarCollapsed');
    if (savedSidebarState !== null) {
      this.sidebarCollapsed = savedSidebarState === 'true';
    }

    // 确保侧边栏滚动容器正确初始化
    this.$nextTick(() => {
      // 修复滚动问题
      this.fixScrolling();
    });
  },

  beforeUnmount() {
    // 清除定时器
    if (this.messageTimeout) {
      clearTimeout(this.messageTimeout);
    }

    // 销毁播放器
    this.closeVideo();
  },

  methods: {
    // 切换侧边栏显示/隐藏
    toggleSidebar() {
      // 功能已禁用
      console.log('侧边栏切换功能已禁用');
    },

    // 加载HLS.js库
    loadHlsLibrary() {
      if (window.Hls) {
        console.log('HLS.js已加载');
        return Promise.resolve();
      }

      return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/hls.js@latest';
        script.async = true;
        script.onload = () => {
          console.log('HLS.js加载成功');
          resolve();
        };
        script.onerror = () => {
          console.error('HLS.js加载失败');
          this.showMessage('HLS视频库加载失败，可能影响视频播放', 'error');
          reject();
        };
        document.head.appendChild(script);
      });
    },

    // 加载Video.js库
    loadVideoJs() {
      if (window.videojs) {
        console.log('Video.js已加载');
        return Promise.resolve();
      }

      return new Promise((resolve, reject) => {
        // 加载CSS
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://vjs.zencdn.net/7.20.3/video-js.css';
        document.head.appendChild(link);

        // 加载JS
        const script = document.createElement('script');
        script.src = 'https://vjs.zencdn.net/7.20.3/video.min.js';
        script.async = true;
        script.onload = () => {
          console.log('Video.js加载成功');
          resolve();
        };
        script.onerror = () => {
          console.error('Video.js加载失败');
          this.showMessage('视频播放库加载失败', 'error');
          reject();
        };
        document.head.appendChild(script);
      });
    },

    // 加载Font Awesome图标库
    loadFontAwesome() {
      const script = document.createElement('script');
      script.src = 'https://kit.fontawesome.com/a076d05399.js';
      script.crossOrigin = 'anonymous';
      document.head.appendChild(script);
    },

    // 获取录像列表 - 直接读取指定目录
    async getRecordings() {
      try {
        const response = await fetch(`${API_BASE_URL}/list-videos`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        this.recordings = data.map(video => ({
          filename: video.filename,
          path: `${this.videoServerUrl}/${encodeURIComponent(video.filename)}`,
          date: video.mtime || '',
          thumbnail: video.thumbnail || '',
          duration: video.duration || ''
        }));
        this.filterRecordings();
        this.showMessage('成功加载视频列表', 'success');
      } catch (error) {
        console.error('获取录像列表失败:', error);
        this.showMessage('获取录像列表失败', 'error');
        this.recordings = [];
        this.filterRecordings();
      }
    },

    // 将本地文件路径转换为可访问的HTTP URL
    getVideoHttpUrl(filePath) {
      // 从文件路径中提取文件名
      const filename = filePath.split(/[\/\\]/).pop();
      // 构建HTTP URL
      return `${this.videoServerUrl}/${encodeURIComponent(filename)}`;
    },

    // 加载测试数据（开发阶段使用，实际项目中可删除）
    loadTestData() {
      // 模拟10个m3u8视频文件
      const videos = [];
      const today = new Date();

      for (let i = 0; i < 10; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        const dateStr = date.toISOString().split('T')[0].replace(/-/g, '');
        const timeStr = `${String(Math.floor(Math.random() * 24)).padStart(2, '0')}${String(Math.floor(Math.random() * 60)).padStart(2, '0')}${String(Math.floor(Math.random() * 60)).padStart(2, '0')}`;
        const filename = `video_${dateStr}_${timeStr}.m3u8`;

        videos.push({
          filename: filename,
          path: `${this.videoServerUrl}/${filename}`,
          date: `${dateStr}_${timeStr}`,
          thumbnail: '',
          duration: `00:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}`
        });
      }

      this.recordings = videos;
      this.filterRecordings();
    },

    // 从文件名中提取日期
    extractDateFromFilename(filename) {
      // 尝试匹配格式：video_20230502_121520.m3u8
      const match = filename.match(/(\d{8})_(\d{6})/);
      if (match) {
        return `${match[1]}_${match[2]}`;
      }
      return null;
    },

    // 过滤录像列表
    filterRecordings() {
      if (!this.searchQuery) {
        // 没有搜索条件，按日期从新到旧排序
        this.filteredRecordings = [...this.recordings].sort((a, b) => b.date.localeCompare(a.date));
      } else {
        // 按搜索词过滤视频文件名
        const query = this.searchQuery.toLowerCase();
        this.filteredRecordings = this.recordings
            .filter(video => video.filename.toLowerCase().includes(query))
            .sort((a, b) => b.date.localeCompare(a.date));
      }

      // 在DOM更新后调整滚动位置
      this.$nextTick(() => {
        const container = document.querySelector('.video-list-container');
        if (container) {
          // 重置滚动位置到顶部
          container.scrollTop = 0;
        }
      });
    },

    // 格式化视频名称(去除日期和扩展名)
    formatVideoName(filename) {
      if (!filename) return '';

      // 移除扩展名
      let name = filename.replace(/\.[^/.]+$/, "");

      // 如果名称包含日期时间格式（如video_20230502_121520），则移除
      name = name.replace(/^video_\d{8}_\d{6}_?/, "");

      // 将下划线替换为空格
      name = name.replace(/_/g, " ");

      return name || filename;
    },

    // 获取视频缩略图
    getVideoThumbnail(video) {
      // 如果视频有缩略图，直接返回
      if (video.thumbnail) {
        return video.thumbnail;
      }
      // 否则返回默认图片
      return 'data:image/svg+xml;charset=UTF-8,%3Csvg%20width%3D%22320%22%20height%3D%22180%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20320%20180%22%20preserveAspectRatio%3D%22none%22%3E%3Cdefs%3E%3Cstyle%20type%3D%22text%2Fcss%22%3E%23holder_16d13f06515%20text%20%7B%20fill%3A%23999%3Bfont-weight%3Anormal%3Bfont-family%3A-apple-system%2CBlinkMacSystemFont%2C%26quot%3BSegoe%20UI%26quot%3B%2CRoboto%2C%26quot%3BHelvetica%20Neue%26quot%3B%2CArial%2C%26quot%3BNoto%20Sans%26quot%3B%2Csans-serif%2C%26quot%3BApple%20Color%20Emoji%26quot%3B%2C%26quot%3BSegoe%20UI%20Emoji%26quot%3B%2C%26quot%3BSegoe%20UI%20Symbol%26quot%3B%2C%26quot%3BNoto%20Color%20Emoji%26quot%3B%2C%20monospace%3Bfont-size%3A16pt%20%7D%20%3C%2Fstyle%3E%3C%2Fdefs%3E%3Cg%20id%3D%22holder_16d13f06515%22%3E%3Crect%20width%3D%22320%22%20height%3D%22180%22%20fill%3D%22%23373940%22%3E%3C%2Frect%3E%3Cg%3E%3Ctext%20x%3D%22120.3359375%22%20y%3D%2297.35%22%3E%E8%A7%86%E9%A2%91%3C%2Ftext%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E';
    },

    // 选择视频进行播放
    async selectVideo(video) {
      if (this.selectedVideo && this.selectedVideo.path === video.path) return;
      if (this.isSelectingVideo) return;
      this.isSelectingVideo = true;
      this.closeVideo();
      this.videoLoading = true;
      this.selectedVideo = video;
      setTimeout(() => {
        if (this.$refs.videoPlayer) {
          this.$refs.videoPlayer.src = video.path;
          this.$refs.videoPlayer.load();
          this.$refs.videoPlayer.oncanplay = () => {
            this.videoLoading = false;
            this.isSelectingVideo = false;
            this.showMessage('视频加载完成', 'success');
          };
          this.$refs.videoPlayer.onerror = () => {
            this.videoLoading = false;
            this.isSelectingVideo = false;
            this.showMessage('视频加载失败', 'error');
          };
        } else {
          this.videoLoading = false;
          this.isSelectingVideo = false;
          this.showMessage('播放器初始化失败', 'error');
        }
      }, 100);
    },

    // 关闭视频播放 - 改进清理逻辑
    closeVideo() {
      this.videoLoading = false;
      if (this.$refs.videoPlayer) {
        this.$refs.videoPlayer.pause();
        this.$refs.videoPlayer.removeAttribute('src');
        this.$refs.videoPlayer.load();
      }
      this.selectedVideo = null;
      this.isSelectingVideo = false;
    },

    // 格式化时间显示
    formatTime(dateTimeStr) {
      if (!dateTimeStr) return '';

      // 如果是带下划线的日期时间(如20230502_121520)，转换为时间格式
      if (dateTimeStr.includes('_')) {
        const timeStr = dateTimeStr.split('_')[1];
        if (timeStr && timeStr.length === 6) {
          return `${timeStr.substring(0, 2)}:${timeStr.substring(2, 4)}:${timeStr.substring(4, 6)}`;
        }
      }

      return dateTimeStr;
    },

    // 获取消息图标
    getMessageIcon() {
      switch (this.messageType) {
        case 'success':
          return 'fa-check-circle';
        case 'error':
          return 'fa-exclamation-circle';
        case 'warning':
          return 'fa-exclamation-triangle';
        default:
          return 'fa-info-circle';
      }
    },

    // 显示消息提示
    showMessage(msg, type = 'info') {
      this.message = msg;
      this.messageType = type;

      // 清除之前的定时器
      if (this.messageTimeout) {
        clearTimeout(this.messageTimeout);
      }

      // 设置新的定时器，3秒后自动消失
      this.messageTimeout = setTimeout(() => {
        this.message = '';
      }, 3000);
    },

    // 获取播放器标题
    getPlayerTitle() {
      if (this.selectedVideo) {
        return this.formatVideoName(this.selectedVideo.filename);
      } else {
        return '视频回放系统';
      }
    },

    // 在视图模式切换时调整滚动位置
    watch: {
      viewMode(newMode, oldMode) {
        if (newMode !== oldMode) {
          // 在DOM更新后调整滚动位置
          this.$nextTick(() => {
            const container = document.querySelector('.video-list-container');
            if (container) {
              // 重置滚动位置到顶部
              container.scrollTop = 0;
            }
          });
        }
      }
    },

    // 修复滚动问题的专用方法
    fixScrolling() {
      // 等待DOM完全渲染
      setTimeout(() => {
        // 获取目标容器
        const sidebar = document.querySelector('.sidebar');
        const scrollContainer = document.querySelector('.sidebar-scroll-container');

        if (sidebar) {
          // 确保 sidebar 本身不滚动
          sidebar.style.overflow = 'hidden';
        }

        if (scrollContainer) {
          // 设置CSS属性确保滚动正常工作
          scrollContainer.style.overflow = 'auto'; // 明确设置滚动
          // scrollContainer.style.height = 'auto'; // flex: 1 应该足够
          // scrollContainer.style.maxHeight = 'calc(100vh - 180px)'; // CSS 中已有

          // 添加样式类以启用滚动 (如果 .scrollable 定义了滚动条样式)
          scrollContainer.classList.add('scrollable');

          // 移除旧监听器避免重复添加 (可选，但推荐)
          // 注意：这种方式移除匿名函数无效，需要更复杂的处理或确保只添加一次
          // scrollContainer.removeEventListener('wheel', ...);

          // 为容器注册事件处理函数，阻止页面滚动
          scrollContainer.addEventListener('wheel', function (e) {
            // 计算新的滚动位置
            const newScrollTop = this.scrollTop + e.deltaY;
            const maxScrollTop = this.scrollHeight - this.clientHeight;

            // 检查是否可以滚动
            const canScrollUp = e.deltaY < 0 && this.scrollTop > 0;
            const canScrollDown = e.deltaY > 0 && this.scrollTop < maxScrollTop;

            if (canScrollUp || canScrollDown) {
              // 如果可以在容器内滚动，阻止页面滚动
              e.preventDefault();
              // 手动设置滚动位置 (浏览器通常会处理，但显式设置无害)
              this.scrollTop = newScrollTop;
              // console.log(`容器滚动: ${this.className}, 位置: ${this.scrollTop}`);
            }
            // 如果已经到达边界，则允许页面滚动 (不调用 e.preventDefault())
          }, {passive: false});

          console.log('滚动处理程序已应用于 .sidebar-scroll-container');
        } else {
          console.log('.sidebar-scroll-container 未找到');
        }

        // 不再需要处理 video-list-container, video-grid, video-list 的滚动

      }, 1000);
    },

    confirmDelete(video) {
      if (confirm(`确定要删除 ${video.filename} 吗？`)) {
        this.deleteVideo(video);
      }
    },
    async deleteVideo(video) {
      try {
        const res = await fetch('http://localhost:4000/api/delete-video', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({filename: video.filename})
        });
        const data = await res.json();
        if (data.success) {
          this.showMessage('删除成功', 'success');
          this.getRecordings(); // 刷新列表
        } else {
          this.showMessage(data.error || '删除失败', 'error');
        }
      } catch (e) {
        this.showMessage('删除请求失败', 'error');
      }
    },
  }
}
</script>

<style>
/* 全局CSS变量 */
:root {
  --header-height: 60px;
  --sidebar-width: 320px;
  --primary-color: #4a6cf7;
  --primary-gradient: linear-gradient(135deg, #4a6cf7, #6c8eef);
  --secondary-color: #38d9a9;
  --accent-color: #f8526b;
  --background-color: #f7f9fc;
  --panel-bg: #ffffff;
  --text-color: #2d3748;
  --text-light: #718096;
  --border-color: #e2e8f0;
  --light-grey: #f1f5f9;
  --dark-grey: #94a3b8;
  --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  --hover-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  --button-shadow: 0 2px 5px rgba(74, 108, 247, 0.2);
  --border-radius: 10px;
  --card-border-radius: 12px;
  --transition-speed: 0.3s;
}

/* 全局样式重置 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* 添加全局滚动样式 */
.scrollable {
  overflow: auto !important;
  scrollbar-width: thin;
  scrollbar-color: var(--primary-color) var(--light-grey);
  -webkit-overflow-scrolling: touch;
}

.scrollable::-webkit-scrollbar {
  width: 6px;
}

.scrollable::-webkit-scrollbar-track {
  background: var(--light-grey);
  border-radius: 4px;
}

.scrollable::-webkit-scrollbar-thumb {
  background: var(--primary-gradient);
  border-radius: 4px;
}

body {
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', sans-serif;
  color: var(--text-color);
  background-color: var(--background-color);
  line-height: 1.6;
}
</style>

<style scoped>
/* 基本容器 */
.app-container {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--background-color);
}

/* 头部样式 */
.header {
  height: var(--header-height);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  background: var(--panel-bg);
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-section i {
  font-size: 26px;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header h1 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color);
  letter-spacing: 0.5px;
}

/* 主内容布局 */
.main-content {
  display: flex;
  flex: 1;
  height: calc(100vh - var(--header-height));
  overflow: hidden;
}

/* 侧边栏样式 */
.sidebar {
  width: var(--sidebar-width);
  background-color: var(--panel-bg);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  position: relative;
  transition: width var(--transition-speed) ease, transform var(--transition-speed) ease;
  height: 100%;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.03);
}

.sidebar.collapsed {
  width: var(--sidebar-width);
}

.recordings-browser {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

.sidebar-header {
  flex-shrink: 0;
  padding: 16px 16px 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.panel-header.with-controls {
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.panel-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
}

.controls {
  display: flex;
  gap: 8px;
}

.btn {
  background: var(--panel-bg);
  border: 1px solid var(--border-color);
  color: var(--text-light);
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 14px;
  transition: all var(--transition-speed) ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
  box-shadow: var(--button-shadow);
}

.btn.active {
  background: var(--primary-gradient);
  color: white;
  border-color: transparent;
}

.refresh-btn {
  width: 34px;
  height: 34px;
}

.refresh-btn i {
  transition: transform 0.6s ease;
}

.refresh-btn:hover i {
  transform: rotate(180deg);
}

.view-toggle {
  display: flex;
  background: var(--light-grey);
  border-radius: 6px;
  padding: 2px;
}

.view-toggle .btn {
  border: none;
  border-radius: 4px;
  width: 34px;
  height: 34px;
}

.filter-bar {
  margin-bottom: 15px;
}

.search-bar {
  display: flex;
  align-items: center;
  background: var(--light-grey);
  border-radius: 8px;
  padding: 8px 12px;
  transition: all var(--transition-speed) ease;
}

.search-bar:focus-within {
  box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.2);
}

.search-bar i {
  color: var(--text-light);
  margin-right: 8px;
}

.search-bar input {
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-color);
  width: 100%;
  outline: none;
}

.search-bar input::placeholder {
  color: var(--text-light);
}

/* 修正滚动容器样式 */
.sidebar-scroll-container {
  flex: 1;
  overflow-y: auto !important;
  max-height: calc(100vh - 180px);
  display: flex;
  flex-direction: column;
  position: relative;
  min-height: 0;
  background-color: var(--panel-bg);
  padding: 0 16px 16px;
}

/* 内容区域样式 */
.content-area {
  flex: 1;
  background-color: var(--background-color);
  overflow-y: auto;
  padding: 24px;
  transition: padding var(--transition-speed) ease;
}

.content-area.full-width {
  padding-left: 24px;
}

/* 视频列表容器 - 修复滚动问题 */
.video-list-container {
  flex: 1;
  min-height: 100%; /* 确保它能撑开父容器 */
  padding-bottom: 30px;
  border: 1px solid transparent;
}

/* 视频网格和列表视图 */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
  padding: 4px;
  margin-bottom: 50px;
}

.video-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 4px;
  margin-bottom: 50px;
}

/* 改进视频网格和列表视图 */
.video-card {
  background-color: white;
  border-radius: var(--card-border-radius);
  overflow: hidden;
  box-shadow: var(--card-shadow);
  cursor: pointer;
  transition: all var(--transition-speed) ease;
  position: relative;
  border: 2px solid transparent;
}

.video-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--hover-shadow);
}

.video-card.selected {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.2);
}

.thumbnail {
  position: relative;
  width: 100%;
  height: 0;
  padding-top: 56.25%; /* 16:9 宽高比 */
  overflow: hidden;
  background: #111;
}

.thumbnail img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-speed) ease;
}

.video-card:hover .thumbnail img {
  transform: scale(1.05);
}

.duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 3px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  backdrop-filter: blur(2px);
}

.video-info {
  padding: 12px;
}

.video-name {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 5px;
  color: var(--text-color);
}

.video-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-light);
}

/* 视频列表视图 */
.video-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: var(--card-border-radius);
  background-color: var(--panel-bg);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all var(--transition-speed) ease;
  box-shadow: var(--card-shadow);
}

.video-item:hover {
  box-shadow: var(--hover-shadow);
  transform: translateY(-2px);
  border-color: var(--primary-color);
}

.video-item.selected {
  border-color: var(--primary-color);
  background-color: rgba(74, 108, 247, 0.05);
}

.video-thumbnail {
  width: 90px;
  height: 50px;
  border-radius: 6px;
  overflow: hidden;
  margin-right: 14px;
  background-color: #111;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-speed) ease;
}

.video-item:hover .video-thumbnail img {
  transform: scale(1.05);
}

.video-details {
  flex: 1;
}

.video-time {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--text-light);
  margin-top: 3px;
}

.video-time i {
  font-size: 11px;
}

/* 录像回放界面 */
.playback-view {
  background-color: var(--panel-bg);
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--card-shadow);
  height: 100%;
}

.no-video-selected {
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: var(--border-radius);
  padding: 40px 20px;
  height: 500px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.no-video-selected i {
  font-size: 80px;
  background: linear-gradient(135deg, #ddd, #aaa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 30px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0);
  }
}

.no-video-selected p {
  font-size: 20px;
  color: var(--text-color);
  font-weight: 500;
  text-align: center;
  max-width: 300px;
  line-height: 1.5;
}

.no-recordings {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 0;
  color: var(--text-light);
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: var(--border-radius);
  margin: 10px 0;
  height: calc(100% - 20px);
}

.no-recordings i {
  font-size: 70px;
  margin-bottom: 25px;
  background: linear-gradient(135deg, #ddd, #aaa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  opacity: 0.8;
  animation: float 3s ease-in-out infinite;
}

.no-recordings p {
  font-size: 18px;
  color: var(--text-color);
  font-weight: 500;
}

/* 视频播放区域 - 改进布局 */
.video-player-container {
  border-radius: var(--border-radius);
  overflow: hidden;
}

.video-player {
  background-color: #0c0c0c;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  min-height: 400px;
  position: relative; /* 确保加载指示器相对于这个容器定位 */
}

.video-wrapper {
  width: 100%;
  max-width: 800px;
  height: 450px;
  position: relative;
  background-color: #000;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

/* Video.js自定义样式 */
.video-js {
  width: 100% !important;
  height: 100% !important;
  background-color: #000;
}

.vjs-tech {
  object-fit: contain !important; /* 确保视频内容不被裁剪 */
}

/* 加载状态 - 改为内联显示，不再全屏覆盖 */
.video-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: rgba(0, 0, 0, 0.7);
  border-radius: 12px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  color: white;
  width: 150px;
  height: 150px;
  backdrop-filter: blur(4px);
}

.video-loading p {
  margin-top: 15px;
  font-size: 14px;
  color: #fff;
  font-weight: 500;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 视频详情区域 */
.video-player-container .panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.video-player-container .panel-header h2 {
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: rgba(231, 76, 60, 0.1);
  color: var(--accent-color);
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--accent-color);
  color: white;
  box-shadow: 0 2px 6px rgba(231, 76, 60, 0.3);
}

.video-details {
  padding: 16px 20px;
  display: flex;
  gap: 20px;
  background: var(--light-grey);
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-color);
}

.detail-item i {
  color: var(--primary-color);
  font-size: 15px;
}

/* 消息提示 */
.message-toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 14px 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease;
  max-width: 320px;
  backdrop-filter: blur(8px);
}

@keyframes slideIn {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.message-toast.success {
  background-color: rgba(56, 217, 169, 0.95);
  color: white;
}

.message-toast.error {
  background-color: rgba(248, 82, 107, 0.95);
  color: white;
}

.message-toast.warning {
  background-color: rgba(249, 159, 30, 0.95);
  color: white;
}

.message-toast.info {
  background-color: rgba(74, 108, 247, 0.95);
  color: white;
}

.message-toast i {
  font-size: 18px;
}

/* 响应式调整，确保在不同屏幕尺寸下滚动正常 */
@media (max-width: 1200px) {
  .main-content {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    max-height: 320px;
  }

  .sidebar.collapsed {
    max-height: 40px;
    width: 100%;
  }

  .sidebar-scroll-container {
    height: calc(100% - 120px);
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }

  .content-area.full-width {
    padding-left: 24px;
    padding-top: 24px;
  }
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 20px;
    height: auto;
  }

  .logo-section {
    margin-bottom: 5px;
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
  }

  .content-area {
    padding: 16px;
  }

  .content-area.full-width {
    padding-left: 16px;
    padding-top: 16px;
  }

  .video-wrapper {
    height: 300px;
  }
}

.vjs-theme-forest {
  --vjs-theme-forest--primary: var(--primary-color);
}

/* 隐藏侧边栏切换按钮 */
.sidebar-toggle {
  display: none !important;
}

/* 删除按钮 */
.delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(248, 82, 107, 0.9);
  border: none;
  color: white;
  font-size: 14px;
  cursor: pointer;
  z-index: 5;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: scale(0);
  transition: all 0.25s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  opacity: 0.9;
}

.video-card:hover .delete-btn,
.video-item:hover .delete-btn {
  transform: scale(1);
}

.delete-btn:hover {
  background: var(--accent-color);
  opacity: 1;
  transform: scale(1.1);
}

.video-card, .video-item {
  position: relative;
}
</style> 