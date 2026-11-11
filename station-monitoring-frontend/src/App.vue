<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <keep-alive :include="['HomePage']" :max="10">
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
</template>

<script setup>

const debounce = (fn, delay) => {
    let timer = null;
    return function () {
      let context = this;
      let args = arguments;
      clearTimeout(timer);
      timer = setTimeout(function () {
        fn.apply(context, args);
      }, delay);
    }
  }
   
  const _ResizeObserver = window.ResizeObserver;
  window.ResizeObserver = class ResizeObserver extends _ResizeObserver{
    constructor(callback) {
      callback = debounce(callback, 16);
      super(callback);
    }
  }


</script>

<style>
/* 全局样式 */
:root {
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
  font-family: 'Arial', sans-serif;
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


</style>
