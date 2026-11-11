let scheduled = false

// 登录后的空闲时间预取比赛演示最常用页面，避免用户第一次点击菜单时才下载页面代码。
export function preloadCorePages() {
  if (scheduled) return
  scheduled = true

  const preload = () => {
    void import(/* webpackPrefetch: true */ '@/views/MonitoringScreen.vue')
    void import(/* webpackPrefetch: true */ '@/views/ImageDetection.vue')
    void import(/* webpackPrefetch: true */ '@/views/Alarm.vue')
    void import(/* webpackPrefetch: true */ '@/views/video.vue')
    void import(/* webpackPrefetch: true */ '@/views/CameraManagement.vue')
  }

  if ('requestIdleCallback' in window) {
    window.requestIdleCallback(preload, { timeout: 2000 })
  } else {
    window.setTimeout(preload, 800)
  }
}
