<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <keep-alive :include="['HomePage']" :max="10">
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
</template>

<style>
/* 全局样式 */
:root {
  --el-color-primary: #1976d2;
  --el-color-primary-dark-2: #125ca7;
  --primary-color: #1976d2;
  --primary-light: #42a5f5;
  --primary-dark: #1565c0;
  --secondary-color: #e3f2fd;
  --text-primary: #2c3e50;
  --text-secondary: #546e7a;
  --transition-speed: 0.3s;
}

html, body {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

#app {
  font-family: 'Noto Sans SC', 'Microsoft YaHei', 'PingFang SC', Arial, sans-serif;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 100%;
  background: linear-gradient(135deg, var(--secondary-color) 0%, #ffffff 100%);
  color: var(--text-primary);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:focus-visible {
  outline: 2px solid #1976d2;
  outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}


</style>
