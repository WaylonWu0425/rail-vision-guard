const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    client: {
      // Webpack Dev Server 默认使用 /ws，与摄像头状态业务 WebSocket
      // 的代理路径冲突。开发环境单独使用 /hmr-socket，避免连接被误转发。
      webSocketURL: {
        pathname: '/hmr-socket'
      },
      overlay: {
        errors: true,
        warnings: false,
        // Element Plus components may resize while a routed page is being
        // unmounted. Chromium reports the unfinished observer delivery as a
        // runtime warning even though the next frame completes normally.
        // Keep the overlay for genuine errors, but do not block the whole UI
        // for these two harmless ResizeObserver notifications.
        runtimeErrors: (error) => {
          const message = error && error.message ? error.message : String(error || '')
          return !(
            message.includes('ResizeObserver loop completed with undelivered notifications') ||
            message.includes('ResizeObserver loop limit exceeded')
          )
        }
      }
    },
    webSocketServer: {
      type: 'ws',
      options: {
        path: '/hmr-socket'
      }
    },
    // 路由使用 createWebHistory；刷新 /login、/imageDetection 等地址时
    // 必须回退到 index.html，再由 Vue Router 渲染对应页面。
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8081', // 本地 Java 后端地址
        changeOrigin: true,
        pathRewrite: { '^/api': '' } // 去掉 /api 前缀再转发给后端
      },
      '/detection': {
        target: 'http://127.0.0.1:5000', // 本地 YOLO 检测服务
        changeOrigin: true,
        pathRewrite: { '^/detection': '' },
        proxyTimeout: 0,
        timeout: 0
      },
      '/ws': {
        target: 'ws://127.0.0.1:8081',
        ws: true,
        changeOrigin: true
      }
    }
  }
})
