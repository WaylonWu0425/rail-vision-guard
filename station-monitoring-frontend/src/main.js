import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';  // 引入 Element Plus 的样式
import './assets/style/global.css'
import * as echarts from 'echarts';
import { formatDate } from './utils/dateFormatter';

const app = createApp(App);

app.use(router); // 使用路由
app.use(ElementPlus); // 使用 Element Plus
app.use(store);
app.use(echarts);
app.config.globalProperties.$formatDate = formatDate

app.mount('#app');
